"""aliaser.py — map env keys to human-friendly aliases and resolve them back."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class AliasResult:
    resolved: Dict[str, str] = field(default_factory=dict)
    not_found: list[str] = field(default_factory=list)
    alias_map: Dict[str, str] = field(default_factory=dict)  # alias -> canonical key

    def has_issues(self) -> bool:
        return bool(self.not_found)

    def summary(self) -> str:
        lines = [
            f"Resolved : {len(self.resolved)}",
            f"Not found: {len(self.not_found)}",
        ]
        if self.not_found:
            lines.append("Missing aliases: " + ", ".join(sorted(self.not_found)))
        return "\n".join(lines)

    def canonical_for(self, alias: str) -> Optional[str]:
        """Return the canonical key name for a given alias, or None."""
        return self.alias_map.get(alias)


def alias_env(
    env: Dict[str, str],
    alias_map: Dict[str, str],
    *,
    include_originals: bool = False,
) -> AliasResult:
    """Build an aliased view of *env* using *alias_map* (alias -> canonical key).

    Args:
        env: The source environment dict.
        alias_map: Mapping of alias name -> canonical key in *env*.
        include_originals: If True, also keep original key/value pairs in resolved.

    Returns:
        AliasResult with resolved aliases and any missing canonical keys.
    """
    resolved: Dict[str, str] = {}
    not_found: list[str] = []

    if include_originals:
        resolved.update(env)

    for alias, canonical in alias_map.items():
        if canonical in env:
            resolved[alias] = env[canonical]
        else:
            not_found.append(alias)

    return AliasResult(
        resolved=resolved,
        not_found=not_found,
        alias_map=dict(alias_map),
    )


def invert_aliases(alias_map: Dict[str, str]) -> Dict[str, str]:
    """Flip alias->canonical to canonical->alias for reverse lookup."""
    return {canonical: alias for alias, canonical in alias_map.items()}
