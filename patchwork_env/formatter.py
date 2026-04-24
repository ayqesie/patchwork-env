"""Format diff output for CLI display."""

from patchwork_env.differ import EnvDiff

ANSI_RED = "\033[91m"
ANSI_GREEN = "\033[92m"
ANSI_YELLOW = "\033[93m"
ANSI_RESET = "\033[0m"


def format_diff(
    diff: EnvDiff,
    base_label: str = "base",
    target_label: str = "target",
    color: bool = True,
) -> str:
    """Return a human-readable diff string."""
    lines = []
    header = f"--- {base_label}\n+++ {target_label}"
    lines.append(header)

    for key in sorted(diff.removed):
        line = f"- {key}={diff.base_only[key]}"
        lines.append(_colorize(line, ANSI_RED, color))

    for key in sorted(diff.added):
        line = f"+ {key}={diff.target_only[key]}"
        lines.append(_colorize(line, ANSI_GREEN, color))

    for key in sorted(diff.changed):
        old_val, new_val = diff.changed[key]
        lines.append(_colorize(f"~ {key}: {old_val!r} -> {new_val!r}", ANSI_YELLOW, color))

    if not diff.removed and not diff.added and not diff.changed:
        lines.append("  (no differences)")

    return "\n".join(lines)


def format_summary(diff: EnvDiff, color: bool = True) -> str:
    """Return a short summary line of the diff."""
    parts = []
    if diff.added:
        parts.append(_colorize(f"+{len(diff.added)} added", ANSI_GREEN, color))
    if diff.removed:
        parts.append(_colorize(f"-{len(diff.removed)} removed", ANSI_RED, color))
    if diff.changed:
        parts.append(_colorize(f"~{len(diff.changed)} changed", ANSI_YELLOW, color))
    if not parts:
        return "No differences found."
    return "  ".join(parts)


def _colorize(text: str, color_code: str, enabled: bool) -> str:
    if not enabled:
        return text
    return f"{color_code}{text}{ANSI_RESET}"
