"""Strip keys from a .env dict based on a list or pattern."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class StripResult:
    stripped: Dict[str, str] = field(default_factory=dict)
    removed_keys: List[str] = field(default_factory=list)
    not_found: List[str] = field(default_factory=list)

    def has_changes(self) -> bool:
        return bool(self.removed_keys)

    def summary(self) -> str:
        lines = [
            f"Keys removed : {len(self.removed_keys)}",
            f"Keys not found: {len(self.not_found)}",
            f"Keys remaining: {len(self.stripped)}",
        ]
        if self.removed_keys:
            lines.append("Removed: " + ", ".join(sorted(self.removed_keys)))
        if self.not_found:
            lines.append("Not found: " + ", ".join(sorted(self.not_found)))
        return "\n".join(lines)


def strip_env(
    env: Dict[str, str],
    keys: Optional[List[str]] = None,
    patterns: Optional[List[str]] = None,
) -> StripResult:
    """Return a copy of *env* with the specified keys (or glob patterns) removed.

    Args:
        env: The source environment dictionary.
        keys: Exact key names to remove.
        patterns: Glob-style patterns (e.g. ``"AWS_*"``) to match keys for removal.

    Returns:
        A :class:`StripResult` with the pruned dict and bookkeeping info.
    """
    keys = list(keys or [])
    patterns = list(patterns or [])

    to_remove: set[str] = set()

    # Exact keys
    not_found: List[str] = []
    for k in keys:
        if k in env:
            to_remove.add(k)
        else:
            not_found.append(k)

    # Pattern-matched keys
    for pattern in patterns:
        matched = [k for k in env if fnmatch.fnmatch(k, pattern)]
        to_remove.update(matched)

    stripped = {k: v for k, v in env.items() if k not in to_remove}
    removed_keys = sorted(to_remove)

    return StripResult(
        stripped=stripped,
        removed_keys=removed_keys,
        not_found=not_found,
    )
