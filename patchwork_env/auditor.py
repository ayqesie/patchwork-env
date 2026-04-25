"""Audit env files for common issues like empty values, duplicate keys, and suspicious patterns."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class AuditResult:
    empty_values: List[str] = field(default_factory=list)
    duplicate_keys: List[str] = field(default_factory=list)
    suspicious_values: List[str] = field(default_factory=list)
    placeholder_values: List[str] = field(default_factory=list)

    def has_issues(self) -> bool:
        return bool(
            self.empty_values
            or self.duplicate_keys
            or self.suspicious_values
            or self.placeholder_values
        )

    def summary(self) -> str:
        parts = []
        if self.empty_values:
            parts.append(f"{len(self.empty_values)} empty value(s)")
        if self.duplicate_keys:
            parts.append(f"{len(self.duplicate_keys)} duplicate key(s)")
        if self.suspicious_values:
            parts.append(f"{len(self.suspicious_values)} suspicious value(s)")
        if self.placeholder_values:
            parts.append(f"{len(self.placeholder_values)} placeholder value(s)")
        return ", ".join(parts) if parts else "no issues found"

    def all_flagged_keys(self) -> List[str]:
        """Return a deduplicated list of all keys that have any issue."""
        seen = set()
        result = []
        for key in (
            self.empty_values
            + self.duplicate_keys
            + self.suspicious_values
            + self.placeholder_values
        ):
            if key not in seen:
                seen.add(key)
                result.append(key)
        return result


_PLACEHOLDER_PATTERNS = (
    "changeme",
    "todo",
    "fixme",
    "your_",
    "<",
    ">",
    "example",
    "placeholder",
)


def audit_env(env: Dict[str, str], raw_lines: List[str] = None) -> AuditResult:
    result = AuditResult()

    for key, value in env.items():
        if value == "":
            result.empty_values.append(key)
        lower_val = value.lower()
        if any(p in lower_val for p in _PLACEHOLDER_PATTERNS):
            result.placeholder_values.append(key)
        if "password" in key.lower() and len(value) < 8 and value != "":
            result.suspicious_values.append(key)

    if raw_lines is not None:
        seen_keys = []
        for line in raw_lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "=" in stripped:
                key = stripped.split("=", 1)[0].strip()
                if key in seen_keys:
                    if key not in result.duplicate_keys:
                        result.duplicate_keys.append(key)
                else:
                    seen_keys.append(key)

    return result
