"""CLI entry point for the `profile` subcommand."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from patchwork_env.parser import parse_env_file
from patchwork_env.profiler import profile_env


def run_profile(args: argparse.Namespace) -> int:
    """Run the profile command. Returns an exit code."""
    env_path = Path(args.env_file)

    if not env_path.exists():
        print(f"error: file not found: {env_path}", file=sys.stderr)
        return 2

    try:
        env = parse_env_file(env_path)
    except Exception as exc:  # noqa: BLE001
        print(f"error: could not parse {env_path}: {exc}", file=sys.stderr)
        return 2

    profile = profile_env(env)

    print(f"Profile: {env_path}")
    print("-" * 40)
    print(profile.summary())

    if args.verbose:
        _print_section("Empty values", profile.empty_values)
        _print_section("Placeholders", profile.placeholder_values)
        _print_section("URLs", profile.url_values)
        _print_section("Numeric", profile.numeric_values)
        _print_section("Boolean", profile.boolean_values)
        _print_section("Long values (>100 chars)", profile.long_values)

    issues = len(profile.empty_values) + len(profile.placeholder_values)
    return 1 if issues > 0 else 0


def _print_section(title: str, keys: list[str]) -> None:
    if not keys:
        return
    print(f"\n  {title}:")
    for key in keys:
        print(f"    - {key}")


def add_profile_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "profile",
        help="Analyse and summarise the contents of an env file.",
    )
    parser.add_argument("env_file", help="Path to the .env file to profile.")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="List individual keys for each category.",
    )
    parser.set_defaults(func=run_profile)
