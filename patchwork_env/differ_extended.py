"""Extended diff utilities: key overlap stats and value similarity."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from patchwork_env.differ import EnvDiff


@dataclass
class DiffStats:
    total_base: int = 0
    total_target: int = 0
    added: int = 0
    removed: int = 0
    changed: int = 0
    unchanged: int = 0
    overlap_ratio: float = 0.0
    change_ratio: float = 0.0
    similar_values: List[Tuple[str, str, str]] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            f"Base keys     : {self.total_base}",
            f"Target keys   : {self.total_target}",
            f"Added         : {self.added}",
            f"Removed       : {self.removed}",
            f"Changed       : {self.changed}",
            f"Unchanged     : {self.unchanged}",
            f"Overlap ratio : {self.overlap_ratio:.1%}",
            f"Change ratio  : {self.change_ratio:.1%}",
        ]
        return "\n".join(lines)


def _value_similarity(a: str, b: str) -> float:
    """Simple character-overlap similarity in [0, 1]."""
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    longer = max(len(a), len(b))
    matches = sum(ca == cb for ca, cb in zip(a, b))
    return matches / longer


def compute_diff_stats(
    diff: EnvDiff,
    base: Dict[str, str],
    target: Dict[str, str],
    similarity_threshold: float = 0.8,
) -> DiffStats:
    """Compute extended statistics from an EnvDiff."""
    stats = DiffStats(
        total_base=len(base),
        total_target=len(target),
        added=len(diff.added),
        removed=len(diff.removed),
        changed=len(diff.changed),
        unchanged=len(diff.unchanged),
    )

    all_keys = set(base) | set(target)
    shared = set(base) & set(target)
    stats.overlap_ratio = len(shared) / len(all_keys) if all_keys else 0.0

    total_shared = len(shared)
    stats.change_ratio = len(diff.changed) / total_shared if total_shared else 0.0

    for key, (base_val, target_val) in diff.changed.items():
        score = _value_similarity(base_val, target_val)
        if score >= similarity_threshold:
            stats.similar_values.append((key, base_val, target_val))

    return stats
