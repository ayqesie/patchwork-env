import pytest
from patchwork_env.tagger import TagResult, tag_env, tag_by_prefix


@pytest.fixture()
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_NAME": "myapp",
        "SECRET_KEY": "abc123",
        "DEBUG": "true",
    }


# --- tag_env ---

def test_tagged_keys_present(sample_env):
    result = tag_env(sample_env, {"DB_HOST": ["database"], "DEBUG": ["flag"]})
    assert "DB_HOST" in result.tagged
    assert "DEBUG" in result.tagged


def test_untagged_keys_captured(sample_env):
    result = tag_env(sample_env, {"DB_HOST": ["database"]})
    assert "DB_PORT" in result.untagged
    assert "APP_NAME" in result.untagged


def test_tag_values_stored_correctly(sample_env):
    result = tag_env(sample_env, {"SECRET_KEY": ["secret", "sensitive"]})
    assert result.tagged["SECRET_KEY"] == ["secret", "sensitive"]


def test_extra_tag_map_keys_ignored(sample_env):
    result = tag_env(sample_env, {"NONEXISTENT": ["ghost"]})
    assert "NONEXISTENT" not in result.tagged
    assert len(result.untagged) == len(sample_env)


def test_has_tags_true_when_tagged(sample_env):
    result = tag_env(sample_env, {"DEBUG": ["flag"]})
    assert result.has_tags() is True


def test_has_tags_false_when_empty(sample_env):
    result = tag_env(sample_env, {})
    assert result.has_tags() is False


def test_keys_for_tag(sample_env):
    tag_map = {"DB_HOST": ["database"], "DB_PORT": ["database", "network"]}
    result = tag_env(sample_env, tag_map)
    db_keys = result.keys_for_tag("database")
    assert set(db_keys) == {"DB_HOST", "DB_PORT"}


def test_all_tags_returns_unique_set(sample_env):
    tag_map = {
        "DB_HOST": ["database"],
        "DB_PORT": ["database", "network"],
        "SECRET_KEY": ["sensitive"],
    }
    result = tag_env(sample_env, tag_map)
    assert result.all_tags() == {"database", "network", "sensitive"}


def test_summary_format(sample_env):
    result = tag_env(sample_env, {"DEBUG": ["flag"]})
    s = result.summary()
    assert "1 tagged" in s
    assert "4 untagged" in s


# --- tag_by_prefix ---

def test_prefix_tagging_matches_db_keys(sample_env):
    result = tag_by_prefix(sample_env, {"DB_": "database"})
    assert "DB_HOST" in result.tagged
    assert "DB_PORT" in result.tagged


def test_prefix_tagging_unmatched_are_untagged(sample_env):
    result = tag_by_prefix(sample_env, {"DB_": "database"})
    assert "APP_NAME" in result.untagged
    assert "DEBUG" in result.untagged


def test_multiple_prefix_matches_give_multiple_tags(sample_env):
    result = tag_by_prefix(sample_env, {"DB_": "database", "D": "starts-with-d"})
    # DB_HOST starts with both "DB_" and "D"
    assert "database" in result.tagged["DB_HOST"]
    assert "starts-with-d" in result.tagged["DB_HOST"]
