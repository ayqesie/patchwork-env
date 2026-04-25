"""Tests for patchwork_env.interpolator."""

import pytest
from patchwork_env.interpolator import (
    interpolate,
    find_references,
    unresolved_keys,
    _resolve,
)


# ---------------------------------------------------------------------------
# find_references
# ---------------------------------------------------------------------------

def test_find_references_brace_style():
    refs = find_references("http://${HOST}:${PORT}")
    assert refs == ["HOST", "PORT"]


def test_find_references_bare_style():
    refs = find_references("/home/$USER/app")
    assert refs == ["USER"]


def test_find_references_mixed():
    refs = find_references("${PROTO}://$HOST")
    assert "PROTO" in refs
    assert "HOST" in refs


def test_find_references_no_refs():
    assert find_references("plain-value") == []


def test_find_references_deduplicates():
    refs = find_references("${X}/${X}")
    assert refs == ["X"]


# ---------------------------------------------------------------------------
# _resolve (single pass)
# ---------------------------------------------------------------------------

def test_resolve_brace():
    env = {"HOST": "localhost"}
    assert _resolve("${HOST}:5432", env) == "localhost:5432"


def test_resolve_bare():
    env = {"USER": "alice"}
    assert _resolve("/home/$USER", env) == "/home/alice"


def test_resolve_unknown_left_intact():
    assert _resolve("${MISSING}", {}) == "${MISSING}"


# ---------------------------------------------------------------------------
# interpolate (multi-pass)
# ---------------------------------------------------------------------------

def test_interpolate_simple():
    env = {"HOST": "db.local", "DSN": "postgres://${HOST}/mydb"}
    result = interpolate(env)
    assert result["DSN"] == "postgres://db.local/mydb"


def test_interpolate_chained():
    env = {"A": "hello", "B": "${A} world", "C": "${B}!"}
    result = interpolate(env)
    assert result["C"] == "hello world!"


def test_interpolate_does_not_mutate_input():
    env = {"X": "${Y}", "Y": "42"}
    original = dict(env)
    interpolate(env)
    assert env == original


def test_interpolate_self_reference_does_not_hang():
    env = {"A": "${A}"}
    result = interpolate(env, max_passes=5)
    assert result["A"] == "${A}"  # unresolvable, left as-is


def test_interpolate_no_references_unchanged():
    env = {"KEY": "value", "OTHER": "123"}
    assert interpolate(env) == env


# ---------------------------------------------------------------------------
# unresolved_keys
# ---------------------------------------------------------------------------

def test_unresolved_keys_empty_when_all_resolved():
    env = {"HOST": "localhost", "URL": "http://${HOST}"}
    assert unresolved_keys(env) == {}


def test_unresolved_keys_reports_missing():
    env = {"URL": "http://${HOST}"}
    result = unresolved_keys(env)
    assert "URL" in result
    assert "HOST" in result["URL"]
