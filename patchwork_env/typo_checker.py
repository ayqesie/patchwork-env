"""Detect potential typos in .env keys by comparing against a reference set."""

from __future__ import annotations

from dataclasses import dataclass, field
from difflib import get_close_matches
from typing import Dict, List, Optional


@dataclass
class TypoResult:
    suggestions: Dict[str, List[str]] = field(default_factory=dict)
    checked: int = 0
    reference_count: int = 0

    def has_suggestions(self) -> bool:
        return bool(self.suggestions)

    def summary(self) -> str:
        if not self.has_suggestions():
            return f"No typos detected ({self.checked} keys checked)."
        lines = [f"{len(self.suggestions)} possible typo(s) found:"]
        for key, matches in self.suggestions.items():
            lines.append(f"  {key!r} -> did you mean: {', '.join(matches)}?")
        return "\n".join(lines)

    def all_suspect_keys(self) -> List[str]:
        return list(self.suggestions.keys())


def check_typos(
    env: Dict[str, str],
    reference: Dict[str, str],
    cutoff: float = 0.8,
    n: int = 3,
) -> TypoResult:
    """Compare keys in *env* against *reference* keys and flag close-but-not-exact matches."""
    ref_keys = list(reference.keys())
    result = TypoResult(checked=len(env), reference_count=len(ref_keys))

    for key in env:
        if key in reference:
            continue  # exact match — not a typo
        matches = get_close_matches(key, ref_keys, n=n, cutoff=cutoff)
        if matches:
            result.suggestions[key] = matches

    return result


def check_typos_against_keys(
    env: Dict[str, str],
    reference_keys: List[str],
    cutoff: float = 0.8,
    n: int = 3,
) -> TypoResult:
    """Convenience wrapper when only a list of reference key names is available."""
    reference = {k: "" for k in reference_keys}
    return check_typos(env, reference, cutoff=cutoff, n=n)
