"""Tests for patchwork_env.differ"""

import pytest
from patchwork_env.differ import diff_envs, EnvDiff


LEFT = {
    "APP_ENV": "staging",
    "DEBUG": "true",
    "SECRET_KEY": "old-secret",
    "SHARED": "same",
}

RIGHT = {
    "APP_ENV": "production",
    "LOG_LEVEL": "warn",
    "SECRET_KEY": "new-secret",
    "SHARED": "same",
}


@pytest.fixture
def diff() -> EnvDiff:
    return diff_envs(LEFT, RIGHT)


def test_added_keys(diff: EnvDiff):
    assert "LOG_LEVEL" in diff.added
    assert diff.added["LOG_LEVEL"] == "warn"


def test_removed_keys(diff: EnvDiff):
    assert "DEBUG" in diff.removed
    assert diff.removed["DEBUG"] == "true"


def test_changed_keys(diff: EnvDiff):
    assert "APP_ENV" in diff.changed
    assert diff.changed["APP_ENV"] == ("staging", "production")
    assert "SECRET_KEY" in diff.changed


def test_unchanged_keys(diff: EnvDiff):
    assert "SHARED" in diff.unchanged
    assert diff.unchanged["SHARED"] == "same"


def test_has_diff_true(diff: EnvDiff):
    assert diff.has_diff is True


def test_has_diff_false():
    same = {"KEY": "val"}
    d = diff_envs(same, same)
    assert d.has_diff is False


def test_summary_contains_markers(diff: EnvDiff):
    summary = diff.summary()
    assert "+" in summary
    assert "-" in summary
    assert "~" in summary


def test_summary_no_diff():
    d = diff_envs({"A": "1"}, {"A": "1"})
    assert d.summary() == "(no differences)"


def test_empty_envs():
    d = diff_envs({}, {})
    assert not d.has_diff


def test_all_added():
    d = diff_envs({}, {"NEW": "val"})
    assert d.added == {"NEW": "val"}
    assert not d.removed
