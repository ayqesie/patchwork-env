import pytest
from patchwork_env.promoter import promote_env, PromoteResult


@pytest.fixture
def source():
    return {
        "DB_HOST": "prod-db.example.com",
        "DB_PORT": "5432",
        "API_KEY": "prod-secret",
        "APP_DEBUG": "false",
    }


@pytest.fixture
def target():
    return {
        "DB_HOST": "staging-db.example.com",
        "DB_PORT": "5432",
        "APP_DEBUG": "true",
        "LOG_LEVEL": "debug",
    }


def test_promote_new_key_added(source, target):
    result = promote_env(source, target)
    assert "API_KEY" in result.promoted


def test_promote_existing_key_skipped_by_default(source, target):
    result = promote_env(source, target)
    assert "DB_HOST" in result.skipped


def test_promote_overwrite_replaces_value(source, target):
    result = promote_env(source, target, overwrite=True)
    assert "DB_HOST" in result.overwritten
    old, new = result.overwritten["DB_HOST"]
    assert old == "staging-db.example.com"
    assert new == "prod-db.example.com"


def test_promote_explicit_keys_only(source, target):
    result = promote_env(source, target, keys=["API_KEY"])
    assert "API_KEY" in result.promoted
    assert "DB_HOST" not in result.promoted
    assert "DB_HOST" not in result.skipped


def test_promote_missing_explicit_key_goes_to_not_found(source, target):
    result = promote_env(source, target, keys=["MISSING_KEY"])
    assert "MISSING_KEY" in result.not_found


def test_promote_prefix_filter(source, target):
    result = promote_env(source, target, prefix="DB_")
    for key in result.promoted:
        assert key.startswith("DB_")
    for key in result.skipped:
        assert key.startswith("DB_")
    assert "API_KEY" not in result.promoted
    assert "API_KEY" not in result.skipped


def test_promote_has_changes_when_keys_promoted(source, target):
    result = promote_env(source, target)
    assert result.has_changes()


def test_promote_no_changes_when_all_skipped(source, target):
    # Only promote keys already in target without overwrite
    result = promote_env(source, target, keys=["DB_HOST", "DB_PORT", "APP_DEBUG"])
    assert not result.has_changes()


def test_promote_summary_contains_counts(source, target):
    result = promote_env(source, target)
    s = result.summary()
    assert "Promoted" in s
    assert "Skipped" in s
    assert "Not found" in s


def test_promote_target_only_key_preserved(source, target):
    result = promote_env(source, target)
    # LOG_LEVEL is only in target; it should not appear in not_found
    assert "LOG_LEVEL" not in result.not_found
