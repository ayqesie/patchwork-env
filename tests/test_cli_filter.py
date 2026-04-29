"""Tests for patchwork_env.cli_filter."""

import argparse
from pathlib import Path
import pytest

from patchwork_env.cli_filter import run_filter


@pytest.fixture
def env_files(tmp_path):
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def _args(**kwargs) -> argparse.Namespace:
    defaults = {
        "include": None,
        "exclude": None,
        "prefix": None,
        "value_pattern": None,
        "empty_only": False,
        "nonempty_only": False,
        "output": None,
        "summary": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_missing_file_returns_two(env_files):
    args = _args(env_file=str(env_files / "missing.env"))
    assert run_filter(args) == 2


def test_no_match_returns_one(env_files):
    f = _write(env_files / "a.env", "APP_HOST=localhost\n")
    args = _args(env_file=str(f), prefix="DB_")
    assert run_filter(args) == 1


def test_match_returns_zero(env_files):
    f = _write(env_files / "a.env", "APP_HOST=localhost\nAPP_PORT=8080\n")
    args = _args(env_file=str(f), prefix="APP_")
    assert run_filter(args) == 0


def test_output_file_written(env_files):
    f = _write(env_files / "a.env", "DB_HOST=db\nAPP_HOST=app\n")
    out = env_files / "out.env"
    args = _args(env_file=str(f), prefix="DB_", output=str(out))
    rc = run_filter(args)
    assert rc == 0
    assert out.exists()
    assert "DB_HOST" in out.read_text()
    assert "APP_HOST" not in out.read_text()


def test_empty_only_filter(env_files):
    f = _write(env_files / "a.env", "FILLED=yes\nEMPTY=\n")
    out = env_files / "out.env"
    args = _args(env_file=str(f), empty_only=True, output=str(out))
    rc = run_filter(args)
    assert rc == 0
    assert "EMPTY" in out.read_text()
    assert "FILLED" not in out.read_text()


def test_exclude_pattern(env_files):
    f = _write(env_files / "a.env", "SECRET_KEY=abc\nAPP_HOST=localhost\n")
    out = env_files / "out.env"
    args = _args(env_file=str(f), exclude=["SECRET*"], output=str(out))
    rc = run_filter(args)
    assert rc == 0
    assert "APP_HOST" in out.read_text()
    assert "SECRET_KEY" not in out.read_text()
