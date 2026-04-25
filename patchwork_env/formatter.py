"""Terminal formatting helpers for diff, summary, validation, and audit output."""

import sys
from typing import Dict

from patchwork_env.differ import EnvDiff
from patchwork_env.validator import ValidationResult
from patchwork_env.auditor import AuditResult

_COLORS = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "cyan": "\033[36m",
    "bold": "\033[1m",
    "reset": "\033[0m",
}


def _colorize(text: str, color: str) -> str:
    if not sys.stdout.isatty():
        return text
    code = _COLORS.get(color, "")
    return f"{code}{text}{_COLORS['reset']}"


def format_diff(diff: EnvDiff, base_label: str = "base", target_label: str = "target") -> str:
    lines = [_colorize(f"--- {base_label}", "bold"), _colorize(f"+++ {target_label}", "bold")]

    if not diff.has_diff():
        lines.append(_colorize("  (no differences)", "cyan"))
        return "\n".join(lines)

    for key in sorted(diff.removed):
        lines.append(_colorize(f"- {key}={diff.removed[key]}", "red"))
    for key in sorted(diff.added):
        lines.append(_colorize(f"+ {key}={diff.added[key]}", "green"))
    for key, (old, new) in sorted(diff.changed.items()):
        lines.append(_colorize(f"~ {key}: {old} -> {new}", "yellow"))

    return "\n".join(lines)


def format_summary(diff: EnvDiff) -> str:
    return _colorize(diff.summary(), "bold")


def format_validation(result: ValidationResult) -> str:
    lines = []
    if result.is_valid():
        lines.append(_colorize("✓ validation passed", "green"))
    else:
        lines.append(_colorize("✗ validation failed", "red"))

    for key in sorted(result.missing_required):
        lines.append(_colorize(f"  missing required: {key}", "red"))
    for key in sorted(result.unknown_keys):
        lines.append(_colorize(f"  unknown key: {key}", "yellow"))
    for key, msg in sorted(result.type_errors.items()):
        lines.append(_colorize(f"  type error [{key}]: {msg}", "yellow"))

    return "\n".join(lines)


def format_audit(result: AuditResult, label: str = "") -> str:
    header = f"audit: {label}" if label else "audit"
    lines = [_colorize(header, "bold")]

    if not result.has_issues():
        lines.append(_colorize("  ✓ no issues found", "green"))
        return "\n".join(lines)

    for key in sorted(result.empty_values):
        lines.append(_colorize(f"  [empty]       {key}", "yellow"))
    for key in sorted(result.duplicate_keys):
        lines.append(_colorize(f"  [duplicate]   {key}", "red"))
    for key in sorted(result.suspicious_values):
        lines.append(_colorize(f"  [suspicious]  {key}", "red"))
    for key in sorted(result.placeholder_values):
        lines.append(_colorize(f"  [placeholder] {key}", "yellow"))

    lines.append(_colorize(f"  summary: {result.summary()}", "bold"))
    return "\n".join(lines)
