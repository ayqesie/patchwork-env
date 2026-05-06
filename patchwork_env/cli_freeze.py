"""CLI entry point for the freeze/drift-check commands."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from patchwork_env.freezer import check_drift, freeze_env
from patchwork_env.parser import parse_env_file


def run_freeze(args: argparse.Namespace) -> int:
    env_path = Path(args.env_file)
    if not env_path.exists():
        print(f"error: env file not found: {env_path}", file=sys.stderr)
        return 2

    env = parse_env_file(str(env_path))
    keys = args.keys.split(",") if args.keys else None
    frozen, result = freeze_env(env, keys=keys)

    out_path = Path(args.output)
    out_path.write_text(json.dumps(frozen, indent=2))
    print(f"Frozen {len(result.frozen_keys)} key(s) to {out_path}")
    if result.unfrozen_keys:
        print(f"Skipped (unfrozen): {', '.join(result.unfrozen_keys)}")
    return 0


def run_drift(args: argparse.Namespace) -> int:
    freeze_path = Path(args.freeze_file)
    env_path = Path(args.env_file)

    if not freeze_path.exists():
        print(f"error: freeze file not found: {freeze_path}", file=sys.stderr)
        return 2
    if not env_path.exists():
        print(f"error: env file not found: {env_path}", file=sys.stderr)
        return 2

    frozen: dict = json.loads(freeze_path.read_text())
    current = parse_env_file(str(env_path))
    result = check_drift(frozen, current)

    print(result.summary())
    return 1 if result.has_drift() else 0


def add_freeze_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p_freeze = subparsers.add_parser("freeze", help="Freeze env keys to a JSON snapshot")
    p_freeze.add_argument("env_file", help="Path to .env file")
    p_freeze.add_argument("-o", "--output", default=".env.frozen", help="Output freeze file")
    p_freeze.add_argument("--keys", default=None, help="Comma-separated list of keys to freeze")
    p_freeze.set_defaults(func=run_freeze)

    p_drift = subparsers.add_parser("drift", help="Check for drift against a frozen baseline")
    p_drift.add_argument("freeze_file", help="Path to frozen JSON baseline")
    p_drift.add_argument("env_file", help="Path to current .env file")
    p_drift.set_defaults(func=run_drift)
