"""Tests for patchwork_env.snapshot."""

import pytest
from pathlib import Path

from patchwork_env.snapshot import (
    Snapshot,
    delete_snapshot,
    list_snapshots,
    load_snapshot,
    save_snapshot,
)


@pytest.fixture
def snap_dir(tmp_path: Path) -> Path:
    return tmp_path / "snaps"


@pytest.fixture
def sample_snapshot() -> Snapshot:
    return Snapshot(
        name="staging",
        env={"DB_HOST": "localhost", "DEBUG": "true"},
        source_file=".env.staging",
    )


def test_save_creates_file(snap_dir, sample_snapshot):
    path = save_snapshot(sample_snapshot, snapshot_dir=snap_dir)
    assert path.exists()
    assert path.name == "staging.json"


def test_load_roundtrip(snap_dir, sample_snapshot):
    save_snapshot(sample_snapshot, snapshot_dir=snap_dir)
    loaded = load_snapshot("staging", snapshot_dir=snap_dir)
    assert loaded.name == "staging"
    assert loaded.env == {"DB_HOST": "localhost", "DEBUG": "true"}
    assert loaded.source_file == ".env.staging"


def test_load_missing_raises(snap_dir):
    with pytest.raises(FileNotFoundError, match="nope"):
        load_snapshot("nope", snapshot_dir=snap_dir)


def test_list_snapshots_empty(snap_dir):
    assert list_snapshots(snapshot_dir=snap_dir) == []


def test_list_snapshots_returns_names(snap_dir):
    for name in ("prod", "staging", "dev"):
        save_snapshot(Snapshot(name=name, env={}), snapshot_dir=snap_dir)
    assert list_snapshots(snapshot_dir=snap_dir) == ["dev", "prod", "staging"]


def test_delete_existing_snapshot(snap_dir, sample_snapshot):
    save_snapshot(sample_snapshot, snapshot_dir=snap_dir)
    result = delete_snapshot("staging", snapshot_dir=snap_dir)
    assert result is True
    assert list_snapshots(snapshot_dir=snap_dir) == []


def test_delete_missing_snapshot_returns_false(snap_dir):
    result = delete_snapshot("ghost", snapshot_dir=snap_dir)
    assert result is False


def test_snapshot_created_at_is_set():
    s = Snapshot(name="x", env={})
    assert s.created_at  # non-empty ISO string


def test_snapshot_to_dict_and_from_dict(sample_snapshot):
    d = sample_snapshot.to_dict()
    restored = Snapshot.from_dict(d)
    assert restored.name == sample_snapshot.name
    assert restored.env == sample_snapshot.env
    assert restored.source_file == sample_snapshot.source_file
