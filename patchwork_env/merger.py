"""Merge multiple .env files into a single unified environment map.

Later files take precedence over earlier ones (last-write-wins).
Optionally track which source file each key came from.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from patchwork_env.parser import parse_env_file


@dataclass
class MergeResult:
    merged: Dict[str, str] = field(default_factory=dict)
    # key -> (value, source_path)
    provenance: Dict[str, Tuple[str, str]] = field(default_factory=dict)
    # keys that were overridden: key -> list of (value, source) in order seen
    conflicts: Dict[str, List[Tuple[str, str]]] = field(default_factory=dict)

    def has_conflicts(self) -> bool:
        return bool(self.conflicts)

    def summary(self) -> str:
        lines = [f"Merged keys : {len(self.merged)}"]
        if self.conflicts:
            lines.append(f"Conflicts   : {len(self.conflicts)} key(s) overridden")
            for key, history in self.conflicts.items():
                sources = " -> ".join(f"{src}={val!r}" for val, src in history)
                lines.append(f"  {key}: {sources}")
        return "\n".join(lines)


def merge_env_files(
    paths: List[str],
    track_provenance: bool = True,
) -> MergeResult:
    """Merge env files in order; later paths override earlier ones."""
    result = MergeResult()

    for path in paths:
        env = parse_env_file(path)
        for key, value in env.items():
            if key in result.merged and track_provenance:
                prev_val, prev_src = result.provenance[key]
                history = result.conflicts.setdefault(key, [])
                if not history:
                    history.append((prev_val, prev_src))
                history.append((value, path))
            result.merged[key] = value
            if track_provenance:
                result.provenance[key] = (value, path)

    return result


def merge_env_dicts(
    envs: List[Dict[str, str]],
    labels: Optional[List[str]] = None,
) -> MergeResult:
    """Merge pre-parsed env dicts. Labels are used as source names."""
    if labels is None:
        labels = [f"source_{i}" for i in range(len(envs))]
    if len(labels) != len(envs):
        raise ValueError("labels length must match envs length")

    result = MergeResult()
    for label, env in zip(labels, envs):
        for key, value in env.items():
            if key in result.merged:
                prev_val, prev_src = result.provenance[key]
                history = result.conflicts.setdefault(key, [])
                if not history:
                    history.append((prev_val, prev_src))
                history.append((value, label))
            result.merged[key] = value
            result.provenance[key] = (value, label)

    return result
