"""Redact sensitive values from env dicts before display or export."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

# Patterns in key names that suggest sensitive data
_SENSITIVE_PATTERNS: List[re.Pattern] = [
    re.compile(r"(password|passwd|pwd)", re.IGNORECASE),
    re.compile(r"(secret|token|api_key|apikey)", re.IGNORECASE),
    re.compile(r"(private_key|privkey)", re.IGNORECASE),
    re.compile(r"(auth|credential|cert)", re.IGNORECASE),
    re.compile(r"(dsn|database_url|db_url)", re.IGNORECASE),
]

REDACT_PLACEHOLDER = "***REDACTED***"


@dataclass
class RedactResult:
    redacted: Dict[str, str]
    redacted_keys: List[str] = field(default_factory=list)

    def summary(self) -> str:
        if not self.redacted_keys:
            return "No sensitive keys detected."
        keys = ", ".join(sorted(self.redacted_keys))
        return f"Redacted {len(self.redacted_keys)} sensitive key(s): {keys}"


def is_sensitive_key(key: str) -> bool:
    """Return True if the key name matches any sensitive pattern."""
    return any(p.search(key) for p in _SENSITIVE_PATTERNS)


def redact_env(
    env: Dict[str, str],
    extra_keys: List[str] | None = None,
    placeholder: str = REDACT_PLACEHOLDER,
) -> RedactResult:
    """Return a copy of *env* with sensitive values replaced by *placeholder*.

    Args:
        env: The parsed env dict to redact.
        extra_keys: Additional key names to force-redact regardless of pattern.
        placeholder: Replacement string for redacted values.
    """
    extra = set(k.upper() for k in (extra_keys or []))
    redacted: Dict[str, str] = {}
    flagged: List[str] = []

    for key, value in env.items():
        if is_sensitive_key(key) or key.upper() in extra:
            redacted[key] = placeholder
            flagged.append(key)
        else:
            redacted[key] = value

    return RedactResult(redacted=redacted, redacted_keys=flagged)
