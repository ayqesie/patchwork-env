import json
import pytest
from pathlib import Path
from types import SimpleNamespace

from patchwork_env.cli_freeze import run_freeze, run_drift


@pytest.fixture
def env_files(tmp_path):
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def _args(**kwargs):
    defaults = {"env_file": "", "output": "", "keys": None, "freeze_file": ""}
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_freeze_missing_env_returns_two(env_files):
    args = _args(env_file=str(env_files / "missing.env"), output=str(env_files / "out.json"))
    assert run_freeze(args) == 2


def test_freeze_creates_output_file(env_files):
    env = _write(env_files / ".env", "DB_HOST=localhost\nDB_PORT=5432\n")
    out = env_files / "frozen.json"
    args = _args(env_file=str(env), output=str(out))
    rc = run_freeze(args)
    assert rc == 0
    assert out.exists()


def test_freeze_output_contains_keys(env_files):
    env = _write(env_files / ".env", "DB_HOST=localhost\nDB_PORT=5432\n")
    out = env_files / "frozen.json"
    args = _args(env_file=str(env), output=str(out))
    run_freeze(args)
    data = json.loads(out.read_text())
    assert data["DB_HOST"] == "localhost"
    assert data["DB_PORT"] == "5432"


def test_freeze_subset_via_keys_arg(env_files):
    env = _write(env_files / ".env", "DB_HOST=localhost\nAPI_KEY=secret\n")
    out = env_files / "frozen.json"
    args = _args(env_file=str(env), output=str(out), keys="DB_HOST")
    run_freeze(args)
    data = json.loads(out.read_text())
    assert "DB_HOST" in data
    assert "API_KEY" not in data


def test_drift_missing_freeze_file_returns_two(env_files):
    env = _write(env_files / ".env", "DB_HOST=localhost\n")
    args = _args(freeze_file=str(env_files / "missing.json"), env_file=str(env))
    assert run_drift(args) == 2


def test_drift_missing_env_file_returns_two(env_files):
    freeze = _write(env_files / "frozen.json", json.dumps({"DB_HOST": "localhost"}))
    args = _args(freeze_file=str(freeze), env_file=str(env_files / "missing.env"))
    assert run_drift(args) == 2


def test_drift_no_drift_returns_zero(env_files):
    env = _write(env_files / ".env", "DB_HOST=localhost\n")
    freeze = _write(env_files / "frozen.json", json.dumps({"DB_HOST": "localhost"}))
    args = _args(freeze_file=str(freeze), env_file=str(env))
    assert run_drift(args) == 0


def test_drift_detected_returns_one(env_files):
    env = _write(env_files / ".env", "DB_HOST=prod-host\n")
    freeze = _write(env_files / "frozen.json", json.dumps({"DB_HOST": "localhost"}))
    args = _args(freeze_file=str(freeze), env_file=str(env))
    assert run_drift(args) == 1
