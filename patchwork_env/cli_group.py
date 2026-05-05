"""CLI entry-point for the `group` sub-command."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from patchwork_env.grouper import group_by_pattern, group_by_prefix
from patchwork_env.parser import parse_env_file


def run_group(args: argparse.Namespace) -> int:
    env_path = Path(args.file)
    if not env_path.exists():
        print(f"error: file not found: {env_path}", file=sys.stderr)
        return 2

    try:
        env = parse_env_file(str(env_path))
    except Exception as exc:  # noqa: BLE001
        print(f"error: could not parse {env_path}: {exc}", file=sys.stderr)
        return 2

    if args.pattern:
        patterns = {}
        for pair in args.pattern:
            if ":" not in pair:
                print(f"error: pattern must be LABEL:REGEX, got: {pair!r}", file=sys.stderr)
                return 2
            label, _, regex = pair.partition(":")
            patterns[label.strip()] = regex.strip()
        result = group_by_pattern(env, patterns)
    else:
        prefixes: Optional[List[str]] = args.prefix if args.prefix else None
        result = group_by_prefix(env, prefixes=prefixes, delimiter=args.delimiter)

    if not result.has_groups():
        print("No groups found.")
        return 1

    print(result.summary())
    return 0


def add_group_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "group",
        help="Group .env keys by prefix or custom regex pattern",
    )
    p.add_argument("file", help="Path to the .env file")
    p.add_argument(
        "--prefix",
        metavar="PREFIX",
        nargs="+",
        help="Explicit prefix(es) to group by (auto-detected when omitted)",
    )
    p.add_argument(
        "--delimiter",
        default="_",
        help="Delimiter used to split key prefixes (default: _)",
    )
    p.add_argument(
        "--pattern",
        metavar="LABEL:REGEX",
        nargs="+",
        help="Named regex patterns, e.g. 'db:^DB_' 'aws:^AWS_'",
    )
    p.set_defaults(func=run_group)
