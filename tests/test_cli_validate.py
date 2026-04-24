"""Tests for cli_validate.run_validate."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from patchwork_env.cli_validate import run_validate


@pytest.fixture()
def tmp_files(tmp_path: Path):
    """Return a helper that writes files under tmp_path."""

    def _write(name: str, content: str) -> Path:
        p = tmp_path / name
        p.write_text(textwrap.dedent(content))
        return p

    return _write


def test_valid_env_returns_zero(tmp_files):
    env = tmp_files(".env", "DB_HOST=localhost\nDB_PORT=5432\n")
    base = tmp_files(".env.base", "DB_HOST=example.com\nDB_PORT=5432\n")
    code = run_validate([str(env), "--base-env", str(base), "--no-color"])
    assert code == 0


def test_missing_required_key_returns_one(tmp_files):
    env = tmp_files(".env", "DB_HOST=localhost\n")
    base = tmp_files(".env.base", "DB_HOST=example.com\nDB_PORT=5432\n")
    code = run_validate([str(env), "--base-env", str(base), "--no-color"])
    assert code == 1


def test_missing_env_file_returns_two(tmp_files, tmp_path):
    base = tmp_files(".env.base", "DB_HOST=example.com\n")
    missing = tmp_path / "nonexistent.env"
    code = run_validate([str(missing), "--base-env", str(base), "--no-color"])
    assert code == 2


def test_missing_schema_file_returns_two(tmp_files, tmp_path):
    env = tmp_files(".env", "DB_HOST=localhost\n")
    missing_schema = tmp_path / "schema.toml"
    code = run_validate([str(env), "--schema", str(missing_schema), "--no-color"])
    assert code == 2


def test_missing_base_env_file_returns_two(tmp_files, tmp_path):
    env = tmp_files(".env", "DB_HOST=localhost\n")
    missing_base = tmp_path / "base.env"
    code = run_validate([str(env), "--base-env", str(missing_base), "--no-color"])
    assert code == 2


def test_no_schema_arg_returns_two(tmp_files):
    env = tmp_files(".env", "DB_HOST=localhost\n")
    code = run_validate([str(env), "--no-color"])
    assert code == 2


def test_schema_toml_valid_env_returns_zero(tmp_files):
    env = tmp_files(".env", "API_KEY=secret\nDEBUG=true\n")
    schema_toml = tmp_files(
        "schema.toml",
        """
        [required]
        API_KEY = "str"

        [optional]
        DEBUG = "bool"
        """,
    )
    code = run_validate([str(env), "--schema", str(schema_toml), "--no-color"])
    assert code == 0


def test_schema_toml_missing_required_returns_one(tmp_files):
    env = tmp_files(".env", "DEBUG=true\n")
    schema_toml = tmp_files(
        "schema.toml",
        """
        [required]
        API_KEY = "str"
        """,
    )
    code = run_validate([str(env), "--schema", str(schema_toml), "--no-color"])
    assert code == 1
