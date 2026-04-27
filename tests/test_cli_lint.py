"""Tests for the lint CLI command."""

import pytest
from pathlib import Path
from unittest.mock import patch

from patchwork_env.cli_lint import run_lint


@pytest.fixture
def env_files(tmp_path):
    """Provide a helper to write temp .env files."""
    def _write(name, content):
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _write


def _args(path, **kwargs):
    """Build a minimal namespace for run_lint."""
    import argparse
    defaults = dict(env=path, no_color=True, quiet=False)
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


# ---------------------------------------------------------------------------
# Exit code: 0 — no issues
# ---------------------------------------------------------------------------

def test_clean_env_returns_zero(env_files):
    path = env_files(".env", "DATABASE_URL=postgres://localhost/db\nSECRET_KEY=abc123\n")
    assert run_lint(_args(path)) == 0


# ---------------------------------------------------------------------------
# Exit code: 1 — lint issues found
# ---------------------------------------------------------------------------

def test_lowercase_key_returns_one(env_files):
    path = env_files(".env", "database_url=postgres://localhost/db\n")
    assert run_lint(_args(path)) == 1


def test_duplicate_key_returns_one(env_files):
    path = env_files(".env", "FOO=bar\nFOO=baz\n")
    assert run_lint(_args(path)) == 1


def test_whitespace_in_value_returns_one(env_files):
    path = env_files(".env", "FOO= bar \n")
    assert run_lint(_args(path)) == 1


def test_multiple_issues_still_returns_one(env_files):
    path = env_files(".env", "foo=bar\nbaz= bad value \n")
    assert run_lint(_args(path)) == 1


# ---------------------------------------------------------------------------
# Exit code: 2 — file not found
# ---------------------------------------------------------------------------

def test_missing_file_returns_two(tmp_path):
    missing = str(tmp_path / "nonexistent.env")
    assert run_lint(_args(missing)) == 2


# ---------------------------------------------------------------------------
# Output content checks
# ---------------------------------------------------------------------------

def test_output_mentions_issue_key(env_files, capsys):
    path = env_files(".env", "bad_key=value\n")
    run_lint(_args(path))
    captured = capsys.readouterr()
    assert "bad_key" in captured.out


def test_clean_env_prints_ok_message(env_files, capsys):
    path = env_files(".env", "GOOD_KEY=value\n")
    run_lint(_args(path))
    captured = capsys.readouterr()
    # Should indicate no issues
    assert "no issues" in captured.out.lower() or "clean" in captured.out.lower() or "0" in captured.out


def test_quiet_suppresses_output(env_files, capsys):
    path = env_files(".env", "bad_key=value\n")
    run_lint(_args(path, quiet=True))
    captured = capsys.readouterr()
    assert captured.out == ""


def test_missing_file_prints_error(tmp_path, capsys):
    missing = str(tmp_path / "ghost.env")
    run_lint(_args(missing))
    captured = capsys.readouterr()
    assert "not found" in captured.out.lower() or "error" in captured.out.lower() or missing in captured.out
