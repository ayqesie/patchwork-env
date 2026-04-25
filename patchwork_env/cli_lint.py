"""CLI entry point for the lint subcommand."""

import argparse
import sys
from pathlib import Path

from patchwork_env.parser import parse_env_file
from patchwork_env.linter import lint_env
from patchwork_env.formatter import _colorize


def run_lint(args: argparse.Namespace) -> int:
    """
    Lint a .env file for style issues.

    Returns:
        0 — no issues
        1 — lint issues found
        2 — file not found or unreadable
    """
    env_path = Path(args.env_file)

    if not env_path.exists():
        print(f"Error: file not found: {env_path}", file=sys.stderr)
        return 2

    try:
        env = parse_env_file(str(env_path))
    except Exception as exc:  # noqa: BLE001
        print(f"Error reading {env_path}: {exc}", file=sys.stderr)
        return 2

    result = lint_env(env)

    if not result.has_issues:
        print(_colorize(f"✔ {result.summary}", "green"))
        return 0

    print(_colorize(f"✖ {result.summary}", "red"))
    for issue in result.all_issues:
        print(f"  • {issue}")

    return 1


def add_lint_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "lint",
        help="Check a .env file for style and consistency issues.",
    )
    parser.add_argument("env_file", help="Path to the .env file to lint.")
    parser.set_defaults(func=run_lint)
