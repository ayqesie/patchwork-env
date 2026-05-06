"""Detect and report deprecated keys in an env file based on a deprecation map."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DeprecateResult:
    deprecated: Dict[str, Optional[str]] = field(default_factory=dict)  # old_key -> suggested replacement
    clean: List[str] = field(default_factory=list)

    def has_issues(self) -> bool:
        return bool(self.deprecated)

    def summary(self) -> str:
        if not self.deprecated:
            return "No deprecated keys found."
        lines = [f"Found {len(self.deprecated)} deprecated key(s):"]
        for key, replacement in self.deprecated.items():
            if replacement:
                lines.append(f"  - {key}  ->  use '{replacement}' instead")
            else:
                lines.append(f"  - {key}  (no replacement suggested)")
        return "\n".join(lines)

    def all_deprecated_keys(self) -> List[str]:
        return list(self.deprecated.keys())

    def keys_with_replacements(self) -> Dict[str, str]:
        """Return only deprecated keys that have a suggested replacement."""
        return {key: repl for key, repl in self.deprecated.items() if repl is not None}


def deprecate_env(
    env: Dict[str, str],
    deprecation_map: Dict[str, Optional[str]],
) -> DeprecateResult:
    """Check env dict against a deprecation map.

    Args:
        env: Parsed environment key/value pairs.
        deprecation_map: Mapping of deprecated key -> replacement key (or None).

    Returns:
        DeprecateResult with deprecated and clean keys categorised.
    """
    result = DeprecateResult()
    for key in env:
        if key in deprecation_map:
            result.deprecated[key] = deprecation_map[key]
        else:
            result.clean.append(key)
    return result
