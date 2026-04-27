"""Tests for patchwork_env.cli_redact."""

import pytest
from argparse import Namespace
from pathlib import Path

from patchwork_env.cli_redact import run_redact


@pytest.fixture
def env_files(tmp_path):
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def _args(**kwargs) -> Namespace:
    defaults = {"env_file": "", "extra_keys": None, "output": None}
    defaults.update(kwargs)
    return Namespace(**defaults)


def test_missing_file_returns_two(env_files):
    args = _args(env_file=str(env_files / "missing.env"))
    assert run_redact(args) == 2


def test_clean_env_returns_zero(env_files):
    f = _write(env_files / "clean.env", "APP_NAME=myapp\nPORT=8080\n")
    args = _args(env_file=str(f))
    assert run_redact(args) == 0


def test_sensitive_env_returns_one(env_files):
    f = _write(env_files / "secret.env", "APP_NAME=myapp\nSECRET_KEY=abc\n")
    args = _args(env_file=str(f))
    assert run_redact(args) == 1


def test_output_file_written(env_files):
    f = _write(env_files / "secret.env", "SECRET_KEY=abc\nPORT=8080\n")
    out = env_files / "redacted.env"
    args = _args(env_file=str(f), output=str(out))
    run_redact(args)
    assert out.exists()
    content = out.read_text()
    assert "***REDACTED***" in content
    assert "abc" not in content


def test_output_preserves_safe_values(env_files):
    f = _write(env_files / "mixed.env", "SECRET_KEY=abc\nPORT=8080\n")
    out = env_files / "redacted.env"
    args = _args(env_file=str(f), output=str(out))
    run_redact(args)
    content = out.read_text()
    assert "PORT=8080" in content


def test_extra_keys_redacted(env_files):
    f = _write(env_files / "extra.env", "APP_NAME=myapp\nPORT=8080\n")
    out = env_files / "redacted.env"
    args = _args(env_file=str(f), extra_keys=["APP_NAME"], output=str(out))
    result = run_redact(args)
    assert result == 1
    content = out.read_text()
    assert "***REDACTED***" in content
    assert "myapp" not in content


def test_stdout_output_no_file(env_files, capsys):
    f = _write(env_files / "simple.env", "PORT=8080\n")
    args = _args(env_file=str(f))
    run_redact(args)
    captured = capsys.readouterr()
    assert "PORT=8080" in captured.out
