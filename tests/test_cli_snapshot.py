"""Tests for patchwork_env.cli_snapshot."""

import pytest
from pathlib import Path
from types import SimpleNamespace

from patchwork_env.cli_snapshot import run_snapshot
from patchwork_env.snapshot import save_snapshot, Snapshot


@pytest.fixture
def snap_dir(tmp_path: Path) -> Path:
    return tmp_path / "snaps"


@pytest.fixture
def env_files(tmp_path: Path):
    base = tmp_path / ".env.base"
    base.write_text("KEY=value\nFOO=bar\n")
    return {"base": base}


def _args(subcommand, **kwargs):
    return SimpleNamespace(subcommand=subcommand, snapshot_dir=None, **kwargs)


def test_save_creates_snapshot(env_files, snap_dir):
    args = _args("save", name="test", env_file=str(env_files["base"]), snapshot_dir=snap_dir)
    args.snapshot_dir = snap_dir
    code = run_snapshot(args)
    assert code == 0
    assert (snap_dir / "test.json").exists()


def test_save_missing_file_returns_two(snap_dir):
    args = SimpleNamespace(subcommand="save", name="x", env_file="/no/such/file", snapshot_dir=snap_dir)
    assert run_snapshot(args) == 2


def test_list_empty(snap_dir, capsys):
    args = SimpleNamespace(subcommand="list", snapshot_dir=snap_dir)
    code = run_snapshot(args)
    assert code == 0
    assert "No snapshots" in capsys.readouterr().out


def test_list_shows_names(snap_dir, capsys):
    for name in ("alpha", "beta"):
        save_snapshot(Snapshot(name=name, env={}), snapshot_dir=snap_dir)
    args = SimpleNamespace(subcommand="list", snapshot_dir=snap_dir)
    run_snapshot(args)
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "beta" in out


def test_diff_no_changes_returns_zero(env_files, snap_dir):
    save_snapshot(Snapshot(name="snap", env={"KEY": "value", "FOO": "bar"}), snapshot_dir=snap_dir)
    args = SimpleNamespace(subcommand="diff", name="snap", env_file=str(env_files["base"]), snapshot_dir=snap_dir)
    assert run_snapshot(args) == 0


def test_diff_with_changes_returns_one(env_files, snap_dir):
    save_snapshot(Snapshot(name="snap", env={"KEY": "old", "FOO": "bar"}), snapshot_dir=snap_dir)
    args = SimpleNamespace(subcommand="diff", name="snap", env_file=str(env_files["base"]), snapshot_dir=snap_dir)
    assert run_snapshot(args) == 1


def test_diff_missing_snapshot_returns_two(env_files, snap_dir):
    args = SimpleNamespace(subcommand="diff", name="ghost", env_file=str(env_files["base"]), snapshot_dir=snap_dir)
    assert run_snapshot(args) == 2


def test_delete_existing(snap_dir):
    save_snapshot(Snapshot(name="to_del", env={}), snapshot_dir=snap_dir)
    args = SimpleNamespace(subcommand="delete", name="to_del", snapshot_dir=snap_dir)
    assert run_snapshot(args) == 0
    assert not (snap_dir / "to_del.json").exists()


def test_delete_missing_returns_two(snap_dir):
    args = SimpleNamespace(subcommand="delete", name="nope", snapshot_dir=snap_dir)
    assert run_snapshot(args) == 2
