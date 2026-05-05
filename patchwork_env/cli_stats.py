"""CLI entry point for the `stats` subcommand."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from patchwork_env.env_stats import compute_env_stats, merge_stats
from patchwork_env.parser import parse_env_file


def run_stats(args: argparse.Namespace) -> int:
    paths = [Path(p) for p in args.files]

    missing = [str(p) for p in paths if not p.exists()]
    if missing:
        for m in missing:
            print(f"error: file not found: {m}", file=sys.stderr)
        return 2

    all_stats = []
    for path in paths:
        env = parse_env_file(str(path))
        stats = compute_env_stats(env)
        all_stats.append(stats)
        if len(paths) > 1:
            print(f"--- {path} ---")
        print(stats.summary())
        if args.verbose:
            print(f"  keys:         {stats.total_keys}")
            print(f"  empty:        {stats.empty_keys}")
            print(f"  numeric:      {stats.numeric_keys}")
            print(f"  boolean:      {stats.boolean_keys}")
            print(f"  urls:         {stats.url_keys}")
            print(f"  long values:  {stats.long_value_keys}")

    if len(paths) > 1 and args.aggregate:
        merged = merge_stats(all_stats)
        print("--- aggregate ---")
        print(merged.summary())

    return 0


def add_stats_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "stats",
        help="show statistics for one or more .env files",
    )
    p.add_argument("files", nargs="+", help=".env file(s) to analyse")
    p.add_argument(
        "--verbose", "-v", action="store_true", help="print per-field breakdown"
    )
    p.add_argument(
        "--aggregate",
        "-a",
        action="store_true",
        help="print combined stats when multiple files are given",
    )
    p.set_defaults(func=run_stats)
