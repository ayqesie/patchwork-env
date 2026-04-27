"""Detect and report duplicate keys within a single .env file."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DuplicateResult:
    duplicates: Dict[str, List[str]] = field(default_factory=dict)

    def has_issues(self) -> bool:
        return bool(self.duplicates)

    def summary(self) -> str:
        if not self.has_issues():
            return "No duplicate keys found."
        lines = ["Duplicate keys detected:"]
        for key, values in self.duplicates.items():
            lines.append(f"  {key}: {values}")
        return "\n".join(lines)

    def all_duplicate_keys(self) -> List[str]:
        return list(self.duplicates.keys())


def find_duplicates(env_text: str) -> DuplicateResult:
    """Parse raw .env text and find keys that appear more than once."""
    seen: Dict[str, List[str]] = {}

    for raw_line in env_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        seen.setdefault(key, []).append(value)

    duplicates = {k: v for k, v in seen.items() if len(v) > 1}
    return DuplicateResult(duplicates=duplicates)
