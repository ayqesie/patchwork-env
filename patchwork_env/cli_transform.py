"""CLI entry point for the transform subcommand."""

import argparse
import sys
from pathlib import Path

from patchwork_env.parser import parse_env_file
from patchwork_env.transformer import transform_env
from patchwork_env.reconciler import to_env_string


def _parse_rule(raw: str) -> dict:
    """Parse a rule string like 'upper', 'prefix:prod_', 'replace:old,new'."""
    if ":" in raw:
        rule, arg = raw.split(":", 1)
        return {"rule": rule.strip(), "arg": arg}
    return {"rule": raw.strip()}


def run_transform(args: argparse.Namespace) -> int:
    env_path = Path(args.file)
    if not env_path.exists():
        print(f"error: file not found: {env_path}", file=sys.stderr)
        return 2

    env = parse_env_file(str(env_path))
    rules = [_parse_rule(r) for r in args.rule] if args.rule else []

    if not rules:
        print("error: at least one --rule is required", file=sys.stderr)
        return 2

    keys = args.keys.split(",") if args.keys else None
    result = transform_env(env, rules, keys=keys)

    if args.output:
        out_path = Path(args.output)
        out_path.write_text(to_env_string(result.transformed))
        print(f"wrote transformed env to {out_path}")
    else:
        print(to_env_string(result.transformed))

    print(result.summary(), file=sys.stderr)
    return 1 if result.has_changes() else 0


def add_transform_subparser(subparsers) -> None:
    p = subparsers.add_parser("transform", help="apply value transformations to a .env file")
    p.add_argument("file", help="path to .env file")
    p.add_argument(
        "--rule",
        action="append",
        metavar="RULE[:ARG]",
        help="transformation rule (e.g. upper, prefix:prod_, replace:old,new). Repeatable.",
    )
    p.add_argument(
        "--keys",
        metavar="KEY1,KEY2",
        help="comma-separated list of keys to transform (default: all)",
    )
    p.add_argument("-o", "--output", metavar="FILE", help="write result to file instead of stdout")
    p.set_defaults(func=run_transform)
