"""Tests for patchwork_env.differ_extended."""

import pytest

from patchwork_env.differ import diff_envs
from patchwork_env.differ_extended import compute_diff_stats, _value_similarity


@pytest.fixture()
def base():
    return {
        "APP_HOST": "localhost",
        "APP_PORT": "8080",
        "DB_URL": "postgres://localhost/dev",
        "SECRET": "abc123",
    }


@pytest.fixture()
def target():
    return {
        "APP_HOST": "prod.example.com",
        "APP_PORT": "8080",
        "DB_URL": "postgres://prod-db/prod",
        "NEW_KEY": "hello",
    }


@pytest.fixture()
def diff(base, target):
    return diff_envs(base, target)


@pytest.fixture()
def stats(diff, base, target):
    return compute_diff_stats(diff, base, target)


def test_total_base_count(stats, base):
    assert stats.total_base == len(base)


def test_total_target_count(stats, target):
    assert stats.total_target == len(target)


def test_added_count(stats):
    assert stats.added == 1  # NEW_KEY


def test_removed_count(stats):
    assert stats.removed == 1  # SECRET


def test_changed_count(stats):
    assert stats.changed == 2  # APP_HOST, DB_URL


def test_unchanged_count(stats):
    assert stats.unchanged == 1  # APP_PORT


def test_overlap_ratio_between_zero_and_one(stats):
    assert 0.0 <= stats.overlap_ratio <= 1.0


def test_change_ratio_between_zero_and_one(stats):
    assert 0.0 <= stats.change_ratio <= 1.0


def test_summary_contains_labels(stats):
    s = stats.summary()
    assert "Base keys" in s
    assert "Overlap ratio" in s
    assert "Change ratio" in s


def test_similar_values_detected():
    base = {"KEY": "postgres://localhost/dev"}
    target = {"KEY": "postgres://localhost/prod"}
    diff = diff_envs(base, target)
    stats = compute_diff_stats(diff, base, target, similarity_threshold=0.7)
    assert any(k == "KEY" for k, _, _ in stats.similar_values)


def test_dissimilar_values_not_flagged():
    base = {"KEY": "aaa"}
    target = {"KEY": "zzz"}
    diff = diff_envs(base, target)
    stats = compute_diff_stats(diff, base, target, similarity_threshold=0.9)
    assert stats.similar_values == []


def test_value_similarity_identical():
    assert _value_similarity("hello", "hello") == 1.0


def test_value_similarity_empty_both():
    assert _value_similarity("", "") == 1.0


def test_value_similarity_one_empty():
    assert _value_similarity("abc", "") == 0.0


def test_overlap_ratio_no_shared_keys():
    base = {"A": "1"}
    target = {"B": "2"}
    diff = diff_envs(base, target)
    stats = compute_diff_stats(diff, base, target)
    assert stats.overlap_ratio == 0.0
