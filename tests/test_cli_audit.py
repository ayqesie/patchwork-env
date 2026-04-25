"""Tests for patchwork_env.cli_audit."""

import pytest
from pathlib import Path
from patchwork_env.cli_audit import run_audit


@pytest.fixture
def env_files(tmp_path):
    def _write(name, content):
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _write


def test_clean_env_returns_zero(env_files):
    path = env_files("clean.env", "HOST=localhost\nPORT=8080\n")
    assert run_audit(path) == 0


def test_empty_value_returns_one(env_files):
    path = env_files("empty.env", "HOST=localhost\nSECRET=\n")
    assert run_audit(path) == 1


def test_placeholder_returns_one(env_files):
    path = env_files("placeholder.env", "API_KEY=changeme\n")
    assert run_audit(path) == 1


def test_missing_file_returns_two():
    assert run_audit("/nonexistent/path/.env") == 2


def test_duplicate_keys_returns_one(env_files):
    path = env_files("dup.env", "HOST=a\nHOST=b\n")
    assert run_audit(path) == 1


def test_strict_mode_suspicious_returns_one(env_files):
    path = env_files("weak.env", "DB_PASSWORD=abc\n")
    assert run_audit(path, strict=True) == 1


def test_strict_mode_clean_returns_zero(env_files):
    path = env_files("ok.env", "DB_PASSWORD=supersecurepassword\n")
    assert run_audit(path, strict=True) == 0
