"""Add, remove, or extract inline comments from .env files."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


_COMMENT_RE = re.compile(r'^([^=]+=[^#]*)\s+#\s*(.+)$')
_INLINE_STRIP_RE = re.compile(r'\s+#.*$')


@dataclass
class CommentResult:
    comments: Dict[str, str] = field(default_factory=dict)   # key -> comment text
    stripped: Dict[str, str] = field(default_factory=dict)   # key -> value without comment
    annotated: Dict[str, str] = field(default_factory=dict)  # key -> value with comment

    def has_comments(self) -> bool:
        return bool(self.comments)

    def summary(self) -> str:
        n = len(self.comments)
        return f"{n} key(s) have inline comments" if n else "No inline comments found"


def extract_comments(env: Dict[str, str]) -> CommentResult:
    """Extract inline comments from env values (values may include raw comment text)."""
    result = CommentResult()
    for key, raw_value in env.items():
        m = _COMMENT_RE.match(f"{key}={raw_value}")
        if m:
            stripped_val = _INLINE_STRIP_RE.sub('', raw_value).strip()
            comment_text = raw_value[len(stripped_val):].lstrip().lstrip('#').strip()
            result.comments[key] = comment_text
            result.stripped[key] = stripped_val
            result.annotated[key] = raw_value
        else:
            result.stripped[key] = raw_value
    return result


def strip_comments(env: Dict[str, str]) -> Dict[str, str]:
    """Return a new env dict with all inline comments removed from values."""
    result = extract_comments(env)
    return dict(result.stripped)


def add_comment(env: Dict[str, str], key: str, comment: str) -> Dict[str, str]:
    """Return a new env dict with a comment appended to the given key's value."""
    if key not in env:
        raise KeyError(f"Key '{key}' not found in env")
    updated = dict(env)
    bare = _INLINE_STRIP_RE.sub('', env[key]).strip()
    updated[key] = f"{bare}  # {comment}"
    return updated


def to_commented_string(env: Dict[str, str], comments: Optional[Dict[str, str]] = None) -> str:
    """Serialise env to .env string, optionally injecting comments from a mapping."""
    lines: List[str] = []
    comments = comments or {}
    for key, value in env.items():
        bare = _INLINE_STRIP_RE.sub('', value).strip()
        if key in comments:
            lines.append(f"{key}={bare}  # {comments[key]}")
        else:
            lines.append(f"{key}={bare}")
    return "\n".join(lines)
