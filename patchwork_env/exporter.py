"""Export env diffs and snapshots to portable formats (JSON, TOML, Markdown)."""

from __future__ import annotations

import json
from typing import Any

from patchwork_env.differ import EnvDiff

try:
    import tomllib  # Python 3.11+
except ImportError:  # pragma: no cover
    import tomli as tomllib  # type: ignore

try:
    import tomli_w
    _TOML_WRITE = True
except ImportError:  # pragma: no cover
    _TOML_WRITE = False


def diff_to_dict(diff: EnvDiff) -> dict[str, Any]:
    """Serialise an EnvDiff to a plain dictionary."""
    return {
        "added": dict(diff.added),
        "removed": list(diff.removed),
        "changed": {k: {"base": b, "target": t} for k, (b, t) in diff.changed.items()},
        "unchanged": list(diff.unchanged),
    }


def export_json(diff: EnvDiff, *, indent: int = 2) -> str:
    """Return a JSON string representing the diff."""
    return json.dumps(diff_to_dict(diff), indent=indent)


def export_toml(diff: EnvDiff) -> str:
    """Return a TOML string representing the diff.

    Requires *tomli-w* to be installed; raises RuntimeError otherwise.
    """
    if not _TOML_WRITE:
        raise RuntimeError(
            "tomli-w is required for TOML export: pip install tomli-w"
        )
    data = diff_to_dict(diff)
    # TOML tables need string-keyed sub-tables; 'changed' is already that.
    return tomli_w.dumps(data)  # type: ignore[attr-defined]


def export_markdown(diff: EnvDiff, *, base_label: str = "base", target_label: str = "target") -> str:
    """Return a Markdown report of the diff."""
    lines: list[str] = ["# Env Diff Report", ""]

    sections = [
        ("Added", [(k, v) for k, v in diff.added.items()]),
        ("Removed", [(k, None) for k in diff.removed]),
        ("Changed", list(diff.changed.items())),
        ("Unchanged", [(k, None) for k in diff.unchanged]),
    ]

    for title, items in sections:
        lines.append(f"## {title} ({len(items)})")
        if not items:
            lines.append("_none_")
        elif title == "Changed":
            lines.append(f"| Key | {base_label} | {target_label} |")
            lines.append("|-----|------|--------|")
            for key, val in items:
                b, t = val  # type: ignore[misc]
                lines.append(f"| `{key}` | `{b}` | `{t}` |")
        elif title == "Added":
            lines.append("| Key | Value |")
            lines.append("|-----|-------|")
            for key, val in items:
                lines.append(f"| `{key}` | `{val}` |")
        else:
            for key, _ in items:
                lines.append(f"- `{key}`")
        lines.append("")

    return "\n".join(lines)
