"""masker.py — Mask env values by key pattern or explicit list."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

_DEFAULT_MASK = "***"
_SENSITIVE_PATTERNS = ("password", "secret", "token", "key", "auth", "credential", "private")


@dataclass
class MaskResult:
    original: Dict[str, str]
    masked: Dict[str, str]
    masked_keys: List[str] = field(default_factory=list)

    def summary(self) -> str:
        if not self.masked_keys:
            return "No keys masked."
        keys = ", ".join(sorted(self.masked_keys))
        return f"{len(self.masked_keys)} key(s) masked: {keys}"

    def has_masked(self) -> bool:
        return bool(self.masked_keys)


def _is_sensitive(key: str) -> bool:
    lower = key.lower()
    return any(pat in lower for pat in _SENSITIVE_PATTERNS)


def mask_env(
    env: Dict[str, str],
    keys: Optional[List[str]] = None,
    auto_detect: bool = True,
    mask_value: str = _DEFAULT_MASK,
) -> MaskResult:
    """Return a copy of *env* with sensitive values replaced by *mask_value*.

    Args:
        env: Parsed env dict.
        keys: Explicit list of keys to mask regardless of name.
        auto_detect: If True, also mask keys whose names match common sensitive
            patterns (password, token, secret, etc.).
        mask_value: Replacement string (default ``***``).
    """
    explicit = set(keys or [])
    masked_out: Dict[str, str] = {}
    masked_keys: List[str] = []

    for k, v in env.items():
        if k in explicit or (auto_detect and _is_sensitive(k)):
            masked_out[k] = mask_value
            masked_keys.append(k)
        else:
            masked_out[k] = v

    return MaskResult(original=dict(env), masked=masked_out, masked_keys=masked_keys)
