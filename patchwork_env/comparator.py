"""Compare two .env files and produce a structured similarity report."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Set

from patchwork_env.parser import parse_env_file


@dataclass
class CompareResult:
    base_path: str
    target_path: str
    shared_keys: Set[str] = field(default_factory=set)
    base_only_keys: Set[str] = field(default_factory=set)
    target_only_keys: Set[str] = field(default_factory=set)
    matching_pairs: Dict[str, str] = field(default_factory=dict)
    differing_pairs: Dict[str, tuple] = field(default_factory=dict)  # key -> (base_val, target_val)

    @property
    def similarity_score(self) -> float:
        """Return a 0.0-1.0 score based on key and value overlap."""
        all_keys = self.shared_keys | self.base_only_keys | self.target_only_keys
        if not all_keys:
            return 1.0
        return len(self.matching_pairs) / len(all_keys)

    def has_diff(self) -> bool:
        return bool(self.base_only_keys or self.target_only_keys or self.differing_pairs)

    def summary(self) -> str:
        score_pct = f"{self.similarity_score * 100:.1f}%"
        return (
            f"Similarity: {score_pct} | "
            f"Matching: {len(self.matching_pairs)} | "
            f"Differing: {len(self.differing_pairs)} | "
            f"Base-only: {len(self.base_only_keys)} | "
            f"Target-only: {len(self.target_only_keys)}"
        )


def compare_env_files(base_path: str, target_path: str) -> CompareResult:
    """Load two env files from disk and compare them."""
    base = parse_env_file(base_path)
    target = parse_env_file(target_path)
    return compare_env_dicts(base, target, base_path=base_path, target_path=target_path)


def compare_env_dicts(
    base: Dict[str, str],
    target: Dict[str, str],
    base_path: str = "<base>",
    target_path: str = "<target>",
) -> CompareResult:
    """Compare two env dicts and return a CompareResult."""
    base_keys = set(base)
    target_keys = set(target)
    shared = base_keys & target_keys

    matching: Dict[str, str] = {}
    differing: Dict[str, tuple] = {}

    for key in shared:
        if base[key] == target[key]:
            matching[key] = base[key]
        else:
            differing[key] = (base[key], target[key])

    return CompareResult(
        base_path=base_path,
        target_path=target_path,
        shared_keys=shared,
        base_only_keys=base_keys - target_keys,
        target_only_keys=target_keys - base_keys,
        matching_pairs=matching,
        differing_pairs=differing,
    )
