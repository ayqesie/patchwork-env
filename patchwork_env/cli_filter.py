"""CLI entry point for the filter subcommand."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from patchwork_env.parser import parse_env_file
from patchwork_env.filter import filter_env
from patchwork_env.reconciler import to_env_string


def run_filter(args: argparse.Namespace) -> int:
    env_path = Path(args.env_file)
    if not env_path.exists():
        print(f"error: file not found: {env_path}", file=sys.stderr)
        return 2

    env = parse_env_file(str(env_path))

    result = filter_env(
        env,
        include_patterns=args.include or None,
        exclude_patterns=args.exclude or None,
        prefix=args.prefix or None,
        value_pattern=args.value_pattern or None,
        empty_only=args.empty_only,
        nonempty_only=args.nonempty_only,
    )

    if not result.has_matches():
        print("No keys matched the given filters.")
        return 1

    output = to_env_string(result.matched)

    if args.output:
        Path(args.output).write_text(output)
        print(f"Wrote {len(result.matched)} key(s) to {args.output}")
    else:
        print(output, end="")

    if args.summary:
        print(result.summary(), file=sys.stderr)

    return 0


def add_filter_subparser(subparsers) -> None:
    p = subparsers.add_parser("filter", help="Filter keys from an env file")
    p.add_argument("env_file", help="Path to .env file")
    p.add_argument("--include", nargs="+", metavar="PATTERN",
                   help="Glob patterns for keys to include")
    p.add_argument("--exclude", nargs="+", metavar="PATTERN",
                   help="Glob patterns for keys to exclude")
    p.add_argument("--prefix", metavar="PREFIX",
                   help="Only include keys with this prefix")
    p.add_argument("--value-pattern", metavar="REGEX",
                   help="Only include keys whose value matches regex")
    p.add_argument("--empty-only", action="store_true",
                   help="Only include keys with empty values")
    p.add_argument("--nonempty-only", action="store_true",
                   help="Only include keys with non-empty values")
    p.add_argument("--output", "-o", metavar="FILE",
                   help="Write filtered output to file")
    p.add_argument("--summary", action="store_true",
                   help="Print match summary to stderr")
    p.set_defaults(func=run_filter)
