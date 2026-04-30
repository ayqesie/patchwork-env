"""CLI entry point for the typo-checker command."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from patchwork_env.parser import parse_env_file
from patchwork_env.typo_checker import check_typos


def run_typo(args: argparse.Namespace) -> int:
    env_path = Path(args.file)
    ref_path = Path(args.reference)

    if not env_path.exists():
        print(f"[error] env file not found: {env_path}", file=sys.stderr)
        return 2
    if not ref_path.exists():
        print(f"[error] reference file not found: {ref_path}", file=sys.stderr)
        return 2

    env = parse_env_file(str(env_path))
    reference = parse_env_file(str(ref_path))

    cutoff = float(args.cutoff) if args.cutoff else 0.8
    result = check_typos(env, reference, cutoff=cutoff)

    print(result.summary())

    if result.has_suggestions():
        return 1
    return 0


def add_typo_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "typo",
        help="Detect possible key typos by comparing against a reference .env file.",
    )
    p.add_argument("file", help="The .env file to check.")
    p.add_argument("reference", help="Reference .env file whose keys are considered canonical.")
    p.add_argument(
        "--cutoff",
        default="0.8",
        help="Similarity cutoff (0.0-1.0, default 0.8). Higher = stricter.",
    )
    p.set_defaults(func=run_typo)
