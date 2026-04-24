"""CLI entry point for validating a .env file against a schema."""

from __future__ import annotations

import sys
from pathlib import Path

from patchwork_env.parser import parse_env_file
from patchwork_env.schema_loader import load_schema_from_toml, schema_from_base_env
from patchwork_env.validator import validate_env
from patchwork_env.formatter import format_validation


def run_validate(argv: list[str] | None = None) -> int:
    """Validate a .env file.  Returns an exit code.

    Exit codes:
        0 – valid
        1 – validation errors found
        2 – file / schema not found
    """
    import argparse

    parser = argparse.ArgumentParser(
        prog="patchwork-env validate",
        description="Validate a .env file against a schema.",
    )
    parser.add_argument("env_file", help="Path to the .env file to validate.")
    parser.add_argument(
        "--schema",
        metavar="SCHEMA_TOML",
        help="Path to a TOML schema file.  If omitted, --base-env is required.",
    )
    parser.add_argument(
        "--base-env",
        metavar="BASE_ENV",
        help="Derive schema from a base .env file (all keys treated as required).",
    )
    parser.add_argument(
        "--no-color", action="store_true", help="Disable ANSI colour output."
    )
    args = parser.parse_args(argv)

    env_path = Path(args.env_file)
    if not env_path.exists():
        print(f"error: env file not found: {env_path}", file=sys.stderr)
        return 2

    # Resolve schema
    if args.schema:
        schema_path = Path(args.schema)
        if not schema_path.exists():
            print(f"error: schema file not found: {schema_path}", file=sys.stderr)
            return 2
        schema = load_schema_from_toml(schema_path)
    elif args.base_env:
        base_path = Path(args.base_env)
        if not base_path.exists():
            print(f"error: base env file not found: {base_path}", file=sys.stderr)
            return 2
        schema = schema_from_base_env(base_path)
    else:
        print(
            "error: supply --schema or --base-env to define the schema.",
            file=sys.stderr,
        )
        return 2

    env = parse_env_file(env_path)
    result = validate_env(env, schema)

    print(format_validation(result, use_color=not args.no_color))
    return 0 if result.is_valid else 1
