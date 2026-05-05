"""Pinpointer: locate which environments contain a specific key or value."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PinpointResult:
    key: str
    matches: Dict[str, str] = field(default_factory=dict)  # env_label -> value
    missing_from: List[str] = field(default_factory=list)

    def found_in(self) -> List[str]:
        return list(self.matches.keys())

    def has_matches(self) -> bool:
        return bool(self.matches)

    def is_consistent(self) -> bool:
        """True if the key exists in all envs and has the same value everywhere."""
        if not self.matches:
            return False
        return len(set(self.matches.values())) == 1 and not self.missing_from

    def summary(self) -> str:
        parts = [f"Key '{self.key}':"]
        for label, value in self.matches.items():
            parts.append(f"  {label}: {value!r}")
        for label in self.missing_from:
            parts.append(f"  {label}: <missing>")
        if self.is_consistent():
            parts.append("  [consistent across all environments]")
        return "\n".join(parts)


def pinpoint_key(
    key: str,
    envs: Dict[str, Dict[str, str]],
    value_filter: Optional[str] = None,
) -> PinpointResult:
    """Search for a key across multiple named env dicts.

    Args:
        key: The environment variable name to look up.
        envs: Mapping of label -> parsed env dict.
        value_filter: If provided, only include envs where the value equals this.

    Returns:
        PinpointResult with match and missing information.
    """
    result = PinpointResult(key=key)
    for label, env in envs.items():
        if key in env:
            value = env[key]
            if value_filter is None or value == value_filter:
                result.matches[label] = value
            else:
                result.missing_from.append(label)
        else:
            result.missing_from.append(label)
    return result


def pinpoint_value(
    value: str,
    envs: Dict[str, Dict[str, str]],
) -> Dict[str, List[str]]:
    """Find all keys across all envs that hold a specific value.

    Returns:
        Mapping of env_label -> list of keys with that value.
    """
    hits: Dict[str, List[str]] = {}
    for label, env in envs.items():
        matched = [k for k, v in env.items() if v == value]
        if matched:
            hits[label] = matched
    return hits
