"""Entry point — wires all sub-commands into a single `patchwork-env` CLI."""

from __future__ import annotations

import argparse
import sys

from patchwork_env.cli_audit import run_audit
from patchwork_env.cli_diff import run_diff
from patchwork_env.cli_patch import run_patch
from patchwork_env.cli_reconcile import run_reconcile
from patchwork_env.cli_snapshot import run_snapshot
from patchwork_env.cli_validate import run_validate
from patchwork_env.snapshot import DEFAULT_SNAPSHOT_DIR


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="patchwork-env",
        description="Diff and reconcile .env files across deployment environments.",
    )
    sub = parser.add_subparsers(dest="command")

    # diff
    p_diff = sub.add_parser("diff", help="Show diff between two .env files")
    p_diff.add_argument("base")
    p_diff.add_argument("target")

    # validate
    p_val = sub.add_parser("validate", help="Validate a .env file against a schema")
    p_val.add_argument("env_file")
    p_val.add_argument("--schema", default=None)

    # reconcile
    p_rec = sub.add_parser("reconcile", help="Reconcile target env toward base")
    p_rec.add_argument("base")
    p_rec.add_argument("target")
    p_rec.add_argument("--strategy", choices=["merge", "overwrite"], default="merge")
    p_rec.add_argument("--output", default=None)

    # audit
    p_aud = sub.add_parser("audit", help="Audit a .env file for common issues")
    p_aud.add_argument("env_file")

    # patch
    p_patch = sub.add_parser("patch", help="Apply a patch file to a .env file")
    p_patch.add_argument("base")
    p_patch.add_argument("patch_file")
    p_patch.add_argument("--output", default=None)

    # snapshot
    p_snap = sub.add_parser("snapshot", help="Manage env snapshots")
    p_snap.add_argument("--snapshot-dir", default=str(DEFAULT_SNAPSHOT_DIR), dest="snapshot_dir")
    snap_sub = p_snap.add_subparsers(dest="subcommand")

    ss_save = snap_sub.add_parser("save", help="Save current env as a named snapshot")
    ss_save.add_argument("name")
    ss_save.add_argument("env_file")

    ss_diff = snap_sub.add_parser("diff", help="Diff a snapshot against a current env file")
    ss_diff.add_argument("name")
    ss_diff.add_argument("env_file")

    snap_sub.add_parser("list", help="List saved snapshots")

    ss_del = snap_sub.add_parser("delete", help="Delete a named snapshot")
    ss_del.add_argument("name")

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    dispatch = {
        "diff": run_diff,
        "validate": run_validate,
        "reconcile": run_reconcile,
        "audit": run_audit,
        "patch": run_patch,
        "snapshot": run_snapshot,
    }
    return dispatch[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
