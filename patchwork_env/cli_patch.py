"""CLI entry point for patching a target .env file using a base as reference."""

import sys
from pathlib import Path

from patchwork_env.parser import parse_env_file
from patchwork_env.differ import diff_envs
from patchwork_env.reconciler import reconcile, to_env_string
from patchwork_env.formatter import format_diff, format_summary


def run_patch(base_path: str, target_path: str, output_path: str | None = None,
             strategy: str = "merge", quiet: bool = False) -> int:
    """
    Patch target env file using base as reference.

    Returns:
        0 — no changes needed
        1 — patch applied successfully
        2 — file error
        3 — invalid strategy
    """
    if strategy not in ("merge", "overwrite"):
        if not quiet:
            print(f"[error] unknown strategy '{strategy}'. use 'merge' or 'overwrite'.",
                  file=sys.stderr)
        return 3

    base_file = Path(base_path)
    target_file = Path(target_path)

    if not base_file.exists():
        if not quiet:
            print(f"[error] base file not found: {base_path}", file=sys.stderr)
        return 2

    if not target_file.exists():
        if not quiet:
            print(f"[error] target file not found: {target_path}", file=sys.stderr)
        return 2

    base_env = parse_env_file(str(base_file))
    target_env = parse_env_file(str(target_file))

    diff = diff_envs(base_env, target_env)

    if not diff.has_diff():
        if not quiet:
            print("[ok] no differences found, nothing to patch.")
        return 0

    if not quiet:
        print(format_diff(diff, base_label=base_path, target_label=target_path))
        print(format_summary(diff))

    patched_env = reconcile(base_env, target_env, strategy=strategy)
    patched_str = to_env_string(patched_env)

    dest = Path(output_path) if output_path else target_file
    dest.write_text(patched_str)

    if not quiet:
        print(f"[patched] wrote {len(patched_env)} keys to {dest}")

    return 1
