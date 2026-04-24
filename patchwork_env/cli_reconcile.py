"""CLI entry point for reconciling .env files."""

import sys
from pathlib import Path

from patchwork_env.parser import parse_env_file
from patchwork_env.differ import diff_envs
from patchwork_env.reconciler import reconcile, to_env_string
from patchwork_env.formatter import format_summary


def run_reconcile(
    base_path: str,
    target_path: str,
    output_path: str | None = None,
    strategy: str = "merge",
    dry_run: bool = False,
) -> int:
    """
    Reconcile target env against base env.

    Returns:
        0 - reconciled successfully (or no diff)
        1 - reconciled with changes
        2 - file not found or invalid strategy
    """
    base_file = Path(base_path)
    target_file = Path(target_path)

    if not base_file.exists():
        print(f"error: base file not found: {base_path}", file=sys.stderr)
        return 2

    if not target_file.exists():
        print(f"error: target file not found: {target_path}", file=sys.stderr)
        return 2

    valid_strategies = ("merge", "overwrite", "prune")
    if strategy not in valid_strategies:
        print(
            f"error: unknown strategy '{strategy}'. choose from: {', '.join(valid_strategies)}",
            file=sys.stderr,
        )
        return 2

    base_env = parse_env_file(base_path)
    target_env = parse_env_file(target_path)

    diff = diff_envs(base_env, target_env)

    if not diff.has_diff():
        print("no differences found. nothing to reconcile.")
        return 0

    print(format_summary(diff))

    reconciled = reconcile(base_env, target_env, strategy=strategy)
    output = to_env_string(reconciled)

    if dry_run:
        print("\n--- dry run output ---")
        print(output)
        return 1

    dest = output_path or target_path
    Path(dest).write_text(output)
    print(f"reconciled env written to: {dest}")
    return 1
