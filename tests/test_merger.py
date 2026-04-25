"""Tests for patchwork_env.merger."""

import pytest

from patchwork_env.merger import MergeResult, merge_env_dicts, merge_env_files


# ---------------------------------------------------------------------------
# merge_env_dicts helpers
# ---------------------------------------------------------------------------

A = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
B = {"PORT": "6543", "SECRET": "abc123"}
C = {"SECRET": "override", "NEW_KEY": "hello"}


def test_merge_two_dicts_last_wins():
    result = merge_env_dicts([A, B])
    assert result.merged["PORT"] == "6543"
    assert result.merged["HOST"] == "localhost"
    assert result.merged["SECRET"] == "abc123"


def test_merge_three_dicts_last_wins():
    result = merge_env_dicts([A, B, C])
    assert result.merged["SECRET"] == "override"
    assert result.merged["NEW_KEY"] == "hello"


def test_merge_all_keys_present():
    result = merge_env_dicts([A, B, C])
    assert set(result.merged.keys()) == {"HOST", "PORT", "DEBUG", "SECRET", "NEW_KEY"}


def test_no_conflicts_when_no_overlap():
    d1 = {"A": "1"}
    d2 = {"B": "2"}
    result = merge_env_dicts([d1, d2])
    assert not result.has_conflicts()


def test_conflict_recorded_for_overlapping_key():
    result = merge_env_dicts([A, B], labels=["base", "prod"])
    assert "PORT" in result.conflicts


def test_conflict_history_has_both_values():
    result = merge_env_dicts([A, B], labels=["base", "prod"])
    history = result.conflicts["PORT"]
    values = [v for v, _ in history]
    assert "5432" in values
    assert "6543" in values


def test_provenance_tracks_winning_source():
    result = merge_env_dicts([A, B], labels=["base", "prod"])
    _, src = result.provenance["PORT"]
    assert src == "prod"


def test_labels_mismatch_raises():
    with pytest.raises(ValueError):
        merge_env_dicts([A, B], labels=["only_one"])


def test_empty_list_returns_empty_result():
    result = merge_env_dicts([])
    assert result.merged == {}
    assert not result.has_conflicts()


def test_single_dict_no_conflicts():
    result = merge_env_dicts([A])
    assert result.merged == A
    assert not result.has_conflicts()


# ---------------------------------------------------------------------------
# summary
# ---------------------------------------------------------------------------

def test_summary_no_conflicts():
    result = merge_env_dicts([A])
    summary = result.summary()
    assert "Merged keys" in summary
    assert "Conflicts" not in summary


def test_summary_shows_conflict_key():
    result = merge_env_dicts([A, B], labels=["base", "prod"])
    summary = result.summary()
    assert "PORT" in summary


# ---------------------------------------------------------------------------
# merge_env_files (filesystem integration)
# ---------------------------------------------------------------------------

def test_merge_env_files(tmp_path):
    f1 = tmp_path / "base.env"
    f2 = tmp_path / "prod.env"
    f1.write_text("HOST=localhost\nPORT=5432\n")
    f2.write_text("PORT=6543\nSECRET=xyz\n")

    result = merge_env_files([str(f1), str(f2)])
    assert result.merged["PORT"] == "6543"
    assert result.merged["HOST"] == "localhost"
    assert result.merged["SECRET"] == "xyz"
    assert "PORT" in result.conflicts
