"""Human-readable formatting for diffs and validation results."""

from __future__ import annotations

from patchwork_env.differ import EnvDiff
from patchwork_env.validator import ValidationResult

_RESET = "\033[0m"
_RED = "\033[31m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"
_BOLD = "\033[1m"


def _colorize(text: str, color: str, use_color: bool = True) -> str:
    if not use_color:
        return text
    return f"{color}{text}{_RESET}"


def format_diff(diff: EnvDiff, use_color: bool = True) -> str:
    """Render a diff as a human-readable string."""
    lines: list[str] = []
    header = _colorize("=== env diff ===", _BOLD, use_color)
    lines.append(header)

    if not diff.has_diff():
        lines.append(_colorize("No differences found.", _GREEN, use_color))
        return "\n".join(lines)

    for key in sorted(diff.removed):
        lines.append(_colorize(f"- {key}={diff.base[key]}", _RED, use_color))

    for key in sorted(diff.added):
        lines.append(_colorize(f"+ {key}={diff.target[key]}", _GREEN, use_color))

    for key in sorted(diff.changed):
        lines.append(
            _colorize(f"~ {key}: {diff.base[key]!r} -> {diff.target[key]!r}", _YELLOW, use_color)
        )

    return "\n".join(lines)


def format_summary(diff: EnvDiff, use_color: bool = True) -> str:
    """One-line summary of a diff."""
    parts = []
    if diff.added:
        parts.append(_colorize(f"+{len(diff.added)} added", _GREEN, use_color))
    if diff.removed:
        parts.append(_colorize(f"-{len(diff.removed)} removed", _RED, use_color))
    if diff.changed:
        parts.append(_colorize(f"~{len(diff.changed)} changed", _YELLOW, use_color))
    if not parts:
        return _colorize("no diff", _GREEN, use_color)
    return ", ".join(parts)


def format_validation(result: ValidationResult, use_color: bool = True) -> str:
    """Render a ValidationResult as a human-readable string."""
    lines: list[str] = []
    header = _colorize("=== env validation ===", _BOLD, use_color)
    lines.append(header)

    if result.is_valid:
        lines.append(_colorize("All checks passed.", _GREEN, use_color))
        return "\n".join(lines)

    for key in sorted(result.missing_required):
        lines.append(_colorize(f"  missing required key: {key}", _RED, use_color))

    for key in sorted(result.unknown_keys):
        lines.append(_colorize(f"  unknown key: {key}", _CYAN, use_color))

    for key, msg in sorted(result.type_errors.items()):
        lines.append(_colorize(f"  type error [{key}]: {msg}", _YELLOW, use_color))

    return "\n".join(lines)
