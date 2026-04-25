"""CLI entry point for the sort/group subcommand."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from patchwork_env.parser import parse_env_file
from patchwork_env.reconciler import to_env_string
from patchwork_env.env_sorter import sort_env


def run_sort(args: argparse.Namespace) -> int:
    env_path = Path(args.env_file)
    if not env_path.exists():
        print(f"[error] file not found: {env_path}", file=sys.stderr)
        return 2

    try:
        env = parse_env_file(str(env_path))
    except Exception as exc:  # noqa: BLE001
        print(f"[error] could not parse {env_path}: {exc}", file=sys.stderr)
        return 2

    prefixes = args.prefixes.split(",") if getattr(args, "prefixes", None) else None
    mode = getattr(args, "mode", "alpha")

    result = sort_env(env, mode=mode, prefixes=prefixes)

    if args.summary:
        print(result.summary())
        return 0

    output_text = to_env_string(result.sorted_env)

    if args.output:
        out_path = Path(args.output)
        out_path.write_text(output_text)
        print(f"[ok] sorted env written to {out_path}")
    else:
        print(output_text, end="")

    return 0


def add_sort_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "sort",
        help="Sort or group keys in a .env file",
    )
    p.add_argument("env_file", help="Path to the .env file")
    p.add_argument(
        "--mode",
        choices=["alpha", "group"],
        default="alpha",
        help="Sort mode: alphabetical (default) or group by prefix",
    )
    p.add_argument(
        "--prefixes",
        default=None,
        help="Comma-separated list of prefixes for group mode (e.g. DB_,AWS_)",
    )
    p.add_argument(
        "--output",
        "-o",
        default=None,
        help="Write sorted output to this file instead of stdout",
    )
    p.add_argument(
        "--summary",
        action="store_true",
        help="Print a summary of groups and key counts instead of the file",
    )
    p.set_defaults(func=run_sort)
