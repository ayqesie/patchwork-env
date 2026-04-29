"""CLI entry-point for the `template` sub-command."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from patchwork_env.parser import parse_env_file
from patchwork_env.schema_loader import load_schema_from_toml
from patchwork_env.templater import generate_template, to_template_string


def run_template(args: argparse.Namespace) -> int:
    env_path = Path(args.env_file)
    if not env_path.exists():
        print(f"[error] env file not found: {env_path}", file=sys.stderr)
        return 2

    schema = None
    if args.schema:
        schema_path = Path(args.schema)
        if not schema_path.exists():
            print(f"[error] schema file not found: {schema_path}", file=sys.stderr)
            return 2
        schema = load_schema_from_toml(schema_path)

    env = parse_env_file(env_path)
    result = generate_template(env, schema=schema)
    output = to_template_string(result)

    if args.output:
        out_path = Path(args.output)
        out_path.write_text(output)
        print(f"Template written to {out_path}")
    else:
        print(output, end="")

    print(result.summary(), file=sys.stderr)
    return 0


def add_template_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "template",
        help="Generate a blank .env template from an existing env file",
    )
    p.add_argument("env_file", help="Source .env file")
    p.add_argument("--schema", metavar="FILE", help="Optional TOML schema for type hints")
    p.add_argument("-o", "--output", metavar="FILE", help="Write template to FILE instead of stdout")
    p.set_defaults(func=run_template)
