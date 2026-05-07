"""Promote env values from one environment to another with optional key filtering."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PromoteResult:
    promoted: Dict[str, str] = field(default_factory=dict)
    skipped: Dict[str, str] = field(default_factory=dict)
    not_found: List[str] = field(default_factory=list)
    overwritten: Dict[str, tuple] = field(default_factory=dict)  # key -> (old, new)

    def has_changes(self) -> bool:
        return bool(self.promoted)

    def summary(self) -> str:
        lines = [
            f"Promoted : {len(self.promoted)}",
            f"Skipped  : {len(self.skipped)}",
            f"Not found: {len(self.not_found)}",
            f"Overwritten: {len(self.overwritten)}",
        ]
        return "\n".join(lines)


def promote_env(
    source: Dict[str, str],
    target: Dict[str, str],
    keys: Optional[List[str]] = None,
    overwrite: bool = False,
    prefix: Optional[str] = None,
) -> PromoteResult:
    """Promote values from source into target.

    Args:
        source: The environment to pull values from.
        target: The environment to promote values into.
        keys: Explicit list of keys to promote. If None, promote all source keys.
        overwrite: If True, overwrite existing keys in target.
        prefix: If set, only promote keys starting with this prefix.
    """
    result = PromoteResult()
    candidate_keys = keys if keys is not None else list(source.keys())

    if prefix:
        candidate_keys = [k for k in candidate_keys if k.startswith(prefix)]

    merged = dict(target)

    for key in candidate_keys:
        if key not in source:
            result.not_found.append(key)
            continue

        value = source[key]

        if key in target:
            if overwrite:
                result.overwritten[key] = (target[key], value)
                merged[key] = value
                result.promoted[key] = value
            else:
                result.skipped[key] = value
        else:
            merged[key] = value
            result.promoted[key] = value

    result.promoted = {k: merged[k] for k in result.promoted}
    return result
