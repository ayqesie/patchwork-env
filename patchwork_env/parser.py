"""Parser for .env files — handles reading and tokenizing key-value pairs."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Optional


ENV_LINE_RE = re.compile(
    r"^\s*(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)\s*$"
)
COMMENT_RE = re.compile(r"^\s*#")


def parse_env_file(path: str | Path) -> Dict[str, str]:
    """Read an .env file and return a dict of key -> value pairs.

    - Ignores blank lines and comment lines (starting with #).
    - Strips surrounding quotes from values.
    - Raises FileNotFoundError if the path does not exist.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"env file not found: {path}")

    env: Dict[str, str] = {}
    for lineno, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or COMMENT_RE.match(line):
            continue
        match = ENV_LINE_RE.match(line)
        if not match:
            raise ValueError(f"Invalid syntax at {path}:{lineno} — {raw_line!r}")
        key = match.group("key")
        value = _strip_quotes(match.group("value"))
        env[key] = value
    return env


def _strip_quotes(value: str) -> str:
    """Remove matching surrounding single or double quotes from a value."""
    for quote in ('"', "'"):
        if value.startswith(quote) and value.endswith(quote) and len(value) >= 2:
            return value[1:-1]
    return value


def parse_env_string(content: str) -> Dict[str, str]:
    """Parse an .env-formatted string directly (useful for testing)."""
    import tempfile, os
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False, encoding="utf-8") as f:
        f.write(content)
        tmp_path = f.name
    try:
        return parse_env_file(tmp_path)
    finally:
        os.unlink(tmp_path)
