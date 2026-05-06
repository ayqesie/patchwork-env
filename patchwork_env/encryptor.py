"""Encrypt and decrypt sensitive values in .env files using Fernet symmetric encryption."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

try:
    from cryptography.fernet import Fernet, InvalidToken
except ImportError:  # pragma: no cover
    Fernet = None  # type: ignore
    InvalidToken = Exception  # type: ignore

SENSITIVE_PATTERNS = ("password", "secret", "token", "key", "api", "auth", "private")


@dataclass
class EncryptResult:
    encrypted: Dict[str, str] = field(default_factory=dict)
    skipped: List[str] = field(default_factory=list)
    key_used: Optional[str] = None

    def has_encrypted(self) -> bool:
        return bool(self.encrypted)

    def summary(self) -> str:
        return (
            f"Encrypted {len(self.encrypted)} key(s), "
            f"skipped {len(self.skipped)} key(s)."
        )


def _is_sensitive(key: str) -> bool:
    lower = key.lower()
    return any(pat in lower for pat in SENSITIVE_PATTERNS)


def generate_key() -> str:
    if Fernet is None:
        raise RuntimeError("cryptography package is required: pip install cryptography")
    return Fernet.generate_key().decode()


def encrypt_env(
    env: Dict[str, str],
    fernet_key: str,
    sensitive_only: bool = True,
) -> EncryptResult:
    if Fernet is None:
        raise RuntimeError("cryptography package is required: pip install cryptography")
    f = Fernet(fernet_key.encode())
    result = EncryptResult(key_used=fernet_key)
    for k, v in env.items():
        if sensitive_only and not _is_sensitive(k):
            result.skipped.append(k)
            continue
        result.encrypted[k] = f.encrypt(v.encode()).decode()
    return result


def decrypt_env(
    env: Dict[str, str],
    fernet_key: str,
) -> Dict[str, str]:
    if Fernet is None:
        raise RuntimeError("cryptography package is required: pip install cryptography")
    f = Fernet(fernet_key.encode())
    out: Dict[str, str] = {}
    for k, v in env.items():
        try:
            out[k] = f.decrypt(v.encode()).decode()
        except (InvalidToken, Exception):
            out[k] = v  # leave non-encrypted values as-is
    return out
