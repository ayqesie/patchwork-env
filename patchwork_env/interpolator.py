"""Variable interpolation for .env files.

Supports ${VAR} and $VAR style references within values.
"""

from __future__ import annotations

import re
from typing import Dict, Optional

_BRACE_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")
_BARE_RE = re.compile(r"\$([A-Za-z_][A-Za-z0-9_]*)")


def interpolate(env: Dict[str, str], max_passes: int = 10) -> Dict[str, str]:
    """Return a new env dict with variable references resolved.

    Performs repeated passes until stable or *max_passes* is reached.
    Unresolvable references are left as-is.

    Args:
        env: Flat mapping of key -> raw value.
        max_passes: Safety limit to prevent infinite loops.

    Returns:
        New dict with interpolated values.
    """
    result = dict(env)
    for _ in range(max_passes):
        changed = False
        for key, value in result.items():
            new_value = _resolve(value, result)
            if new_value != value:
                result[key] = new_value
                changed = True
        if not changed:
            break
    return result


def _resolve(value: str, env: Dict[str, str]) -> str:
    """Expand all variable references in *value* using *env*."""
    value = _BRACE_RE.sub(lambda m: env.get(m.group(1), m.group(0)), value)
    value = _BARE_RE.sub(lambda m: env.get(m.group(1), m.group(0)), value)
    return value


def find_references(value: str) -> list[str]:
    """Return all variable names referenced in *value*."""
    brace_refs = _BRACE_RE.findall(value)
    bare_refs = _BARE_RE.findall(value)
    seen: list[str] = []
    for name in brace_refs + bare_refs:
        if name not in seen:
            seen.append(name)
    return seen


def unresolved_keys(env: Dict[str, str]) -> Dict[str, list[str]]:
    """Return keys whose values still contain unresolvable references.

    Returns a mapping of key -> list of missing variable names.
    """
    resolved = interpolate(env)
    missing: Dict[str, list[str]] = {}
    for key, value in resolved.items():
        refs = find_references(value)
        if refs:
            missing[key] = refs
    return missing
