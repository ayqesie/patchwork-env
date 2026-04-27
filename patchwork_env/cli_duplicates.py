"""CLI entry point for the 'duplicates' subcommand."""

import argparse
import sys
from pathlib import Path

from patchwork_env.duplicates import find_duplicates
from patchwork_env.formatter import _colorize


def run_duplicates(args: argparse.Namespace) -> int:
    env_path = Path(args.file)

    if not env_path.exists():
        print(f"Error: file not found: {env_path}", file=sys.stderr)
        return 2

    text = env_path.read_text(encoding="utf-8")
    result = find_duplicates(text)

    if not result.has_issues():
        print(_colorize("green", f"No duplicate keys in {env_path}."))
        return 0

    print(_colorize("yellow", f"Duplicates found in {env_path}:"))
    for key, values in result.duplicates.items():
        formatted_values = ", ".join(repr(v) for v in values)
        print(f"  {_colorize('red', key)}: [{formatted_values}]")

    print()
    print(result.summary())
    return 1


def add_duplicates_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "duplicates",
        help="Detect duplicate keys in a .env file.",
    )
    p.add_argument("file", help="Path to the .env file to check.")
    p.set_defaults(func=run_duplicates)
