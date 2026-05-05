"""CLI entry-point for the `score` sub-command."""
from __future__ import annotations

import argparse
from pathlib import Path

from .parser import parse_env_file
from .schema_loader import load_schema_from_toml, schema_from_base_env
from .scorer import score_env


def run_score(args: argparse.Namespace) -> int:
    env_path = Path(args.env_file)
    if not env_path.exists():
        print(f"error: env file not found: {env_path}")
        return 2

    env = parse_env_file(str(env_path))

    schema = None
    if hasattr(args, "schema") and args.schema:
        schema_path = Path(args.schema)
        if not schema_path.exists():
            print(f"error: schema file not found: {schema_path}")
            return 2
        schema = load_schema_from_toml(str(schema_path))
    elif hasattr(args, "base") and args.base:
        base_path = Path(args.base)
        if not base_path.exists():
            print(f"error: base env file not found: {base_path}")
            return 2
        base_env = parse_env_file(str(base_path))
        schema = schema_from_base_env(base_env)

    result = score_env(env, schema)
    print(result.summary())

    if result.total < 60:
        return 1
    return 0


def add_score_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("score", help="Score an .env file for overall health")
    p.add_argument("env_file", help="Path to the .env file to score")
    group = p.add_mutually_exclusive_group()
    group.add_argument("--schema", metavar="TOML", help="TOML schema file for validation")
    group.add_argument("--base", metavar="ENV", help="Base .env file to derive schema from")
    p.set_defaults(func=run_score)
