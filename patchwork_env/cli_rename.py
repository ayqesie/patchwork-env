"""CLI handler for the `rename` subcommand."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

from patchwork_env.parser import parse_env_file
from patchwork_env.renamer import rename_keys
from patchwork_env.reconciler import to_env_string


def _parse_pair(value: str):
    """Parse 'OLD=NEW' rename pair from CLI argument."""
    if "=" not in value:
        raise argparse.ArgumentTypeError(
            f"Rename pair must be in OLD=NEW format, got: {value!r}"
        )
    old, new = value.split("=", 1)
    return old.strip(), new.strip()


def run_rename(args: argparse.Namespace) -> int:
    env_path = Path(args.file)
    if not env_path.exists():
        print(f"error: file not found: {env_path}", file=sys.stderr)
        return 2

    try:
        renames_list: List[tuple] = [_parse_pair(p) for p in args.rename]
    except argparse.ArgumentTypeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    renames = dict(renames_list)
    env = parse_env_file(str(env_path))
    result = rename_keys(env, renames, overwrite=args.overwrite)

    if result.skipped:
        for key in result.skipped:
            print(f"warning: key not found, skipped: {key}", file=sys.stderr)

    if result.conflicts:
        for key in result.conflicts:
            print(
                f"warning: target key already exists, skipped (use --overwrite): {key}",
                file=sys.stderr,
            )

    output_path = Path(args.output) if args.output else env_path
    output_path.write_text(to_env_string(result.env))
    print(f"wrote {output_path} — {result.summary()}")

    return 1 if result.has_issues() else 0


def add_rename_subparser(subparsers) -> None:
    p = subparsers.add_parser(
        "rename",
        help="Rename one or more keys in an env file",
    )
    p.add_argument("file", help="Path to the .env file")
    p.add_argument(
        "rename",
        nargs="+",
        metavar="OLD=NEW",
        help="Key rename pair(s) in OLD=NEW format",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite the new key if it already exists",
    )
    p.add_argument(
        "--output",
        metavar="FILE",
        help="Write result to FILE instead of overwriting input",
    )
    p.set_defaults(func=run_rename)
