"""CLI entry point for the `patchwork-env validate` subcommand."""

import sys
from typing import Optional

from patchwork_env.parser import parse_env_file
from patchwork_env.schema_loader import load_schema_from_toml, schema_from_base_env
from patchwork_env.validator import validate


def run_validate(
    env_path: str,
    schema_path: Optional[str] = None,
    base_env_path: Optional[str] = None,
    strict: bool = False,
) -> int:
    """
    Validate an env file against a schema or a base env.

    Returns exit code: 0 = valid, 1 = invalid, 2 = usage error.
    """
    if schema_path and base_env_path:
        print("Error: provide either --schema or --base, not both.", file=sys.stderr)
        return 2

    try:
        env = parse_env_file(env_path)
    except FileNotFoundError:
        print(f"Error: env file not found: {env_path}", file=sys.stderr)
        return 2

    if schema_path:
        try:
            schema = load_schema_from_toml(schema_path)
        except FileNotFoundError:
            print(f"Error: schema file not found: {schema_path}", file=sys.stderr)
            return 2
    elif base_env_path:
        try:
            base_env = parse_env_file(base_env_path)
        except FileNotFoundError:
            print(f"Error: base env file not found: {base_env_path}", file=sys.stderr)
            return 2
        schema = schema_from_base_env(base_env)
    else:
        print("Error: provide --schema or --base.", file=sys.stderr)
        return 2

    result = validate(env, schema)

    if strict and result.unknown_keys:
        print(f"Strict mode: unknown keys found: {', '.join(sorted(result.unknown_keys))}")
        return 1

    print(result.summary())
    return 0 if result.is_valid else 1
