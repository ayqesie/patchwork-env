"""Tests for patchwork_env.aliaser."""
import pytest
from patchwork_env.aliaser import alias_env, invert_aliases, AliasResult


@pytest.fixture()
def base_env():
    return {
        "DATABASE_URL": "postgres://localhost/mydb",
        "SECRET_KEY": "s3cr3t",
        "DEBUG": "true",
        "PORT": "8080",
    }


@pytest.fixture()
def alias_map():
    return {
        "db_url": "DATABASE_URL",
        "secret": "SECRET_KEY",
        "debug_mode": "DEBUG",
    }


def test_resolved_keys_present(base_env, alias_map):
    result = alias_env(base_env, alias_map)
    assert "db_url" in result.resolved
    assert "secret" in result.resolved
    assert "debug_mode" in result.resolved


def test_resolved_values_match_source(base_env, alias_map):
    result = alias_env(base_env, alias_map)
    assert result.resolved["db_url"] == "postgres://localhost/mydb"
    assert result.resolved["secret"] == "s3cr3t"


def test_missing_canonical_key_goes_to_not_found(base_env):
    result = alias_env(base_env, {"app_port": "MISSING_KEY"})
    assert "app_port" in result.not_found
    assert "app_port" not in result.resolved


def test_has_issues_when_not_found(base_env):
    result = alias_env(base_env, {"ghost": "GHOST_KEY"})
    assert result.has_issues() is True


def test_no_issues_when_all_resolved(base_env, alias_map):
    result = alias_env(base_env, alias_map)
    assert result.has_issues() is False


def test_include_originals_keeps_source_keys(base_env, alias_map):
    result = alias_env(base_env, alias_map, include_originals=True)
    assert "DATABASE_URL" in result.resolved
    assert "PORT" in result.resolved


def test_include_originals_false_excludes_source_keys(base_env, alias_map):
    result = alias_env(base_env, alias_map, include_originals=False)
    assert "DATABASE_URL" not in result.resolved
    assert "PORT" not in result.resolved


def test_canonical_for_returns_correct_key(base_env, alias_map):
    result = alias_env(base_env, alias_map)
    assert result.canonical_for("db_url") == "DATABASE_URL"


def test_canonical_for_returns_none_for_unknown(base_env, alias_map):
    result = alias_env(base_env, alias_map)
    assert result.canonical_for("nonexistent") is None


def test_summary_contains_resolved_count(base_env, alias_map):
    result = alias_env(base_env, alias_map)
    assert "3" in result.summary()


def test_summary_lists_missing_aliases(base_env):
    result = alias_env(base_env, {"ghost": "GHOST_KEY"})
    assert "ghost" in result.summary()


def test_invert_aliases_flips_mapping(alias_map):
    inverted = invert_aliases(alias_map)
    assert inverted["DATABASE_URL"] == "db_url"
    assert inverted["SECRET_KEY"] == "secret"


def test_empty_alias_map_returns_empty_resolved(base_env):
    result = alias_env(base_env, {})
    assert result.resolved == {}
    assert result.not_found == []
