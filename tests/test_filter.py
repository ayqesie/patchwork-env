"""Tests for patchwork_env.filter."""

import pytest
from patchwork_env.filter import filter_env, FilterResult


@pytest.fixture
def sample_env():
    return {
        "APP_HOST": "localhost",
        "APP_PORT": "8080",
        "DB_HOST": "db.local",
        "DB_PASSWORD": "",
        "SECRET_KEY": "abc123",
        "DEBUG": "true",
    }


def test_no_filters_returns_all(sample_env):
    result = filter_env(sample_env)
    assert result.matched == sample_env
    assert result.excluded == {}


def test_prefix_filter(sample_env):
    result = filter_env(sample_env, prefix="APP_")
    assert "APP_HOST" in result.matched
    assert "APP_PORT" in result.matched
    assert "DB_HOST" not in result.matched


def test_include_pattern_wildcard(sample_env):
    result = filter_env(sample_env, include_patterns=["DB_*"])
    assert "DB_HOST" in result.matched
    assert "DB_PASSWORD" in result.matched
    assert "APP_HOST" in result.excluded


def test_exclude_pattern_wildcard(sample_env):
    result = filter_env(sample_env, exclude_patterns=["*PASSWORD*", "SECRET*"])
    assert "DB_PASSWORD" not in result.matched
    assert "SECRET_KEY" not in result.matched
    assert "APP_HOST" in result.matched


def test_value_pattern_regex(sample_env):
    result = filter_env(sample_env, value_pattern=r"\d+")
    assert "APP_PORT" in result.matched
    assert "APP_HOST" not in result.matched


def test_empty_only(sample_env):
    result = filter_env(sample_env, empty_only=True)
    assert result.matched == {"DB_PASSWORD": ""}


def test_nonempty_only(sample_env):
    result = filter_env(sample_env, nonempty_only=True)
    assert "DB_PASSWORD" not in result.matched
    assert "APP_HOST" in result.matched


def test_has_matches_true(sample_env):
    result = filter_env(sample_env, prefix="APP_")
    assert result.has_matches()


def test_has_matches_false(sample_env):
    result = filter_env(sample_env, prefix="NONEXISTENT_")
    assert not result.has_matches()


def test_summary_string(sample_env):
    result = filter_env(sample_env, prefix="APP_")
    s = result.summary()
    assert "matched" in s
    assert "excluded" in s


def test_combined_prefix_and_exclude(sample_env):
    result = filter_env(sample_env, prefix="DB_", exclude_patterns=["*PASSWORD*"])
    assert "DB_HOST" in result.matched
    assert "DB_PASSWORD" not in result.matched
