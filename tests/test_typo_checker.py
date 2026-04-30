"""Tests for patchwork_env.typo_checker."""

import pytest
from patchwork_env.typo_checker import TypoResult, check_typos, check_typos_against_keys


@pytest.fixture
def reference():
    return {
        "DATABASE_URL": "postgres://",
        "SECRET_KEY": "abc123",
        "DEBUG": "true",
        "ALLOWED_HOSTS": "*",
    }


def test_exact_match_not_flagged(reference):
    env = {"DATABASE_URL": "mysql://"}
    result = check_typos(env, reference)
    assert not result.has_suggestions()


def test_close_match_flagged(reference):
    env = {"DATABSE_URL": "mysql://"}  # transposed letters
    result = check_typos(env, reference)
    assert "DATABSE_URL" in result.suggestions
    assert "DATABASE_URL" in result.suggestions["DATABSE_URL"]


def test_no_close_match_not_flagged(reference):
    env = {"COMPLETELY_DIFFERENT": "value"}
    result = check_typos(env, reference)
    assert not result.has_suggestions()


def test_multiple_typos_detected(reference):
    env = {
        "DATABSE_URL": "x",
        "SECERT_KEY": "y",
    }
    result = check_typos(env, reference)
    assert len(result.suggestions) == 2


def test_checked_count_reflects_env_size(reference):
    env = {"A": "1", "B": "2", "C": "3"}
    result = check_typos(env, reference)
    assert result.checked == 3


def test_reference_count_stored(reference):
    result = check_typos({}, reference)
    assert result.reference_count == len(reference)


def test_summary_no_issues(reference):
    result = check_typos({"DATABASE_URL": "x"}, reference)
    assert "No typos" in result.summary()


def test_summary_with_issues(reference):
    env = {"DATABSE_URL": "x"}
    result = check_typos(env, reference)
    assert "did you mean" in result.summary()
    assert "DATABSE_URL" in result.summary()


def test_all_suspect_keys(reference):
    env = {"DATABSE_URL": "x", "SECERT_KEY": "y"}
    result = check_typos(env, reference)
    suspects = result.all_suspect_keys()
    assert "DATABSE_URL" in suspects
    assert "SECERT_KEY" in suspects


def test_check_against_keys_wrapper():
    env = {"DATABSE_URL": "x"}
    result = check_typos_against_keys(env, ["DATABASE_URL", "SECRET_KEY"])
    assert "DATABSE_URL" in result.suggestions


def test_high_cutoff_misses_weak_match(reference):
    env = {"DB_URL": "x"}  # too short / different
    result = check_typos(env, reference, cutoff=0.95)
    assert "DB_URL" not in result.suggestions


def test_has_suggestions_false_when_clean(reference):
    result = check_typos({"DEBUG": "false"}, reference)
    assert result.has_suggestions() is False
