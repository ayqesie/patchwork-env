"""Tests for patchwork_env.env_sorter."""

import pytest
from patchwork_env.env_sorter import (
    sort_alphabetically,
    group_by_prefix,
    sort_env,
    _detect_prefixes,
    SortResult,
)


@pytest.fixture
def mixed_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "AWS_KEY": "abc",
        "AWS_SECRET": "xyz",
        "APP_DEBUG": "true",
        "APP_NAME": "myapp",
        "STANDALONE": "yes",
    }


def test_sort_alphabetically_orders_keys(mixed_env):
    result = sort_alphabetically(mixed_env)
    keys = list(result.keys())
    assert keys == sorted(keys)


def test_sort_alphabetically_preserves_values(mixed_env):
    result = sort_alphabetically(mixed_env)
    for k, v in mixed_env.items():
        assert result[k] == v


def test_detect_prefixes_finds_common(mixed_env):
    prefixes = _detect_prefixes(list(mixed_env.keys()))
    assert "DB_" in prefixes
    assert "AWS_" in prefixes
    assert "APP_" in prefixes


def test_detect_prefixes_excludes_singletons():
    keys = ["STANDALONE", "DB_HOST", "DB_PORT"]
    prefixes = _detect_prefixes(keys)
    assert "DB_" in prefixes
    assert "STANDALONE" not in prefixes


def test_group_by_prefix_explicit(mixed_env):
    result = group_by_prefix(mixed_env, prefixes=["DB_", "AWS_"])
    assert "DB_HOST" in result.groups["DB_"]
    assert "DB_PORT" in result.groups["DB_"]
    assert "AWS_KEY" in result.groups["AWS_"]
    assert "AWS_SECRET" in result.groups["AWS_"]


def test_group_by_prefix_ungrouped(mixed_env):
    result = group_by_prefix(mixed_env, prefixes=["DB_", "AWS_"])
    assert "STANDALONE" in result.ungrouped
    assert "APP_DEBUG" in result.ungrouped


def test_group_by_prefix_auto_detect(mixed_env):
    result = group_by_prefix(mixed_env)
    all_grouped = [k for keys in result.groups.values() for k in keys]
    assert "DB_HOST" in all_grouped
    assert "AWS_KEY" in all_grouped


def test_group_sorted_env_contains_all_keys(mixed_env):
    result = group_by_prefix(mixed_env)
    assert set(result.sorted_env.keys()) == set(mixed_env.keys())


def test_sort_env_alpha_mode(mixed_env):
    result = sort_env(mixed_env, mode="alpha")
    keys = list(result.sorted_env.keys())
    assert keys == sorted(keys)
    assert result.groups == {}


def test_sort_env_group_mode(mixed_env):
    result = sort_env(mixed_env, mode="group", prefixes=["DB_", "AWS_"])
    assert "DB_" in result.groups
    assert "AWS_" in result.groups


def test_summary_includes_total(mixed_env):
    result = sort_env(mixed_env, mode="alpha")
    s = result.summary()
    assert str(len(mixed_env)) in s


def test_summary_includes_groups(mixed_env):
    result = sort_env(mixed_env, mode="group", prefixes=["DB_", "AWS_"])
    s = result.summary()
    assert "DB_" in s
    assert "AWS_" in s
