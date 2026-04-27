"""Rename keys across an env dict, with tracking of what changed."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class RenameResult:
    renamed: List[Tuple[str, str]] = field(default_factory=list)   # (old, new)
    skipped: List[str] = field(default_factory=list)               # old key not found
    conflicts: List[str] = field(default_factory=list)             # new key already exists
    env: Dict[str, str] = field(default_factory=dict)

    def has_issues(self) -> bool:
        return bool(self.skipped or self.conflicts)

    def summary(self) -> str:
        parts = [f"{len(self.renamed)} renamed"]
        if self.skipped:
            parts.append(f"{len(self.skipped)} not found")
        if self.conflicts:
            parts.append(f"{len(self.conflicts)} conflicts")
        return ", ".join(parts)


def rename_keys(
    env: Dict[str, str],
    renames: Dict[str, str],
    overwrite: bool = False,
) -> RenameResult:
    """Apply a mapping of {old_key: new_key} to *env*.

    Args:
        env:       The source environment dict.
        renames:   Mapping of old key names to new key names.
        overwrite: If True, overwrite the new key even if it already exists.

    Returns:
        A RenameResult with the updated env and metadata.
    """
    result_env = dict(env)
    renamed: List[Tuple[str, str]] = []
    skipped: List[str] = []
    conflicts: List[str] = []

    for old, new in renames.items():
        if old not in result_env:
            skipped.append(old)
            continue

        if new in result_env and not overwrite:
            conflicts.append(new)
            continue

        result_env[new] = result_env.pop(old)
        renamed.append((old, new))

    return RenameResult(
        renamed=renamed,
        skipped=skipped,
        conflicts=conflicts,
        env=result_env,
    )
