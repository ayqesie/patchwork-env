"""CLI entry point for the split subcommand."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from patchwork_env.parser import parse_env_file
from patchwork_env.splitter import split_env, to_env_string


def run_split(args: argparse.Namespace) -> int:
    env_path = Path(args.file)
    if not env_path.exists():
        print(f"error: file not found: {env_path}", file=sys.stderr)
        return 2

    try:
        env = parse_env_file(str(env_path))
    except Exception as exc:  # pragma: no cover
        print(f"error: could not parse {env_path}: {exc}", file=sys.stderr)
        return 2

    prefixes = args.prefixes if args.prefixes else None
    result = split_env(env, prefixes=prefixes, strip_prefix=args.strip_prefix)

    if not result.has_groups():
        print("no groups detected — nothing to split")
        return 1

    out_dir = Path(args.outdir) if args.outdir else env_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    for group_name, group_env in result.groups.items():
        out_file = out_dir / f"{group_name.lower()}.env"
        out_file.write_text(to_env_string(group_env) + "\n")
        print(f"wrote {out_file} ({len(group_env)} key(s))")

    if result.ungrouped and args.keep_ungrouped:
        out_file = out_dir / "ungrouped.env"
        out_file.write_text(to_env_string(result.ungrouped) + "\n")
        print(f"wrote {out_file} ({len(result.ungrouped)} key(s)) [ungrouped]")

    print(result.summary())
    return 0


def add_split_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("split", help="split a .env file into multiple files by prefix")
    p.add_argument("file", help="source .env file")
    p.add_argument(
        "--prefixes",
        nargs="+",
        metavar="PREFIX",
        help="explicit prefixes to split on (auto-detected when omitted)",
    )
    p.add_argument(
        "--strip-prefix",
        action="store_true",
        default=False,
        help="remove prefix and underscore from keys in output files",
    )
    p.add_argument(
        "--outdir",
        metavar="DIR",
        help="directory to write output files (defaults to same dir as input)",
    )
    p.add_argument(
        "--keep-ungrouped",
        action="store_true",
        default=False,
        help="write ungrouped keys to ungrouped.env",
    )
    p.set_defaults(func=run_split)
