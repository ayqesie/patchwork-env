"""Inject key-value pairs into an existing env dict, with conflict tracking."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class InjectResult:
    injected: Dict[str, str] = field(default_factory=dict)
    skipped: Dict[str, str] = field(default_factory=dict)  # key -> existing value
    overwritten: Dict[str, Tuple[str, str]] = field(default_factory=dict)  # key -> (old, new)
    final: Dict[str, str] = field(default_factory=dict)

    def has_changes(self) -> bool:
        return bool(self.injected or self.overwritten)

    def summary(self) -> str:
        parts = []
        if self.injected:
            parts.append(f"{len(self.injected)} injected")
        if self.overwritten:
            parts.append(f"{len(self.overwritten)} overwritten")
        if self.skipped:
            parts.append(f"{len(self.skipped)} skipped")
        return ", ".join(parts) if parts else "no changes"


def inject_env(
    base: Dict[str, str],
    pairs: Dict[str, str],
    overwrite: bool = False,
    skip_existing: bool = False,
) -> InjectResult:
    """Inject key-value pairs into base env.

    Args:
        base: The original env dict.
        pairs: Key-value pairs to inject.
        overwrite: If True, overwrite existing keys with new values.
        skip_existing: If True, silently skip keys already present (no overwrite).

    Returns:
        InjectResult with tracking of what changed.
    """
    result = InjectResult(final=dict(base))

    for key, value in pairs.items():
        if key in result.final:
            if overwrite:
                result.overwritten[key] = (result.final[key], value)
                result.final[key] = value
            else:
                result.skipped[key] = result.final[key]
        else:
            result.injected[key] = value
            result.final[key] = value

    return result
