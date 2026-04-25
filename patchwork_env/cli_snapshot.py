"""CLI commands for snapshot management: save, load-diff, list, delete."""

from __future__ import annotations

import sys
from pathlib import Path

from patchwork_env.differ import diff_envs
from patchwork_env.formatter import format_diff, format_summary
from patchwork_env.parser import parse_env_file
from patchwork_env.snapshot import (
    DEFAULT_SNAPSHOT_DIR,
    Snapshot,
    delete_snapshot,
    list_snapshots,
    load_snapshot,
    save_snapshot,
)


def run_snapshot(args) -> int:  # noqa: ANN001
    """Dispatch snapshot sub-commands. Returns exit code."""
    snapshot_dir = Path(getattr(args, "snapshot_dir", DEFAULT_SNAPSHOT_DIR))

    if args.subcommand == "save":
        return _cmd_save(args, snapshot_dir)
    if args.subcommand == "diff":
        return _cmd_diff(args, snapshot_dir)
    if args.subcommand == "list":
        return _cmd_list(snapshot_dir)
    if args.subcommand == "delete":
        return _cmd_delete(args, snapshot_dir)

    print(f"Unknown snapshot subcommand: {args.subcommand}", file=sys.stderr)
    return 2


def _cmd_save(args, snapshot_dir: Path) -> int:
    env_path = Path(args.env_file)
    if not env_path.exists():
        print(f"Error: file not found: {env_path}", file=sys.stderr)
        return 2
    env = parse_env_file(env_path)
    snap = Snapshot(name=args.name, env=env, source_file=str(env_path))
    dest = save_snapshot(snap, snapshot_dir=snapshot_dir)
    print(f"Snapshot '{args.name}' saved to {dest}")
    return 0


def _cmd_diff(args, snapshot_dir: Path) -> int:
    try:
        snap = load_snapshot(args.name, snapshot_dir=snapshot_dir)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    env_path = Path(args.env_file)
    if not env_path.exists():
        print(f"Error: file not found: {env_path}", file=sys.stderr)
        return 2

    current_env = parse_env_file(env_path)
    result = diff_envs(snap.env, current_env)
    print(format_diff(result, base_label=f"snapshot:{args.name}", target_label=str(env_path)))
    print(format_summary(result))
    return 1 if result.has_diff() else 0


def _cmd_list(snapshot_dir: Path) -> int:
    names = list_snapshots(snapshot_dir=snapshot_dir)
    if not names:
        print("No snapshots saved.")
    else:
        for name in names:
            print(name)
    return 0


def _cmd_delete(args, snapshot_dir: Path) -> int:
    removed = delete_snapshot(args.name, snapshot_dir=snapshot_dir)
    if removed:
        print(f"Snapshot '{args.name}' deleted.")
        return 0
    print(f"Error: snapshot '{args.name}' not found.", file=sys.stderr)
    return 2
