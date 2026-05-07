"""Split a single .env file into multiple files by prefix or explicit grouping."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SplitResult:
    groups: Dict[str, Dict[str, str]] = field(default_factory=dict)
    ungrouped: Dict[str, str] = field(default_factory=dict)
    source_key_count: int = 0

    def has_groups(self) -> bool:
        return bool(self.groups)

    def summary(self) -> str:
        parts = [f"{len(self.groups)} group(s) from {self.source_key_count} key(s)"]
        for name, keys in self.groups.items():
            parts.append(f"  [{name}] {len(keys)} key(s)")
        if self.ungrouped:
            parts.append(f"  [ungrouped] {len(self.ungrouped)} key(s)")
        return "\n".join(parts)


def _detect_prefixes(env: Dict[str, str], min_count: int = 2) -> List[str]:
    """Return prefixes (up to first underscore) that appear at least min_count times."""
    from collections import Counter
    counts: Counter = Counter()
    for key in env:
        if "_" in key:
            counts[key.split("_", 1)[0]] += 1
    return [prefix for prefix, count in counts.items() if count >= min_count]


def split_env(
    env: Dict[str, str],
    prefixes: Optional[List[str]] = None,
    strip_prefix: bool = False,
) -> SplitResult:
    """Split *env* into groups keyed by prefix.

    Args:
        env: Parsed environment dict.
        prefixes: Explicit list of prefixes to split on. Auto-detected when None.
        strip_prefix: If True, remove the prefix (and underscore) from keys in each group.
    """
    result = SplitResult(source_key_count=len(env))
    active_prefixes = prefixes if prefixes is not None else _detect_prefixes(env)

    for key, value in env.items():
        matched = False
        for prefix in active_prefixes:
            if key.startswith(prefix + "_"):
                group_key = key[len(prefix) + 1:] if strip_prefix else key
                result.groups.setdefault(prefix, {})[group_key] = value
                matched = True
                break
        if not matched:
            result.ungrouped[key] = value

    return result


def to_env_string(env: Dict[str, str]) -> str:
    """Serialize a dict back to .env format."""
    return "\n".join(f"{k}={v}" for k, v in env.items())
