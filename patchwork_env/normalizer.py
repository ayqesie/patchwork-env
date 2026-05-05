"""Normalize .env file keys and values to a consistent style."""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class NormalizeResult:
    original: Dict[str, str]
    normalized: Dict[str, str]
    changes: List[Tuple[str, str, str]] = field(default_factory=list)  # (key, old, new)

    def has_changes(self) -> bool:
        return len(self.changes) > 0

    def summary(self) -> str:
        if not self.has_changes():
            return "No normalization changes needed."
        lines = [f"Normalized {len(self.changes)} value(s):"]
        for key, old, new in self.changes:
            lines.append(f"  {key}: {old!r} -> {new!r}")
        return "\n".join(lines)


def _normalize_value(value: str, rules: List[str]) -> str:
    """Apply normalization rules to a single value."""
    result = value
    if "strip" in rules:
        result = result.strip()
    if "strip_quotes" in rules:
        for q in ('"', "'"):
            if result.startswith(q) and result.endswith(q) and len(result) >= 2:
                result = result[1:-1]
                break
    if "lowercase" in rules:
        result = result.lower()
    if "uppercase" in rules:
        result = result.upper()
    return result


def normalize_env(
    env: Dict[str, str],
    key_case: str = "upper",
    value_rules: List[str] = None,
) -> NormalizeResult:
    """
    Normalize env keys and/or values.

    Args:
        env: The parsed env dict.
        key_case: 'upper', 'lower', or 'preserve'.
        value_rules: List of rules to apply to values.
                     Supported: 'strip', 'strip_quotes', 'lowercase', 'uppercase'.
    """
    if value_rules is None:
        value_rules = ["strip"]

    normalized: Dict[str, str] = {}
    changes: List[Tuple[str, str, str]] = []

    for key, value in env.items():
        # Normalize key
        if key_case == "upper":
            new_key = key.upper()
        elif key_case == "lower":
            new_key = key.lower()
        else:
            new_key = key

        # Normalize value
        new_value = _normalize_value(value, value_rules)

        if new_key != key or new_value != value:
            changes.append((new_key, value, new_value))

        normalized[new_key] = new_value

    return NormalizeResult(original=env, normalized=normalized, changes=changes)
