"""CLI entry point for the cascade subcommand."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from patchwork_env.parser import parse_env_file
from patchwork_env.cascader import cascade_env_files
from patchwork_env.formatter import _colorize


def run_cascade(args: argparse.Namespace) -> int:
    """Cascade multiple .env files in priority order and print the result."""
    file_pairs = []
    for path_str in args.files:
        p = Path(path_str)
        if not p.exists():
            print(f"error: file not found: {path_str}", file=sys.stderr)
            return 2
        file_pairs.append((p.name, parse_env_file(str(p))))

    if len(file_pairs) < 2:
        print("error: at least two files are required for cascade.", file=sys.stderr)
        return 2

    result = cascade_env_files(file_pairs)

    if args.verbose:
        print(result.summary())
        print()

    if args.output:
        out = Path(args.output)
        lines = [f"{k}={v}" for k, v in sorted(result.final.items())]
        out.write_text("\n".join(lines) + "\n")
        print(f"Written to {args.output}")
    else:
        for key, value in sorted(result.final.items()):
            source = result.sources.get(key, "?")
            if args.show_source:
                print(f"{key}={value}  # {source}")
            else:
                print(f"{key}={value}")

    return 1 if result.has_overrides() else 0


def add_cascade_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "cascade",
        help="Merge .env files in priority order (last file wins).",
    )
    p.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help=".env files in ascending priority order.",
    )
    p.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Write merged result to this file instead of stdout.",
    )
    p.add_argument(
        "--show-source",
        action="store_true",
        default=False,
        help="Annotate each key with the file it came from.",
    )
    p.add_argument(
        "--verbose", "-v",
        action="store_true",
        default=False,
        help="Print cascade summary before output.",
    )
    p.set_defaults(func=run_cascade)
