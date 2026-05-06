"""Freeze an env dict — mark keys as immutable and detect drift from a frozen baseline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FreezeResult:
    frozen_keys: List[str] = field(default_factory=list)
    drifted_keys: Dict[str, tuple] = field(default_factory=dict)  # key -> (frozen_val, current_val)
    unfrozen_keys: List[str] = field(default_factory=list)

    def has_drift(self) -> bool:
        return bool(self.drifted_keys)

    def summary(self) -> str:
        lines = [
            f"Frozen keys   : {len(self.frozen_keys)}",
            f"Drifted keys  : {len(self.drifted_keys)}",
            f"Unfrozen keys : {len(self.unfrozen_keys)}",
        ]
        if self.drifted_keys:
            lines.append("Drift detected:")
            for key, (frozen_val, current_val) in self.drifted_keys.items():
                lines.append(f"  {key}: {frozen_val!r} -> {current_val!r}")
        return "\n".join(lines)


def freeze_env(
    env: Dict[str, str],
    keys: Optional[List[str]] = None,
) -> tuple[Dict[str, str], FreezeResult]:
    """Return a frozen snapshot dict and a FreezeResult describing what was frozen."""
    target_keys = keys if keys is not None else list(env.keys())
    result = FreezeResult()
    frozen: Dict[str, str] = {}

    for key in target_keys:
        if key in env:
            frozen[key] = env[key]
            result.frozen_keys.append(key)
        # keys not in env are silently skipped

    result.unfrozen_keys = [k for k in env if k not in frozen]
    return frozen, result


def check_drift(
    frozen: Dict[str, str],
    current: Dict[str, str],
) -> FreezeResult:
    """Compare a frozen baseline against a current env and report any drift."""
    result = FreezeResult(frozen_keys=list(frozen.keys()))

    for key, frozen_val in frozen.items():
        current_val = current.get(key)
        if current_val is None:
            result.drifted_keys[key] = (frozen_val, "<missing>")
        elif current_val != frozen_val:
            result.drifted_keys[key] = (frozen_val, current_val)

    result.unfrozen_keys = [k for k in current if k not in frozen]
    return result
