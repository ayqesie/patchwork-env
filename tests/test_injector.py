"""Tests for patchwork_env.injector."""

import pytest
from patchwork_env.injector import inject_env, InjectResult


@pytest.fixture
def base_env():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "dev"}


def test_new_key_injected(base_env):
    result = inject_env(base_env, {"NEW_KEY": "new_value"})
    assert "NEW_KEY" in result.injected
    assert result.final["NEW_KEY"] == "new_value"


def test_existing_key_skipped_by_default(base_env):
    result = inject_env(base_env, {"DB_HOST": "newhost"})
    assert "DB_HOST" in result.skipped
    assert result.final["DB_HOST"] == "localhost"


def test_existing_key_overwritten_when_flag_set(base_env):
    result = inject_env(base_env, {"DB_HOST": "newhost"}, overwrite=True)
    assert "DB_HOST" in result.overwritten
    assert result.overwritten["DB_HOST"] == ("localhost", "newhost")
    assert result.final["DB_HOST"] == "newhost"


def test_base_keys_preserved(base_env):
    result = inject_env(base_env, {"NEW_KEY": "val"})
    assert result.final["DB_PORT"] == "5432"
    assert result.final["APP_ENV"] == "dev"


def test_has_changes_true_when_injected(base_env):
    result = inject_env(base_env, {"FRESH": "yes"})
    assert result.has_changes() is True


def test_has_changes_false_when_all_skipped(base_env):
    result = inject_env(base_env, {"DB_HOST": "other"})
    assert result.has_changes() is False


def test_has_changes_true_when_overwritten(base_env):
    result = inject_env(base_env, {"DB_HOST": "other"}, overwrite=True)
    assert result.has_changes() is True


def test_summary_no_changes(base_env):
    result = inject_env(base_env, {"DB_HOST": "x"})
    assert result.summary() == "no changes"


def test_summary_with_injected(base_env):
    result = inject_env(base_env, {"NEW": "val"})
    assert "injected" in result.summary()


def test_summary_with_overwritten(base_env):
    result = inject_env(base_env, {"DB_HOST": "x"}, overwrite=True)
    assert "overwritten" in result.summary()


def test_summary_with_skipped(base_env):
    result = inject_env(base_env, {"DB_HOST": "x"})
    assert "skipped" in result.summary()


def test_multiple_new_keys(base_env):
    result = inject_env(base_env, {"A": "1", "B": "2", "C": "3"})
    assert len(result.injected) == 3
    assert result.final["A"] == "1"


def test_empty_pairs_no_changes(base_env):
    result = inject_env(base_env, {})
    assert result.has_changes() is False
    assert result.final == base_env


def test_base_not_mutated(base_env):
    original = dict(base_env)
    inject_env(base_env, {"DB_HOST": "mutated"}, overwrite=True)
    assert base_env == original
