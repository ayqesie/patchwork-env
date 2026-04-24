"""Diff logic — compares two parsed env dicts and reports differences."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class EnvDiff:
    """Result of comparing two env files."""
    added: Dict[str, str] = field(default_factory=dict)      # keys only in right
    removed: Dict[str, str] = field(default_factory=dict)    # keys only in left
    changed: Dict[str, tuple] = field(default_factory=dict)  # key -> (left_val, right_val)
    unchanged: Dict[str, str] = field(default_factory=dict)  # identical in both

    @property
    def has_diff(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def summary(self) -> str:
        lines: List[str] = []
        for key, val in sorted(self.added.items()):
            lines.append(f"+ {key}={val}")
        for key, val in sorted(self.removed.items()):
            lines.append(f"- {key}={val}")
        for key, (lv, rv) in sorted(self.changed.items()):
            lines.append(f"~ {key}: {lv!r} -> {rv!r}")
        return "\n".join(lines) if lines else "(no differences)"


def diff_envs(
    left: Dict[str, str],
    right: Dict[str, str],
    left_label: str = "left",
    right_label: str = "right",
) -> EnvDiff:
    """Compare two env dicts and return an EnvDiff."""
    all_keys = set(left) | set(right)
    result = EnvDiff()

    for key in all_keys:
        in_left = key in left
        in_right = key in right

        if in_left and not in_right:
            result.removed[key] = left[key]
        elif in_right and not in_left:
            result.added[key] = right[key]
        elif left[key] != right[key]:
            result.changed[key] = (left[key], right[key])
        else:
            result.unchanged[key] = left[key]

    return result
