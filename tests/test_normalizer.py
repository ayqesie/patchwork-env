"""Tests for patchwork_env.normalizer."""

import pytest
from patchwork_env.normalizer import normalize_env, NormalizeResult


@pytest.fixture
def mixed_env():
    return {
        "db_host": "  localhost  ",
        "DB_PORT": "5432",
        "Api_Key": "'secret'",
        "debug": "true",
    }


def test_no_changes_when_already_normalized():
    env = {"DB_HOST": "localhost", "PORT": "8080"}
    result = normalize_env(env, key_case="upper", value_rules=["strip"])
    assert not result.has_changes()


def test_keys_uppercased(mixed_env):
    result = normalize_env(mixed_env, key_case="upper", value_rules=[])
    assert "DB_HOST" in result.normalized
    assert "API_KEY" in result.normalized
    assert "DEBUG" in result.normalized


def test_keys_lowercased(mixed_env):
    result = normalize_env(mixed_env, key_case="lower", value_rules=[])
    assert "db_host" in result.normalized
    assert "api_key" in result.normalized
    assert "db_port" in result.normalized


def test_keys_preserved_when_preserve(mixed_env):
    result = normalize_env(mixed_env, key_case="preserve", value_rules=[])
    assert "db_host" in result.normalized
    assert "DB_PORT" in result.normalized
    assert "Api_Key" in result.normalized


def test_strip_rule_removes_whitespace():
    env = {"HOST": "  localhost  "}
    result = normalize_env(env, key_case="preserve", value_rules=["strip"])
    assert result.normalized["HOST"] == "localhost"


def test_strip_quotes_removes_single_quotes():
    env = {"KEY": "'myvalue'"}
    result = normalize_env(env, key_case="preserve", value_rules=["strip_quotes"])
    assert result.normalized["KEY"] == "myvalue"


def test_strip_quotes_removes_double_quotes():
    env = {"KEY": '"myvalue"'}
    result = normalize_env(env, key_case="preserve", value_rules=["strip_quotes"])
    assert result.normalized["KEY"] == "myvalue"


def test_mismatched_quotes_not_stripped():
    env = {"KEY": "'myvalue\""}
    result = normalize_env(env, key_case="preserve", value_rules=["strip_quotes"])
    assert result.normalized["KEY"] == "'myvalue\""


def test_uppercase_value_rule():
    env = {"ENV": "production"}
    result = normalize_env(env, key_case="preserve", value_rules=["uppercase"])
    assert result.normalized["ENV"] == "PRODUCTION"


def test_lowercase_value_rule():
    env = {"ENV": "PRODUCTION"}
    result = normalize_env(env, key_case="preserve", value_rules=["lowercase"])
    assert result.normalized["ENV"] == "production"


def test_changes_recorded_for_key_case():
    env = {"db_host": "localhost"}
    result = normalize_env(env, key_case="upper", value_rules=[])
    assert result.has_changes()
    keys_changed = [c[0] for c in result.changes]
    assert "DB_HOST" in keys_changed


def test_summary_no_changes():
    env = {"HOST": "localhost"}
    result = normalize_env(env, key_case="upper", value_rules=["strip"])
    assert "No normalization" in result.summary()


def test_summary_with_changes():
    env = {"host": "  localhost  "}
    result = normalize_env(env, key_case="upper", value_rules=["strip"])
    assert "Normalized" in result.summary()
    assert "HOST" in result.summary()
