import pytest
from patchwork_env.transformer import transform_env, TransformResult, _apply_rule


@pytest.fixture
def base_env():
    return {
        "APP_NAME": "myapp",
        "DB_HOST": "localhost",
        "SECRET_KEY": "abc123",
        "PORT": "8080",
    }


def test_upper_rule(base_env):
    result = transform_env(base_env, [{"rule": "upper"}], keys=["APP_NAME"])
    assert result.transformed["APP_NAME"] == "MYAPP"


def test_lower_rule(base_env):
    result = transform_env(base_env, [{"rule": "lower"}], keys=["DB_HOST"])
    assert result.transformed["DB_HOST"] == "localhost"


def test_prefix_rule(base_env):
    result = transform_env(base_env, [{"rule": "prefix", "arg": "prod_"}], keys=["APP_NAME"])
    assert result.transformed["APP_NAME"] == "prod_myapp"


def test_suffix_rule(base_env):
    result = transform_env(base_env, [{"rule": "suffix", "arg": "_v2"}], keys=["APP_NAME"])
    assert result.transformed["APP_NAME"] == "myapp_v2"


def test_strip_rule():
    env = {"KEY": "  value  "}
    result = transform_env(env, [{"rule": "strip"}])
    assert result.transformed["KEY"] == "value"


def test_replace_rule(base_env):
    result = transform_env(base_env, [{"rule": "replace", "arg": "localhost,db.prod.internal"}], keys=["DB_HOST"])
    assert result.transformed["DB_HOST"] == "db.prod.internal"


def test_chained_rules(base_env):
    rules = [{"rule": "prefix", "arg": "env_"}, {"rule": "upper"}]
    result = transform_env(base_env, rules, keys=["APP_NAME"])
    assert result.transformed["APP_NAME"] == "ENV_MYAPP"


def test_no_keys_transforms_all(base_env):
    result = transform_env(base_env, [{"rule": "upper"}])
    for key in base_env:
        assert result.transformed[key] == base_env[key].upper()


def test_keys_filter_limits_scope(base_env):
    result = transform_env(base_env, [{"rule": "upper"}], keys=["APP_NAME"])
    assert result.transformed["DB_HOST"] == base_env["DB_HOST"]


def test_missing_key_skipped(base_env):
    result = transform_env(base_env, [{"rule": "upper"}], keys=["NONEXISTENT"])
    assert result.transformed == base_env


def test_has_changes_true(base_env):
    result = transform_env(base_env, [{"rule": "upper"}], keys=["APP_NAME"])
    assert result.has_changes()


def test_has_changes_false_when_no_effect():
    env = {"KEY": "VALUE"}
    result = transform_env(env, [{"rule": "upper"}])
    assert not result.has_changes()


def test_applied_tracks_changed_keys(base_env):
    result = transform_env(base_env, [{"rule": "upper"}], keys=["APP_NAME", "DB_HOST"])
    assert "APP_NAME" in result.applied


def test_summary_with_changes(base_env):
    result = transform_env(base_env, [{"rule": "upper"}], keys=["APP_NAME"])
    assert "1 transformation(s) applied" in result.summary()


def test_summary_no_changes():
    env = {"KEY": "VALUE"}
    result = transform_env(env, [{"rule": "upper"}])
    assert result.summary() == "no transformations applied"


def test_apply_rule_unknown_returns_unchanged():
    assert _apply_rule("hello", "unknown_rule") == "hello"
