"""Tests for patchwork_env.renamer."""

import pytest
from patchwork_env.renamer import rename_keys, RenameResult


@pytest.fixture()
def base_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_SECRET": "hunter2",
        "LEGACY_FLAG": "true",
    }


def test_simple_rename(base_env):
    result = rename_keys(base_env, {"DB_HOST": "DATABASE_HOST"})
    assert "DATABASE_HOST" in result.env
    assert "DB_HOST" not in result.env
    assert result.env["DATABASE_HOST"] == "localhost"


def test_renamed_tracked(base_env):
    result = rename_keys(base_env, {"DB_PORT": "DATABASE_PORT"})
    assert ("DB_PORT", "DATABASE_PORT") in result.renamed


def test_missing_key_skipped(base_env):
    result = rename_keys(base_env, {"MISSING_KEY": "NEW_KEY"})
    assert "MISSING_KEY" in result.skipped
    assert "NEW_KEY" not in result.env


def test_conflict_prevents_overwrite(base_env):
    # DB_PORT already exists; renaming DB_HOST -> DB_PORT should conflict
    result = rename_keys(base_env, {"DB_HOST": "DB_PORT"})
    assert "DB_PORT" in result.conflicts
    assert result.env["DB_HOST"] == "localhost"  # original untouched


def test_conflict_overwrite_flag(base_env):
    result = rename_keys(base_env, {"DB_HOST": "DB_PORT"}, overwrite=True)
    assert result.env["DB_PORT"] == "localhost"
    assert "DB_HOST" not in result.env
    assert not result.conflicts


def test_multiple_renames(base_env):
    renames = {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"}
    result = rename_keys(base_env, renames)
    assert "DATABASE_HOST" in result.env
    assert "DATABASE_PORT" in result.env
    assert len(result.renamed) == 2


def test_original_env_not_mutated(base_env):
    original_copy = dict(base_env)
    rename_keys(base_env, {"DB_HOST": "DATABASE_HOST"})
    assert base_env == original_copy


def test_has_issues_false_on_clean(base_env):
    result = rename_keys(base_env, {"DB_HOST": "DATABASE_HOST"})
    assert not result.has_issues()


def test_has_issues_true_on_skip(base_env):
    result = rename_keys(base_env, {"NOPE": "SOMETHING"})
    assert result.has_issues()


def test_summary_clean(base_env):
    result = rename_keys(base_env, {"DB_HOST": "DATABASE_HOST"})
    assert "1 renamed" in result.summary()
    assert "not found" not in result.summary()


def test_summary_with_issues(base_env):
    result = rename_keys(base_env, {"NOPE": "SOMETHING", "DB_HOST": "DB_PORT"})
    summary = result.summary()
    assert "not found" in summary
    assert "conflicts" in summary
