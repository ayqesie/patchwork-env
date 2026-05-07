"""Tests for patchwork_env.stripper."""

import pytest
from patchwork_env.stripper import strip_env, StripResult


@pytest.fixture
def base_env() -> dict:
    return {
        "APP_NAME": "myapp",
        "APP_ENV": "production",
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "AWS_ACCESS_KEY": "AKIA123",
        "AWS_SECRET_KEY": "secret",
        "DEBUG": "false",
    }


def test_no_keys_no_patterns_returns_unchanged(base_env):
    result = strip_env(base_env)
    assert result.stripped == base_env
    assert result.removed_keys == []
    assert result.not_found == []


def test_exact_key_removed(base_env):
    result = strip_env(base_env, keys=["DEBUG"])
    assert "DEBUG" not in result.stripped
    assert "DEBUG" in result.removed_keys


def test_multiple_exact_keys_removed(base_env):
    result = strip_env(base_env, keys=["DB_HOST", "DB_PORT"])
    assert "DB_HOST" not in result.stripped
    assert "DB_PORT" not in result.stripped
    assert len(result.removed_keys) == 2


def test_missing_exact_key_goes_to_not_found(base_env):
    result = strip_env(base_env, keys=["NONEXISTENT"])
    assert "NONEXISTENT" in result.not_found
    assert result.removed_keys == []


def test_pattern_removes_matching_keys(base_env):
    result = strip_env(base_env, patterns=["AWS_*"])
    assert "AWS_ACCESS_KEY" not in result.stripped
    assert "AWS_SECRET_KEY" not in result.stripped
    assert "AWS_ACCESS_KEY" in result.removed_keys
    assert "AWS_SECRET_KEY" in result.removed_keys


def test_pattern_does_not_remove_non_matching(base_env):
    result = strip_env(base_env, patterns=["AWS_*"])
    assert "APP_NAME" in result.stripped
    assert "DB_HOST" in result.stripped


def test_combined_keys_and_patterns(base_env):
    result = strip_env(base_env, keys=["DEBUG"], patterns=["DB_*"])
    assert "DEBUG" not in result.stripped
    assert "DB_HOST" not in result.stripped
    assert "DB_PORT" not in result.stripped
    assert len(result.removed_keys) == 3


def test_has_changes_true_when_keys_removed(base_env):
    result = strip_env(base_env, keys=["DEBUG"])
    assert result.has_changes() is True


def test_has_changes_false_when_nothing_removed(base_env):
    result = strip_env(base_env)
    assert result.has_changes() is False


def test_original_env_not_mutated(base_env):
    original_copy = dict(base_env)
    strip_env(base_env, keys=["DEBUG"], patterns=["AWS_*"])
    assert base_env == original_copy


def test_summary_contains_counts(base_env):
    result = strip_env(base_env, keys=["DEBUG", "MISSING"], patterns=["AWS_*"])
    summary = result.summary()
    assert "Keys removed" in summary
    assert "Not found" in summary
    assert "Keys remaining" in summary


def test_summary_lists_removed_keys(base_env):
    result = strip_env(base_env, keys=["DEBUG"])
    assert "DEBUG" in result.summary()


def test_wildcard_star_matches_all(base_env):
    result = strip_env(base_env, patterns=["*"])
    assert result.stripped == {}
    assert len(result.removed_keys) == len(base_env)
