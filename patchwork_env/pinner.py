"""Pin env keys to specific values, producing a locked snapshot of selected keys."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PinResult:
    pinned: Dict[str, str] = field(default_factory=dict)
    skipped: List[str] = field(default_factory=list)
    not_found: List[str] = field(default_factory=list)

    def has_pins(self) -> bool:
        return bool(self.pinned)

    def summary(self) -> str:
        parts = [f"{len(self.pinned)} pinned"]
        if self.skipped:
            parts.append(f"{len(self.skipped)} skipped (already match)")
        if self.not_found:
            parts.append(f"{len(self.not_found)} not found")
        return ", ".join(parts)


def pin_keys(
    env: Dict[str, str],
    pins: Dict[str, str],
    skip_if_match: bool = False,
) -> PinResult:
    """Apply pinned values to an env dict.

    Args:
        env: The source environment dict.
        pins: Mapping of key -> pinned value to enforce.
        skip_if_match: If True, skip keys where the current value already matches.

    Returns:
        PinResult with the resulting pinned env, skipped keys, and not-found keys.
    """
    result = PinResult()

    for key, pinned_value in pins.items():
        if key not in env:
            result.not_found.append(key)
            continue

        current_value = env[key]
        if skip_if_match and current_value == pinned_value:
            result.skipped.append(key)
            continue

        result.pinned[key] = pinned_value

    return result


def apply_pins(
    env: Dict[str, str],
    pin_result: PinResult,
) -> Dict[str, str]:
    """Return a new env dict with pinned values applied."""
    merged = dict(env)
    merged.update(pin_result.pinned)
    return merged
