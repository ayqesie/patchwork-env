"""Generates a human-readable diff summary report across multiple env files."""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from patchwork_env.differ import EnvDiff, diff_envs
from patchwork_env.parser import parse_env_file


@dataclass
class MultiDiffReport:
    comparisons: List[Tuple[str, str, EnvDiff]] = field(default_factory=list)

    def total_pairs(self) -> int:
        return len(self.comparisons)

    def pairs_with_diff(self) -> int:
        return sum(1 for _, _, d in self.comparisons if d.added or d.removed or d.changed)

    def all_changed_keys(self) -> Dict[str, int]:
        """Return a count of how many times each key changed across all pairs."""
        counts: Dict[str, int] = {}
        for _, _, d in self.comparisons:
            for key in list(d.added) + list(d.removed) + list(d.changed):
                counts[key] = counts.get(key, 0) + 1
        return counts

    def summary(self) -> str:
        lines = [
            f"Multi-env diff report: {self.total_pairs()} pair(s), "
            f"{self.pairs_with_diff()} with differences"
        ]
        for base_name, target_name, d in self.comparisons:
            added = len(d.added)
            removed = len(d.removed)
            changed = len(d.changed)
            unchanged = len(d.unchanged)
            lines.append(
                f"  {base_name} -> {target_name}: "
                f"+{added} -{removed} ~{changed} ={unchanged}"
            )
        return "\n".join(lines)


def build_multi_diff(file_pairs: List[Tuple[str, str]]) -> MultiDiffReport:
    """Build a MultiDiffReport from a list of (base_path, target_path) tuples."""
    report = MultiDiffReport()
    for base_path, target_path in file_pairs:
        base_env = parse_env_file(base_path)
        target_env = parse_env_file(target_path)
        d = diff_envs(base_env, target_env)
        report.comparisons.append((base_path, target_path, d))
    return report
