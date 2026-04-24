"""Reconcile .env files by applying diffs from a source environment."""

from typing import Optional
from patchwork_env.differ import EnvDiff


def reconcile(
    base: dict[str, str],
    target: dict[str, str],
    diff: EnvDiff,
    strategy: str = "merge",
    fill_value: Optional[str] = None,
) -> dict[str, str]:
    """
    Reconcile target env against base using a computed diff.

    Strategies:
        - merge: add missing keys from base into target, keep target values for conflicts
        - overwrite: apply all base values onto target
        - fill_missing: only add keys missing in target, use fill_value if provided
    """
    if strategy not in ("merge", "overwrite", "fill_missing"):
        raise ValueError(f"Unknown strategy: {strategy!r}")

    result = dict(target)

    if strategy == "merge":
        for key in diff.added:
            result[key] = base[key]

    elif strategy == "overwrite":
        for key in diff.added:
            result[key] = base[key]
        for key in diff.changed:
            result[key] = base[key]

    elif strategy == "fill_missing":
        for key in diff.added:
            result[key] = fill_value if fill_value is not None else base[key]

    return result


def apply_patch(base: dict[str, str], patch: dict[str, Optional[str]]) -> dict[str, str]:
    """
    Apply a patch dict to a base env dict.
    Keys with None values are removed; others are set/updated.
    """
    result = dict(base)
    for key, value in patch.items():
        if value is None:
            result.pop(key, None)
        else:
            result[key] = value
    return result


def to_env_string(env: dict[str, str]) -> str:
    """Serialize an env dict back to .env file string format."""
    lines = []
    for key, value in sorted(env.items()):
        if " " in value or "#" in value or not value:
            lines.append(f'{key}="{value}"')
        else:
            lines.append(f"{key}={value}")
    return "\n".join(lines) + "\n" if lines else ""
