import pytest
from patchwork_env.splitter import split_env, _detect_prefixes, to_env_string, SplitResult


@pytest.fixture
def mixed_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "mydb",
        "AWS_KEY": "AKIAIOSFODNN7",
        "AWS_SECRET": "wJalrXUtnFEMI",
        "APP_NAME": "patchwork",
        "APP_ENV": "production",
        "STANDALONE": "value",
    }


def test_detect_prefixes_finds_db(mixed_env):
    prefixes = _detect_prefixes(mixed_env)
    assert "DB" in prefixes


def test_detect_prefixes_finds_aws(mixed_env):
    prefixes = _detect_prefixes(mixed_env)
    assert "AWS" in prefixes


def test_detect_prefixes_finds_app(mixed_env):
    prefixes = _detect_prefixes(mixed_env)
    assert "APP" in prefixes


def test_detect_prefixes_excludes_singletons():
    env = {"ONLY_ONE": "val", "OTHER": "val2"}
    prefixes = _detect_prefixes(env)
    assert "ONLY" not in prefixes


def test_split_groups_db_keys(mixed_env):
    result = split_env(mixed_env, prefixes=["DB"])
    assert "DB" in result.groups
    assert "DB_HOST" in result.groups["DB"]
    assert "DB_PORT" in result.groups["DB"]


def test_split_groups_aws_keys(mixed_env):
    result = split_env(mixed_env, prefixes=["AWS"])
    assert "AWS" in result.groups
    assert len(result.groups["AWS"]) == 2


def test_split_ungrouped_contains_standalone(mixed_env):
    result = split_env(mixed_env, prefixes=["DB", "AWS", "APP"])
    assert "STANDALONE" in result.ungrouped


def test_split_strip_prefix_removes_prefix(mixed_env):
    result = split_env(mixed_env, prefixes=["DB"], strip_prefix=True)
    assert "HOST" in result.groups["DB"]
    assert "PORT" in result.groups["DB"]
    assert "DB_HOST" not in result.groups["DB"]


def test_split_auto_detects_prefixes(mixed_env):
    result = split_env(mixed_env)
    assert result.has_groups()
    assert "DB" in result.groups


def test_source_key_count(mixed_env):
    result = split_env(mixed_env, prefixes=["DB"])
    assert result.source_key_count == len(mixed_env)


def test_has_groups_false_when_no_match():
    env = {"STANDALONE": "val"}
    result = split_env(env, prefixes=["DB"])
    assert not result.has_groups()


def test_summary_contains_group_name(mixed_env):
    result = split_env(mixed_env, prefixes=["DB", "AWS"])
    s = result.summary()
    assert "DB" in s
    assert "AWS" in s


def test_to_env_string_format():
    env = {"KEY": "value", "OTHER": "123"}
    s = to_env_string(env)
    assert "KEY=value" in s
    assert "OTHER=123" in s


def test_all_keys_accounted_for(mixed_env):
    result = split_env(mixed_env, prefixes=["DB", "AWS", "APP"])
    total = sum(len(v) for v in result.groups.values()) + len(result.ungrouped)
    assert total == len(mixed_env)
