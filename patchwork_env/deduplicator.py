"""Deduplicator: remove duplicate values across keys in an .env dict."""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class DeduplicateResult:
    env: Dict[str, str]
    duplicates: Dict[str, List[str]]  # value -> list of keys sharing it
    removed: List[str]  # keys removed because their value was a duplicate
    kept: List[str]     # keys retained as the canonical key for a value

    def has_issues(self) -> bool:
        return bool(self.duplicates)

    def summary(self) -> str:
        if not self.has_issues():
            return "No duplicate values found."
        lines = [f"Found {len(self.duplicates)} duplicate value(s):"]
        for val, keys in self.duplicates.items():
            display_val = val[:30] + "..." if len(val) > 30 else val
            lines.append(f"  '{display_val}' shared by: {', '.join(keys)}")
        if self.removed:
            lines.append(f"Removed keys: {', '.join(self.removed)}")
            lines.append(f"Kept keys:    {', '.join(self.kept)}")
        return "\n".join(lines)


def find_duplicate_values(
    env: Dict[str, str],
    ignore_empty: bool = True,
) -> Dict[str, List[str]]:
    """Return a mapping of value -> [keys] for values that appear more than once."""
    value_map: Dict[str, List[str]] = {}
    for key, val in env.items():
        if ignore_empty and val == "":
            continue
        value_map.setdefault(val, []).append(key)
    return {v: keys for v, keys in value_map.items() if len(keys) > 1}


def deduplicate_env(
    env: Dict[str, str],
    strategy: str = "keep_first",
    ignore_empty: bool = True,
) -> DeduplicateResult:
    """Remove keys with duplicate values, keeping one canonical key per value.

    Args:
        env: The parsed environment dict.
        strategy: 'keep_first' keeps the first key encountered;
                  'keep_last' keeps the last key encountered.
        ignore_empty: If True, empty-string values are not considered duplicates.

    Returns:
        DeduplicateResult with cleaned env and metadata.
    """
    if strategy not in ("keep_first", "keep_last"):
        raise ValueError(f"Unknown strategy: {strategy!r}. Use 'keep_first' or 'keep_last'.")

    duplicates = find_duplicate_values(env, ignore_empty=ignore_empty)
    removed: List[str] = []
    kept: List[str] = []
    skip: set = set()

    for val, keys in duplicates.items():
        canonical = keys[0] if strategy == "keep_first" else keys[-1]
        dropped = [k for k in keys if k != canonical]
        kept.append(canonical)
        removed.extend(dropped)
        skip.update(dropped)

    clean_env = {k: v for k, v in env.items() if k not in skip}
    return DeduplicateResult(
        env=clean_env,
        duplicates=duplicates,
        removed=sorted(removed),
        kept=sorted(kept),
    )
