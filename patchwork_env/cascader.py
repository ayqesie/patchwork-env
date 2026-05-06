"""Cascade multiple .env files in priority order (last file wins)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class CascadeResult:
    final: Dict[str, str]
    sources: Dict[str, str]  # key -> filename that provided the winning value
    overrides: List[Tuple[str, str, str, str]]  # (key, old_val, new_val, filename)
    file_order: List[str]

    def summary(self) -> str:
        lines = [
            f"Cascaded {len(self.file_order)} file(s), {len(self.final)} total keys.",
            f"  Overrides applied: {len(self.overrides)}",
        ]
        for key, old_val, new_val, fname in self.overrides:
            lines.append(f"    {key}: {old_val!r} -> {new_val!r} (from {fname})")
        return "\n".join(lines)

    def has_overrides(self) -> bool:
        return bool(self.overrides)


def cascade_env_files(files: List[Tuple[str, Dict[str, str]]]) -> CascadeResult:
    """Merge env dicts in order; later entries override earlier ones.

    Args:
        files: list of (filename, env_dict) pairs in ascending priority order.

    Returns:
        CascadeResult with the merged env and provenance metadata.
    """
    final: Dict[str, str] = {}
    sources: Dict[str, str] = {}
    overrides: List[Tuple[str, str, str, str]] = []
    file_order = [fname for fname, _ in files]

    for fname, env in files:
        for key, value in env.items():
            if key in final and final[key] != value:
                overrides.append((key, final[key], value, fname))
            final[key] = value
            sources[key] = fname

    return CascadeResult(
        final=final,
        sources=sources,
        overrides=overrides,
        file_order=file_order,
    )
