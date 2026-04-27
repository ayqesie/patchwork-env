"""Tests for patchwork_env.formatter module."""

from patchwork_env.differ import diff_envs
from patchwork_env.formatter import format_diff, format_summary, _colorize


BASE = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
TARGET = {"HOST": "prod.example.com", "PORT": "5432", "WORKERS": "4"}


def test_format_diff_contains_header():
    d = diff_envs(BASE, TARGET)
    output = format_diff(d, color=False)
    assert "--- base" in output
    assert "+++ target" in output


def test_format_diff_shows_removed_key():
    d = diff_envs(BASE, TARGET)
    output = format_diff(d, color=False)
    assert "- DEBUG=true" in output


def test_format_diff_shows_added_key():
    d = diff_envs(BASE, TARGET)
    output = format_diff(d, color=False)
    assert "+ WORKERS=4" in output


def test_format_diff_shows_changed_key():
    d = diff_envs(BASE, TARGET)
    output = format_diff(d, color=False)
    assert "~ HOST" in output
    assert "localhost" in output
    assert "prod.example.com" in output


def test_format_diff_no_diff_message():
    d = diff_envs(BASE, BASE)
    output = format_diff(d, color=False)
    assert "(no differences)" in output


def test_format_diff_custom_labels():
    d = diff_envs(BASE, TARGET)
    output = format_diff(d, base_label="dev", target_label="prod", color=False)
    assert "--- dev" in output
    assert "+++ prod" in output


def test_format_diff_unchanged_key_not_shown():
    """Keys that are identical in both envs should not appear in the diff output."""
    d = diff_envs(BASE, TARGET)
    output = format_diff(d, color=False)
    # PORT is the same in both BASE and TARGET, so it should not be listed
    assert "PORT" not in output


def test_format_summary_shows_counts():
    d = diff_envs(BASE, TARGET)
    output = format_summary(d, color=False)
    assert "+1 added" in output
    assert "-1 removed" in output
    assert "~1 changed" in output


def test_format_summary_no_diff():
    d = diff_envs(BASE, BASE)
    output = format_summary(d, color=False)
    assert output == "No differences found."


def test_colorize_enabled():
    result = _colorize("hello", "\033[91m", enabled=True)
    assert "\033[91m" in result
    assert "\033[0m" in result


def test_colorize_disabled():
    result = _colorize("hello", "\033[91m", enabled=False)
    assert result == "hello"
