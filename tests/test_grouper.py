"""Tests for patchwork_env.grouper."""

import pytest
from patchwork_env.grouper import GroupResult, group_by_prefix, group_by_pattern


@pytest.fixture()
def mixed_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "mydb",
        "AWS_ACCESS_KEY": "AKIA...",
        "AWS_SECRET_KEY": "secret",
        "APP_DEBUG": "true",
        "APP_ENV": "production",
        "STANDALONE": "alone",
    }


# --- group_by_prefix ---

def test_prefix_groups_db_keys(mixed_env):
    result = group_by_prefix(mixed_env)
    assert "DB" in result.groups
    assert set(result.groups["DB"]) == {"DB_HOST", "DB_PORT", "DB_NAME"}


def test_prefix_groups_aws_keys(mixed_env):
    result = group_by_prefix(mixed_env)
    assert "AWS" in result.groups
    assert set(result.groups["AWS"]) == {"AWS_ACCESS_KEY", "AWS_SECRET_KEY"}


def test_prefix_singleton_goes_to_ungrouped(mixed_env):
    result = group_by_prefix(mixed_env)
    assert "STANDALONE" in result.ungrouped


def test_prefix_explicit_list_limits_groups(mixed_env):
    result = group_by_prefix(mixed_env, prefixes=["DB"])
    assert "DB" in result.groups
    assert "AWS" not in result.groups
    assert "AWS_ACCESS_KEY" in result.ungrouped


def test_has_groups_true_when_groups_exist(mixed_env):
    result = group_by_prefix(mixed_env)
    assert result.has_groups()


def test_has_groups_false_for_empty():
    result = group_by_prefix({})
    assert not result.has_groups()


def test_all_groups_sorted(mixed_env):
    result = group_by_prefix(mixed_env)
    labels = result.all_groups()
    assert labels == sorted(labels)


def test_summary_contains_group_label(mixed_env):
    result = group_by_prefix(mixed_env)
    s = result.summary()
    assert "[DB]" in s
    assert "[AWS]" in s


def test_summary_contains_ungrouped(mixed_env):
    result = group_by_prefix(mixed_env)
    assert "[ungrouped]" in result.summary()


def test_empty_env_summary_message():
    result = group_by_prefix({})
    assert result.summary() == "No groups found."


# --- group_by_pattern ---

def test_pattern_matches_db_keys(mixed_env):
    result = group_by_pattern(mixed_env, {"database": r"^DB_", "cloud": r"^AWS_"})
    assert set(result.groups["database"]) == {"DB_HOST", "DB_PORT", "DB_NAME"}


def test_pattern_first_match_wins(mixed_env):
    # DB_HOST matches both patterns; first one should win
    result = group_by_pattern(mixed_env, {"first": r"^DB_HOST", "second": r"^DB_"})
    assert "DB_HOST" in result.groups["first"]
    assert "DB_HOST" not in result.groups.get("second", [])


def test_pattern_unmatched_goes_to_ungrouped(mixed_env):
    result = group_by_pattern(mixed_env, {"db": r"^DB_"})
    assert "STANDALONE" in result.ungrouped
    assert "AWS_ACCESS_KEY" in result.ungrouped


def test_pattern_empty_patterns_all_ungrouped(mixed_env):
    result = group_by_pattern(mixed_env, {})
    assert not result.has_groups()
    assert len(result.ungrouped) == len(mixed_env)
