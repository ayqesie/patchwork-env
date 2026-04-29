"""Filter env dicts by key patterns, prefixes, or value conditions."""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FilterResult:
    matched: Dict[str, str] = field(default_factory=dict)
    excluded: Dict[str, str] = field(default_factory=dict)

    def summary(self) -> str:
        return (
            f"{len(self.matched)} key(s) matched, "
            f"{len(self.excluded)} key(s) excluded"
        )

    def has_matches(self) -> bool:
        return bool(self.matched)


def filter_env(
    env: Dict[str, str],
    *,
    include_patterns: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None,
    prefix: Optional[str] = None,
    value_pattern: Optional[str] = None,
    empty_only: bool = False,
    nonempty_only: bool = False,
) -> FilterResult:
    """Return a FilterResult partitioning env keys into matched/excluded."""
    result = FilterResult()

    for key, value in env.items():
        if prefix and not key.startswith(prefix):
            result.excluded[key] = value
            continue

        if include_patterns and not any(
            fnmatch.fnmatch(key, p) for p in include_patterns
        ):
            result.excluded[key] = value
            continue

        if exclude_patterns and any(
            fnmatch.fnmatch(key, p) for p in exclude_patterns
        ):
            result.excluded[key] = value
            continue

        if value_pattern and not re.search(value_pattern, value):
            result.excluded[key] = value
            continue

        if empty_only and value.strip() != "":
            result.excluded[key] = value
            continue

        if nonempty_only and value.strip() == "":
            result.excluded[key] = value
            continue

        result.matched[key] = value

    return result
