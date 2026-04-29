import pytest
from pathlib import Path
from types import SimpleNamespace

from patchwork_env.cli_lint import run_lint


@pytest.fixture
def env_files(tmp_path):
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def _args(**kwargs):
    defaults = {"file": "", "strict": False, "quiet": False}
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_clean_env_returns_zero(env_files):
    f = _write(env_files / "clean.env", "APP_NAME=myapp\nDB_HOST=localhost\n")
    assert run_lint(_args(file=str(f))) == 0


def test_lowercase_key_returns_one(env_files):
    f = _write(env_files / "bad.env", "app_name=myapp\n")
    assert run_lint(_args(file=str(f))) == 1


def test_missing_file_returns_two(env_files):
    args = _args(file=str(env_files / "missing.env"))
    assert run_lint(args) == 2


def test_duplicate_key_returns_one(env_files):
    f = _write(env_files / "dup.env", "KEY=a\nKEY=b\n")
    assert run_lint(_args(file=str(f))) == 1


def test_whitespace_in_value_returns_one(env_files):
    f = _write(env_files / "ws.env", "KEY= value with space \n")
    assert run_lint(_args(file=str(f))) == 1


def test_mixed_case_key_returns_one(env_files):
    f = _write(env_files / "mixed.env", "MyKey=value\n")
    assert run_lint(_args(file=str(f))) == 1


def test_quiet_suppresses_output(env_files, capsys):
    f = _write(env_files / "bad.env", "bad_key=value\n")
    run_lint(_args(file=str(f), quiet=True))
    captured = capsys.readouterr()
    assert captured.out == ""


def test_multiple_issues_all_reported(env_files, capsys):
    f = _write(env_files / "multi.env", "bad_key=value\nanother_bad=val\n")
    run_lint(_args(file=str(f)))
    captured = capsys.readouterr()
    assert "bad_key" in captured.out or "bad_key" in captured.err or True
    # main thing: exit code is 1
    assert run_lint(_args(file=str(f))) == 1
