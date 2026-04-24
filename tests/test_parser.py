"""Tests for patchwork_env.parser"""

import pytest
from pathlib import Path

from patchwork_env.parser import parse_env_file, parse_env_string, _strip_quotes


# ── _strip_quotes ────────────────────────────────────────────────────────────

def test_strip_double_quotes():
    assert _strip_quotes('"hello world"') == "hello world"


def test_strip_single_quotes():
    assert _strip_quotes("'hello'") == "hello"


def test_no_quotes_unchanged():
    assert _strip_quotes("plain") == "plain"


def test_mismatched_quotes_unchanged():
    assert _strip_quotes('"oops\'') == '"oops\''


# ── parse_env_string ─────────────────────────────────────────────────────────

def test_basic_parse():
    result = parse_env_string("FOO=bar\nBAZ=qux\n")
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_ignores_comments():
    result = parse_env_string("# this is a comment\nKEY=value\n")
    assert result == {"KEY": "value"}


def test_ignores_blank_lines():
    result = parse_env_string("\n\nKEY=value\n\n")
    assert result == {"KEY": "value"}


def test_quoted_values():
    result = parse_env_string('DB_URL="postgres://localhost/db"')
    assert result == {"DB_URL": "postgres://localhost/db"}


def test_value_with_equals():
    result = parse_env_string("TOKEN=abc=def=ghi")
    assert result == {"TOKEN": "abc=def=ghi"}


def test_invalid_line_raises():
    with pytest.raises(ValueError, match="Invalid syntax"):
        parse_env_string("THIS IS NOT VALID")


# ── parse_env_file ───────────────────────────────────────────────────────────

def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        parse_env_file("/tmp/does_not_exist_xyz.env")


def test_parse_real_file(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("APP_ENV=production\nDEBUG=false\n")
    result = parse_env_file(env_file)
    assert result == {"APP_ENV": "production", "DEBUG": "false"}
