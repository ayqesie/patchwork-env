"""Trim leading/trailing whitespace from .env values and optionally keys."""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class TrimResult:
    original: Dict[str, str]
    trimmed: Dict[str, str]
    changes: List[Tuple[str, str, str]] = field(default_factory=list)  # (key, before, after)

    def has_changes(self) -> bool:
        return len(self.changes) > 0

    def summary(self) -> str:
        if not self.has_changes():
            return "No whitespace issues found."
        lines = [f"Trimmed {len(self.changes)} value(s):"]
        for key, before, after in self.changes:
            lines.append(f"  {key}: {repr(before)} -> {repr(after)}")
        return "\n".join(lines)


def trim_env(
    env: Dict[str, str],
    trim_keys: bool = False,
) -> TrimResult:
    """Trim whitespace from env values (and optionally keys).

    Args:
        env: Parsed env dict.
        trim_keys: If True, also strip whitespace from key names.

    Returns:
        TrimResult with original, trimmed dict, and list of changes.
    """
    trimmed: Dict[str, str] = {}
    changes: List[Tuple[str, str, str]] = []

    for raw_key, raw_value in env.items():
        key = raw_key.strip() if trim_keys else raw_key
        value = raw_value.strip()

        trimmed[key] = value

        value_changed = value != raw_value
        key_changed = key != raw_key

        if value_changed or key_changed:
            display_key = key if not key_changed else f"{raw_key} -> {key}"
            changes.append((display_key, raw_value, value))

    return TrimResult(original=dict(env), trimmed=trimmed, changes=changes)


def to_trimmed_string(result: TrimResult) -> str:
    """Serialize a TrimResult's trimmed dict back to .env format."""
    lines = []
    for key, value in result.trimmed.items():
        if " " in value or "#" in value:
            lines.append(f'{key}="{value}"')
        else:
            lines.append(f"{key}={value}")
    return "\n".join(lines)
