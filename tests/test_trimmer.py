"""Tests for patchwork_env.trimmer."""

import pytest
from patchwork_env.trimmer import trim_env, to_trimmed_string, TrimResult


@pytest.fixture
def mixed_env():
    return {
        "DB_HOST": "  localhost  ",
        "DB_PORT": "5432",
        "API_KEY": "  abc123",
        "CLEAN_KEY": "already_clean",
        "TRAILING": "value   ",
    }


def test_clean_env_has_no_changes():
    env = {"A": "hello", "B": "world"}
    result = trim_env(env)
    assert not result.has_changes()


def test_leading_whitespace_trimmed(mixed_env):
    result = trim_env(mixed_env)
    assert result.trimmed["API_KEY"] == "abc123"


def test_trailing_whitespace_trimmed(mixed_env):
    result = trim_env(mixed_env)
    assert result.trimmed["TRAILING"] == "value"


def test_both_sides_trimmed(mixed_env):
    result = trim_env(mixed_env)
    assert result.trimmed["DB_HOST"] == "localhost"


def test_clean_value_unchanged(mixed_env):
    result = trim_env(mixed_env)
    assert result.trimmed["DB_PORT"] == "5432"
    assert result.trimmed["CLEAN_KEY"] == "already_clean"


def test_changes_list_contains_dirty_keys(mixed_env):
    result = trim_env(mixed_env)
    changed_keys = [k for k, _, _ in result.changes]
    assert "DB_HOST" in changed_keys
    assert "API_KEY" in changed_keys
    assert "TRAILING" in changed_keys


def test_changes_list_excludes_clean_keys(mixed_env):
    result = trim_env(mixed_env)
    changed_keys = [k for k, _, _ in result.changes]
    assert "DB_PORT" not in changed_keys
    assert "CLEAN_KEY" not in changed_keys


def test_has_changes_true_when_dirty(mixed_env):
    result = trim_env(mixed_env)
    assert result.has_changes()


def test_original_preserved(mixed_env):
    result = trim_env(mixed_env)
    assert result.original["DB_HOST"] == "  localhost  "


def test_trim_keys_strips_key_whitespace():
    env = {"  SPACED_KEY  ": "value"}
    result = trim_env(env, trim_keys=True)
    assert "SPACED_KEY" in result.trimmed
    assert "  SPACED_KEY  " not in result.trimmed


def test_trim_keys_false_preserves_key_whitespace():
    env = {"  SPACED_KEY  ": "value"}
    result = trim_env(env, trim_keys=False)
    assert "  SPACED_KEY  " in result.trimmed


def test_summary_no_changes():
    result = trim_env({"A": "clean"})
    assert "No whitespace" in result.summary()


def test_summary_with_changes(mixed_env):
    result = trim_env(mixed_env)
    s = result.summary()
    assert "Trimmed" in s
    assert "DB_HOST" in s


def test_to_trimmed_string_basic():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = trim_env(env)
    output = to_trimmed_string(result)
    assert "HOST=localhost" in output
    assert "PORT=5432" in output


def test_to_trimmed_string_quotes_values_with_spaces():
    env = {"MSG": "hello world"}
    result = trim_env(env)
    output = to_trimmed_string(result)
    assert 'MSG="hello world"' in output
