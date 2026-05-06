"""Tests for patchwork_env.deprecator."""

import pytest
from patchwork_env.deprecator import deprecate_env, DeprecateResult


@pytest.fixture
def deprecation_map():
    return {
        "OLD_DB_HOST": "DB_HOST",
        "LEGACY_SECRET": "APP_SECRET",
        "DEPRECATED_FLAG": None,
    }


@pytest.fixture
def mixed_env():
    return {
        "OLD_DB_HOST": "localhost",
        "DB_PORT": "5432",
        "LEGACY_SECRET": "hunter2",
        "APP_NAME": "myapp",
        "DEPRECATED_FLAG": "true",
    }


def test_clean_env_has_no_issues(deprecation_map):
    env = {"DB_HOST": "localhost", "APP_NAME": "myapp"}
    result = deprecate_env(env, deprecation_map)
    assert not result.has_issues()


def test_deprecated_key_detected(mixed_env, deprecation_map):
    result = deprecate_env(mixed_env, deprecation_map)
    assert "OLD_DB_HOST" in result.deprecated


def test_multiple_deprecated_keys_detected(mixed_env, deprecation_map):
    result = deprecate_env(mixed_env, deprecation_map)
    assert len(result.deprecated) == 3


def test_replacement_recorded(mixed_env, deprecation_map):
    result = deprecate_env(mixed_env, deprecation_map)
    assert result.deprecated["OLD_DB_HOST"] == "DB_HOST"
    assert result.deprecated["LEGACY_SECRET"] == "APP_SECRET"


def test_no_replacement_is_none(mixed_env, deprecation_map):
    result = deprecate_env(mixed_env, deprecation_map)
    assert result.deprecated["DEPRECATED_FLAG"] is None


def test_clean_keys_not_in_deprecated(mixed_env, deprecation_map):
    result = deprecate_env(mixed_env, deprecation_map)
    assert "DB_PORT" in result.clean
    assert "APP_NAME" in result.clean


def test_has_issues_true_when_deprecated(mixed_env, deprecation_map):
    result = deprecate_env(mixed_env, deprecation_map)
    assert result.has_issues()


def test_all_deprecated_keys_list(mixed_env, deprecation_map):
    result = deprecate_env(mixed_env, deprecation_map)
    keys = result.all_deprecated_keys()
    assert set(keys) == {"OLD_DB_HOST", "LEGACY_SECRET", "DEPRECATED_FLAG"}


def test_summary_mentions_replacement(mixed_env, deprecation_map):
    result = deprecate_env(mixed_env, deprecation_map)
    s = result.summary()
    assert "DB_HOST" in s
    assert "APP_SECRET" in s


def test_summary_no_replacement_label(mixed_env, deprecation_map):
    result = deprecate_env(mixed_env, deprecation_map)
    s = result.summary()
    assert "no replacement" in s


def test_summary_clean_env():
    result = DeprecateResult()
    assert "No deprecated" in result.summary()


def test_empty_env_no_issues(deprecation_map):
    result = deprecate_env({}, deprecation_map)
    assert not result.has_issues()
    assert result.clean == []
