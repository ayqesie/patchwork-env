"""Lint .env files for style and consistency issues."""

from dataclasses import dataclass, field
from typing import Dict, List

IMPORT_PATTERNS = ["#", "export "]


@dataclass
class LintResult:
    issues: Dict[str, List[str]] = field(default_factory=dict)

    def add(self, key: str, message: str) -> None:
        self.issues.setdefault(key, []).append(message)

    @property
    def has_issues(self) -> bool:
        return bool(self.issues)

    @property
    def summary(self) -> str:
        if not self.has_issues:
            return "No lint issues found."
        total = sum(len(v) for v in self.issues.values())
        return f"{total} lint issue(s) across {len(self.issues)} key(s)."

    @property
    def all_issues(self) -> List[str]:
        lines = []
        for key, messages in sorted(self.issues.items()):
            for msg in messages:
                lines.append(f"{key}: {msg}")
        return lines


def lint_env(env: Dict[str, str]) -> LintResult:
    """Run all lint checks on a parsed env dict."""
    result = LintResult()
    for key, value in env.items():
        _check_key_naming(key, result)
        _check_value_spacing(key, value, result)
        _check_inline_comment(key, value, result)
    return result


def _check_key_naming(key: str, result: LintResult) -> None:
    if key != key.upper():
        result.add(key, "Key should be uppercase (e.g. MY_VAR).")
    if key.startswith("_") or key.endswith("_"):
        result.add(key, "Key should not start or end with an underscore.")
    if "__" in key:
        result.add(key, "Key contains consecutive underscores.")


def _check_value_spacing(key: str, value: str, result: LintResult) -> None:
    if value != value.strip():
        result.add(key, "Value has leading or trailing whitespace.")


def _check_inline_comment(key: str, value: str, result: LintResult) -> None:
    stripped = value.strip()
    if " #" in stripped and not (
        stripped.startswith('"') or stripped.startswith("'")
    ):
        result.add(key, "Value appears to contain an inline comment; quote if intentional.")
