"""Snapshot module — save and load named env snapshots for later comparison."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_SNAPSHOT_DIR = Path(".patchwork_snapshots")


@dataclass
class Snapshot:
    name: str
    env: Dict[str, str]
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source_file: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "env": self.env,
            "created_at": self.created_at,
            "source_file": self.source_file,
        }

    @staticmethod
    def from_dict(data: dict) -> "Snapshot":
        return Snapshot(
            name=data["name"],
            env=data["env"],
            created_at=data.get("created_at", ""),
            source_file=data.get("source_file"),
        )


def save_snapshot(snapshot: Snapshot, snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR) -> Path:
    """Persist a snapshot to disk as JSON. Returns the file path written."""
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    dest = snapshot_dir / f"{snapshot.name}.json"
    dest.write_text(json.dumps(snapshot.to_dict(), indent=2))
    return dest


def load_snapshot(name: str, snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR) -> Snapshot:
    """Load a named snapshot. Raises FileNotFoundError if it doesn't exist."""
    path = snapshot_dir / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Snapshot '{name}' not found in {snapshot_dir}")
    data = json.loads(path.read_text())
    return Snapshot.from_dict(data)


def list_snapshots(snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR) -> List[str]:
    """Return names of all saved snapshots, sorted alphabetically."""
    if not snapshot_dir.exists():
        return []
    return sorted(p.stem for p in snapshot_dir.glob("*.json"))


def delete_snapshot(name: str, snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR) -> bool:
    """Delete a named snapshot. Returns True if deleted, False if not found."""
    path = snapshot_dir / f"{name}.json"
    if path.exists():
        path.unlink()
        return True
    return False
