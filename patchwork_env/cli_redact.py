"""CLI entry point for the `redact` subcommand."""

from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

from patchwork_env.parser import parse_env_file
from patchwork_env.redactor import redact_env
from patchwork_env.formatter import _colorize


def run_redact(args: Namespace) -> int:
    """Run the redact command. Returns an exit code.

    Exit codes:
        0 — success, no sensitive keys found
        1 — success, sensitive keys were redacted
        2 — error (missing file, parse error)
    """
    env_path = Path(args.env_file)
    if not env_path.exists():
        print(f"Error: file not found: {env_path}", file=sys.stderr)
        return 2

    try:
        env = parse_env_file(str(env_path))
    except Exception as exc:  # noqa: BLE001
        print(f"Error parsing {env_path}: {exc}", file=sys.stderr)
        return 2

    extra = list(args.extra_keys) if args.extra_keys else []
    result = redact_env(env, extra_keys=extra)

    if args.output:
        out_path = Path(args.output)
        lines = [f"{k}={v}" for k, v in result.redacted.items()]
        out_path.write_text("\n".join(lines) + "\n")
        print(f"Redacted env written to {out_path}")
    else:
        for key, value in result.redacted.items():
            print(f"{key}={value}")

    if result.redacted_keys:
        msg = _colorize(result.summary(), "yellow")
        print(msg, file=sys.stderr)
        return 1

    return 0


def add_redact_subparser(subparsers) -> None:  # type: ignore[type-arg]
    p: ArgumentParser = subparsers.add_parser(
        "redact",
        help="Redact sensitive values from an env file.",
    )
    p.add_argument("env_file", help="Path to the .env file to redact.")
    p.add_argument(
        "--extra-keys",
        nargs="+",
        metavar="KEY",
        help="Additional key names to force-redact.",
    )
    p.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        help="Write redacted output to FILE instead of stdout.",
    )
    p.set_defaults(func=run_redact)
