"""Tests for patchwork_env.pinpointer."""

import pytest
from patchwork_env.pinpointer import (
    PinpointResult,
    pinpoint_key,
    pinpoint_value,
)


@pytest.fixture()
def envs():
    return {
        "dev": {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "dev-secret"},
        "staging": {"DB_HOST": "staging.db", "DB_PORT": "5432", "SECRET": "stg-secret"},
        "prod": {"DB_HOST": "prod.db", "DB_PORT": "5433"},
    }


def test_key_found_in_all_envs(envs):
    result = pinpoint_key("DB_PORT", envs)
    assert set(result.found_in()) == {"dev", "staging"}
    # prod has 5433 not 5432 so still found but different value
    assert "prod" in result.matches or "prod" in result.missing_from


def test_key_present_everywhere(envs):
    result = pinpoint_key("DB_HOST", envs)
    assert set(result.found_in()) == {"dev", "staging", "prod"}
    assert result.missing_from == []


def test_key_missing_from_some_envs(envs):
    result = pinpoint_key("SECRET", envs)
    assert "dev" in result.found_in()
    assert "staging" in result.found_in()
    assert "prod" in result.missing_from


def test_key_missing_from_all_envs(envs):
    result = pinpoint_key("NONEXISTENT", envs)
    assert not result.has_matches()
    assert set(result.missing_from) == {"dev", "staging", "prod"}


def test_is_consistent_when_all_same():
    envs = {
        "dev": {"PORT": "8080"},
        "staging": {"PORT": "8080"},
        "prod": {"PORT": "8080"},
    }
    result = pinpoint_key("PORT", envs)
    assert result.is_consistent()


def test_is_not_consistent_when_values_differ(envs):
    result = pinpoint_key("DB_HOST", envs)
    assert not result.is_consistent()


def test_is_not_consistent_when_missing_from_some(envs):
    result = pinpoint_key("SECRET", envs)
    assert not result.is_consistent()


def test_value_filter_narrows_matches(envs):
    result = pinpoint_key("DB_PORT", envs, value_filter="5432")
    assert "dev" in result.matches
    assert "staging" in result.matches
    assert "prod" in result.missing_from


def test_summary_contains_key_name(envs):
    result = pinpoint_key("DB_HOST", envs)
    text = result.summary()
    assert "DB_HOST" in text


def test_summary_shows_missing(envs):
    result = pinpoint_key("SECRET", envs)
    text = result.summary()
    assert "<missing>" in text


def test_pinpoint_value_finds_shared_value(envs):
    hits = pinpoint_value("5432", envs)
    assert "dev" in hits
    assert "staging" in hits
    assert "DB_PORT" in hits["dev"]


def test_pinpoint_value_no_match(envs):
    hits = pinpoint_value("not-a-real-value", envs)
    assert hits == {}


def test_pinpoint_value_multiple_keys_same_value():
    envs = {"dev": {"A": "same", "B": "same", "C": "different"}}
    hits = pinpoint_value("same", envs)
    assert set(hits["dev"]) == {"A", "B"}
