"""Tests for patchwork_env.reconciler module."""

import pytest
from patchwork_env.differ import diff_envs
from patchwork_env.reconciler import reconcile, apply_patch, to_env_string


BASE = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true", "SECRET": "abc123"}
TARGET = {"HOST": "prod.example.com", "PORT": "5432", "WORKERS": "4"}


@pytest.fixture
def diff():
    return diff_envs(BASE, TARGET)


def test_merge_adds_missing_keys(diff):
    result = reconcile(BASE, TARGET, diff, strategy="merge")
    assert "DEBUG" in result
    assert "SECRET" in result


def test_merge_keeps_target_values_for_conflicts(diff):
    result = reconcile(BASE, TARGET, diff, strategy="merge")
    assert result["HOST"] == "prod.example.com"


def test_merge_keeps_target_only_keys(diff):
    result = reconcile(BASE, TARGET, diff, strategy="merge")
    assert "WORKERS" in result
    assert result["WORKERS"] == "4"


def test_overwrite_applies_base_values_for_changed(diff):
    result = reconcile(BASE, TARGET, diff, strategy="overwrite")
    assert result["HOST"] == "localhost"


def test_overwrite_adds_missing_keys(diff):
    result = reconcile(BASE, TARGET, diff, strategy="overwrite")
    assert result["DEBUG"] == "true"


def test_fill_missing_uses_fill_value(diff):
    result = reconcile(BASE, TARGET, diff, strategy="fill_missing", fill_value="CHANGEME")
    assert result["DEBUG"] == "CHANGEME"
    assert result["SECRET"] == "CHANGEME"


def test_fill_missing_does_not_overwrite_changed(diff):
    result = reconcile(BASE, TARGET, diff, strategy="fill_missing")
    assert result["HOST"] == "prod.example.com"


def test_invalid_strategy_raises(diff):
    with pytest.raises(ValueError, match="Unknown strategy"):
        reconcile(BASE, TARGET, diff, strategy="bad_strategy")


def test_apply_patch_sets_value():
    result = apply_patch({"A": "1"}, {"B": "2"})
    assert result == {"A": "1", "B": "2"}


def test_apply_patch_removes_none_keys():
    result = apply_patch({"A": "1", "B": "2"}, {"B": None})
    assert "B" not in result
    assert result["A"] == "1"


def test_apply_patch_updates_existing():
    result = apply_patch({"A": "old"}, {"A": "new"})
    assert result["A"] == "new"


def test_to_env_string_basic():
    env = {"FOO": "bar", "BAZ": "qux"}
    output = to_env_string(env)
    assert "BAZ=qux" in output
    assert "FOO=bar" in output


def test_to_env_string_quotes_values_with_spaces():
    env = {"MSG": "hello world"}
    output = to_env_string(env)
    assert 'MSG="hello world"' in output


def test_to_env_string_empty_value_quoted():
    env = {"EMPTY": ""}
    output = to_env_string(env)
    assert 'EMPTY=""' in output
