"""Tests for patchwork_env.deduplicator."""

import pytest
from patchwork_env.deduplicator import (
    DeduplicateResult,
    find_duplicate_values,
    deduplicate_env,
)


@pytest.fixture
def mixed_env():
    return {
        "DB_HOST": "localhost",
        "CACHE_HOST": "localhost",   # duplicate of DB_HOST
        "SECRET": "abc123",
        "TOKEN": "abc123",           # duplicate of SECRET
        "PORT": "8080",
        "EMPTY_A": "",
        "EMPTY_B": "",              # empty duplicate (ignored by default)
    }


def test_no_duplicates_clean():
    env = {"A": "1", "B": "2", "C": "3"}
    result = deduplicate_env(env)
    assert not result.has_issues()
    assert result.env == env


def test_duplicate_value_detected(mixed_env):
    dupes = find_duplicate_values(mixed_env)
    assert "localhost" in dupes
    assert "abc123" in dupes


def test_empty_values_ignored_by_default(mixed_env):
    dupes = find_duplicate_values(mixed_env, ignore_empty=True)
    assert "" not in dupes


def test_empty_values_included_when_flag_false(mixed_env):
    dupes = find_duplicate_values(mixed_env, ignore_empty=False)
    assert "" in dupes
    assert set(dupes[""]) == {"EMPTY_A", "EMPTY_B"}


def test_keep_first_removes_later_key(mixed_env):
    result = deduplicate_env(mixed_env, strategy="keep_first")
    # DB_HOST comes before CACHE_HOST in insertion order
    assert "DB_HOST" in result.env
    assert "CACHE_HOST" not in result.env


def test_keep_last_removes_earlier_key(mixed_env):
    result = deduplicate_env(mixed_env, strategy="keep_last")
    assert "CACHE_HOST" in result.env
    assert "DB_HOST" not in result.env


def test_removed_list_populated(mixed_env):
    result = deduplicate_env(mixed_env, strategy="keep_first")
    assert "CACHE_HOST" in result.removed
    assert "TOKEN" in result.removed


def test_kept_list_populated(mixed_env):
    result = deduplicate_env(mixed_env, strategy="keep_first")
    assert "DB_HOST" in result.kept
    assert "SECRET" in result.kept


def test_has_issues_true_when_duplicates(mixed_env):
    result = deduplicate_env(mixed_env)
    assert result.has_issues()


def test_has_issues_false_when_clean():
    result = deduplicate_env({"X": "1", "Y": "2"})
    assert not result.has_issues()


def test_summary_no_issues():
    result = deduplicate_env({"A": "hello", "B": "world"})
    assert "No duplicate" in result.summary()


def test_summary_reports_duplicate_count(mixed_env):
    result = deduplicate_env(mixed_env)
    assert "2 duplicate" in result.summary()


def test_invalid_strategy_raises():
    with pytest.raises(ValueError, match="Unknown strategy"):
        deduplicate_env({"A": "1"}, strategy="random")


def test_unique_values_preserved(mixed_env):
    result = deduplicate_env(mixed_env, strategy="keep_first")
    assert result.env["PORT"] == "8080"
