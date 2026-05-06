"""Profile an env file: count keys, detect patterns, summarize value types."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List


_PLACEHOLDER_PATTERNS = re.compile(
    r"^(CHANGE_?ME|TODO|FIXME|PLACEHOLDER|YOUR_.*|<.*>|\.\.\.)$", re.IGNORECASE
)
_URL_PATTERN = re.compile(r"^https?://", re.IGNORECASE)
_NUMERIC_PATTERN = re.compile(r"^-?\d+(\.\d+)?$")
_BOOL_PATTERN = re.compile(r"^(true|false|yes|no|1|0)$", re.IGNORECASE)


@dataclass
class EnvProfile:
    total_keys: int = 0
    empty_values: List[str] = field(default_factory=list)
    placeholder_values: List[str] = field(default_factory=list)
    url_values: List[str] = field(default_factory=list)
    numeric_values: List[str] = field(default_factory=list)
    boolean_values: List[str] = field(default_factory=list)
    long_values: List[str] = field(default_factory=list)  # > 100 chars
    type_counts: Dict[str, int] = field(default_factory=dict)

    def summary(self) -> str:
        lines = [
            f"Total keys     : {self.total_keys}",
            f"Empty values   : {len(self.empty_values)}",
            f"Placeholders   : {len(self.placeholder_values)}",
            f"URLs           : {len(self.url_values)}",
            f"Numeric        : {len(self.numeric_values)}",
            f"Boolean        : {len(self.boolean_values)}",
            f"Long values    : {len(self.long_values)}",
        ]
        return "\n".join(lines)

    def keys_needing_attention(self) -> List[str]:
        """Return keys that are empty or still have placeholder values.

        These are the most likely candidates to be filled in before
        deploying, so it's handy to have them in one place.
        """
        return sorted(set(self.empty_values) | set(self.placeholder_values))


def profile_env(env: Dict[str, str]) -> EnvProfile:
    """Analyse an env dict and return an EnvProfile."""
    p = EnvProfile(total_keys=len(env))

    for key, value in env.items():
        if value == "":
            p.empty_values.append(key)
        elif _PLACEHOLDER_PATTERNS.match(value):
            p.placeholder_values.append(key)
        elif _URL_PATTERN.match(value):
            p.url_values.append(key)
        elif _NUMERIC_PATTERN.match(value):
            p.numeric_values.append(key)
        elif _BOOL_PATTERN.match(value):
            p.boolean_values.append(key)

        if len(value) > 100:
            p.long_values.append(key)

    p.type_counts = {
        "empty": len(p.empty_values),
        "placeholder": len(p.placeholder_values),
        "url": len(p.url_values),
        "numeric": len(p.numeric_values),
        "boolean": len(p.boolean_values),
        "other": p.total_keys
        - len(p.empty_values)
        - len(p.placeholder_values)
        - len(p.url_values)
        - len(p.numeric_values)
        - len(p.boolean_values),
    }

    return p
