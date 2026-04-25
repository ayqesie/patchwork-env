"""Sort and group .env file keys by prefix, alphabetically, or custom order."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SortResult:
    groups: Dict[str, List[str]] = field(default_factory=dict)
    ungrouped: List[str] = field(default_factory=list)
    sorted_env: Dict[str, str] = field(default_factory=dict)

    def summary(self) -> str:
        lines = [f"Total keys: {len(self.sorted_env)}"]
        if self.groups:
            lines.append(f"Groups: {', '.join(self.groups.keys())}")
        if self.ungrouped:
            lines.append(f"Ungrouped keys: {len(self.ungrouped)}")
        return "\n".join(lines)


def sort_alphabetically(env: Dict[str, str]) -> Dict[str, str]:
    """Return a new dict with keys sorted alphabetically."""
    return dict(sorted(env.items()))


def group_by_prefix(
    env: Dict[str, str],
    prefixes: Optional[List[str]] = None,
    separator: str = "_",
) -> SortResult:
    """Group keys by a shared prefix (e.g. DB_, AWS_, APP_).

    If prefixes is None, auto-detect prefixes from the keys.
    """
    if prefixes is None:
        prefixes = _detect_prefixes(list(env.keys()), separator)

    groups: Dict[str, List[str]] = {p: [] for p in prefixes}
    ungrouped: List[str] = []

    for key in sorted(env.keys()):
        matched = False
        for prefix in prefixes:
            if key.startswith(prefix):
                groups[prefix].append(key)
                matched = True
                break
        if not matched:
            ungrouped.append(key)

    sorted_env: Dict[str, str] = {}
    for prefix in prefixes:
        for key in groups[prefix]:
            sorted_env[key] = env[key]
    for key in ungrouped:
        sorted_env[key] = env[key]

    return SortResult(groups=groups, ungrouped=ungrouped, sorted_env=sorted_env)


def _detect_prefixes(keys: List[str], separator: str = "_") -> List[str]:
    """Auto-detect common prefixes that appear in more than one key."""
    counts: Dict[str, int] = {}
    for key in keys:
        if separator in key:
            prefix = key.split(separator)[0] + separator
            counts[prefix] = counts.get(prefix, 0) + 1
    return sorted(p for p, c in counts.items() if c > 1)


def sort_env(
    env: Dict[str, str],
    mode: str = "alpha",
    prefixes: Optional[List[str]] = None,
) -> SortResult:
    """Sort an env dict by the given mode ('alpha' or 'group')."""
    if mode == "group":
        return group_by_prefix(env, prefixes)
    sorted_dict = sort_alphabetically(env)
    return SortResult(
        groups={},
        ungrouped=list(sorted_dict.keys()),
        sorted_env=sorted_dict,
    )
