"""Tests for patchwork_env.comparator."""

import pytest

from patchwork_env.comparator import compare_env_dicts, CompareResult


@pytest.fixture
def base():
    return {"HOST": "localhost", "PORT": "5432", "DEBUG": "true", "SECRET": "abc"}


@pytest.fixture
def target():
    return {"HOST": "prod.example.com", "PORT": "5432", "WORKERS": "4", "SECRET": "xyz"}


@pytest.fixture
def result(base, target) -> CompareResult:
    return compare_env_dicts(base, target)


def test_shared_keys_identified(result):
    assert result.shared_keys == {"HOST", "PORT", "SECRET"}


def test_base_only_keys(result):
    assert result.base_only_keys == {"DEBUG"}


def test_target_only_keys(result):
    assert result.target_only_keys == {"WORKERS"}


def test_matching_pairs_same_value(result):
    assert "PORT" in result.matching_pairs
    assert result.matching_pairs["PORT"] == "5432"


def test_differing_pairs_captures_both_values(result):
    assert "HOST" in result.differing_pairs
    base_val, target_val = result.differing_pairs["HOST"]
    assert base_val == "localhost"
    assert target_val == "prod.example.com"


def test_differing_pairs_secret(result):
    assert "SECRET" in result.differing_pairs


def test_has_diff_when_differences_exist(result):
    assert result.has_diff() is True


def test_no_diff_for_identical_envs():
    env = {"A": "1", "B": "2"}
    r = compare_env_dicts(env, env.copy())
    assert r.has_diff() is False


def test_similarity_score_perfect():
    env = {"A": "1"}
    r = compare_env_dicts(env, env.copy())
    assert r.similarity_score == 1.0


def test_similarity_score_zero():
    r = compare_env_dicts({"A": "1"}, {"B": "2"})
    assert r.similarity_score == 0.0


def test_similarity_score_partial(result):
    # 1 matching (PORT) out of 5 total unique keys
    assert 0.0 < result.similarity_score < 1.0


def test_summary_contains_similarity(result):
    s = result.summary()
    assert "Similarity" in s
    assert "%" in s


def test_summary_contains_counts(result):
    s = result.summary()
    assert "Matching" in s
    assert "Differing" in s


def test_empty_envs_similarity_is_one():
    r = compare_env_dicts({}, {})
    assert r.similarity_score == 1.0
    assert r.has_diff() is False


def test_custom_paths_stored():
    r = compare_env_dicts({}, {}, base_path=".env.base", target_path=".env.prod")
    assert r.base_path == ".env.base"
    assert r.target_path == ".env.prod"


def test_matching_pairs_does_not_contain_differing_keys(result):
    """Keys with different values should not appear in matching_pairs."""
    for key in result.differing_pairs:
        assert key not in result.matching_pairs


def test_differing_pairs_does_not_contain_matching_keys(result):
    """Keys with identical values should not appear in differing_pairs."""
    for key in result.matching_pairs:
        assert key not in result.differing_pairs


def test_base_only_keys_not_in_shared(result):
    """Keys exclusive to base should not appear in shared_keys."""
    assert result.base_only_keys.isdisjoint(result.shared_keys)


def test_target_only_keys_not_in_shared(result):
    """Keys exclusive to target should not appear in shared_keys."""
    assert result.target_only_keys.isdisjoint(result.shared_keys)
