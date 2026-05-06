import pytest
from pathlib import Path
from types import SimpleNamespace

from patchwork_env.cli_transform import run_transform, _parse_rule


@pytest.fixture
def env_files(tmp_path):
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def _args(**kwargs):
    defaults = {"file": "", "rule": None, "keys": None, "output": None}
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_missing_file_returns_two(env_files):
    args = _args(file=str(env_files / "missing.env"), rule=["upper"])
    assert run_transform(args) == 2


def test_no_rules_returns_two(env_files):
    f = _write(env_files / "a.env", "KEY=value\n")
    args = _args(file=str(f), rule=[])
    assert run_transform(args) == 2


def test_transform_changes_returns_one(env_files):
    f = _write(env_files / "a.env", "APP_NAME=myapp\n")
    args = _args(file=str(f), rule=["upper"])
    assert run_transform(args) == 1


def test_no_change_returns_zero(env_files):
    f = _write(env_files / "a.env", "APP_NAME=MYAPP\n")
    args = _args(file=str(f), rule=["upper"])
    assert run_transform(args) == 0


def test_output_file_written(env_files):
    f = _write(env_files / "a.env", "KEY=hello\n")
    out = env_files / "out.env"
    args = _args(file=str(f), rule=["upper"], output=str(out))
    run_transform(args)
    assert out.exists()
    assert "HELLO" in out.read_text()


def test_keys_filter_applied(env_files):
    f = _write(env_files / "a.env", "KEY=hello\nOTHER=world\n")
    out = env_files / "out.env"
    args = _args(file=str(f), rule=["upper"], keys="KEY", output=str(out))
    run_transform(args)
    content = out.read_text()
    assert "HELLO" in content
    assert "world" in content


def test_output_not_written_when_no_changes(env_files):
    """When the transform produces no changes and an output path is given,
    the output file should still be written (idempotent copy)."""
    f = _write(env_files / "a.env", "KEY=ALREADY_UPPER\n")
    out = env_files / "out.env"
    args = _args(file=str(f), rule=["upper"], output=str(out))
    run_transform(args)
    assert out.exists()
    assert "ALREADY_UPPER" in out.read_text()


def test_parse_rule_no_arg():
    r = _parse_rule("upper")
    assert r == {"rule": "upper"}


def test_parse_rule_with_arg():
    r = _parse_rule("prefix:prod_")
    assert r == {"rule": "prefix", "arg": "prod_"}


def test_parse_rule_replace_with_comma():
    r = _parse_rule("replace:old,new")
    assert r == {"rule": "replace", "arg": "old,new"}
