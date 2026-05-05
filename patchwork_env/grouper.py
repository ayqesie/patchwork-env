"""Group .env keys by prefix, suffix, or custom pattern."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class GroupResult:
    groups: Dict[str, List[str]] = field(default_factory=dict)
    ungrouped: List[str] = field(default_factory=list)

    def has_groups(self) -> bool:
        return bool(self.groups)

    def summary(self) -> str:
        lines = []
        for label, keys in sorted(self.groups.items()):
            lines.append(f"[{label}] {len(keys)} key(s): {', '.join(sorted(keys))}")
        if self.ungrouped:
            lines.append(f"[ungrouped] {len(self.ungrouped)} key(s): {', '.join(sorted(self.ungrouped))}")
        return "\n".join(lines) if lines else "No groups found."

    def all_groups(self) -> List[str]:
        return sorted(self.groups.keys())


def group_by_prefix(
    env: Dict[str, str],
    prefixes: Optional[List[str]] = None,
    delimiter: str = "_",
) -> GroupResult:
    """Group keys by their prefix (up to the first delimiter).

    If *prefixes* is given, only those prefix labels are used.  Otherwise
    every prefix that appears at least twice is treated as a group.
    """
    result = GroupResult()

    if prefixes is not None:
        allowed = set(p.upper().rstrip(delimiter) for p in prefixes)
    else:
        allowed = None

    counts: Dict[str, int] = {}
    for key in env:
        parts = key.split(delimiter, 1)
        if len(parts) == 2:
            counts[parts[0]] = counts.get(parts[0], 0) + 1

    for key in env:
        parts = key.split(delimiter, 1)
        prefix = parts[0] if len(parts) == 2 else None

        if prefix and (allowed is not None and prefix in allowed or allowed is None and counts.get(prefix, 0) >= 2):
            result.groups.setdefault(prefix, []).append(key)
        else:
            result.ungrouped.append(key)

    return result


def group_by_pattern(
    env: Dict[str, str],
    patterns: Dict[str, str],
) -> GroupResult:
    """Group keys by named regex patterns.

    *patterns* maps a label to a regex string.  Keys are matched in
    iteration order; the first match wins.  Unmatched keys go to
    *ungrouped*.
    """
    compiled = [(label, re.compile(pat)) for label, pat in patterns.items()]
    result = GroupResult()

    for key in env:
        matched = False
        for label, rx in compiled:
            if rx.search(key):
                result.groups.setdefault(label, []).append(key)
                matched = True
                break
        if not matched:
            result.ungrouped.append(key)

    return result
