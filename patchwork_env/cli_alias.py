"""cli_alias.py — CLI wrapper for the aliaser module."""
from __future__ import annotations
import argparse
import sys
from patchwork_env.parser import parse_env_file
from patchwork_env.aliaser import alias_env


def _parse_alias_pair(raw: str) -> tuple[str, str]:
    """Parse 'alias=CANONICAL_KEY' into a (alias, canonical) tuple."""
    if "=" not in raw:
        raise argparse.ArgumentTypeError(
            f"Alias pair must be 'alias=CANONICAL_KEY', got: {raw!r}"
        )
    alias, _, canonical = raw.partition("=")
    return alias.strip(), canonical.strip()


def run_alias(args: argparse.Namespace) -> int:
    """Entry point for the 'alias' subcommand.

    Returns:
        0 — all aliases resolved
        1 — one or more aliases could not be resolved
        2 — input file not found or unreadable
    """
    try:
        env = parse_env_file(args.file)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    alias_map: dict[str, str] = {}
    for raw in args.alias or []:
        try:
            alias, canonical = _parse_alias_pair(raw)
            alias_map[alias] = canonical
        except argparse.ArgumentTypeError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

    if not alias_map:
        print("error: at least one --alias pair is required", file=sys.stderr)
        return 2

    result = alias_env(env, alias_map, include_originals=args.include_originals)

    if args.verbose:
        print(result.summary())
        print()

    for key, value in sorted(result.resolved.items()):
        print(f"{key}={value}")

    if result.has_issues():
        for alias in result.not_found:
            print(f"warning: alias '{alias}' -> canonical key not found", file=sys.stderr)
        return 1

    return 0


def add_alias_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "alias",
        help="Resolve human-friendly aliases to env key values",
    )
    p.add_argument("file", help="Path to the .env file")
    p.add_argument(
        "--alias",
        metavar="ALIAS=KEY",
        action="append",
        help="Alias mapping in the form alias=CANONICAL_KEY (repeatable)",
    )
    p.add_argument(
        "--include-originals",
        action="store_true",
        default=False,
        help="Also emit original key/value pairs alongside aliases",
    )
    p.add_argument("--verbose", action="store_true", default=False)
    p.set_defaults(func=run_alias)
