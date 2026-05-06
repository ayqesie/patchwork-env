"""CLI entry point for the deprecate subcommand."""

import argparse
import sys
from pathlib import Path

from patchwork_env.parser import parse_env_file
from patchwork_env.deprecator import deprecate_env
from patchwork_env.formatter import _colorize


def _load_deprecation_map(path: str) -> dict:
    """Load a simple KEY=REPLACEMENT deprecation map from a file.
    Lines starting with '#' are ignored. A value of '-' means no replacement.
    """
    result = {}
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            old, _, new = line.partition("=")
            result[old.strip()] = None if new.strip() == "-" else new.strip()
    return result


def run_deprecate(args: argparse.Namespace) -> int:
    env_path = Path(args.env_file)
    map_path = Path(args.map_file)

    if not env_path.exists():
        print(f"error: env file not found: {env_path}", file=sys.stderr)
        return 2

    if not map_path.exists():
        print(f"error: deprecation map not found: {map_path}", file=sys.stderr)
        return 2

    try:
        env = parse_env_file(str(env_path))
        dep_map = _load_deprecation_map(str(map_path))
    except Exception as exc:  # pragma: no cover
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = deprecate_env(env, dep_map)

    if result.has_issues():
        for key, replacement in result.deprecated.items():
            if replacement:
                msg = f"DEPRECATED  {key}  ->  {replacement}"
            else:
                msg = f"DEPRECATED  {key}  (no replacement)"
            print(_colorize(msg, "yellow"))
        print()
        print(result.summary())
        return 1

    print(_colorize("No deprecated keys found.", "green"))
    return 0


def add_deprecate_subparser(subparsers) -> None:
    p = subparsers.add_parser(
        "deprecate",
        help="Detect deprecated keys in an env file using a deprecation map.",
    )
    p.add_argument("env_file", help="Path to the .env file to check.")
    p.add_argument("map_file", help="Path to the deprecation map file (KEY=REPLACEMENT).")
    p.set_defaults(func=run_deprecate)
