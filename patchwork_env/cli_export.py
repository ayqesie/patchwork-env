"""CLI entry point for the `patchwork-env export` command."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from patchwork_env.differ import diff_envs
from patchwork_env.exporter import export_json, export_markdown, export_toml
from patchwork_env.parser import parse_env_file

_FORMATS = ("json", "markdown", "toml")


def run_export(args: argparse.Namespace) -> int:
    """Run the export command.  Returns an exit code."""
    base_path = Path(args.base)
    target_path = Path(args.target)

    for p in (base_path, target_path):
        if not p.exists():
            print(f"error: file not found: {p}", file=sys.stderr)
            return 2

    base_env = parse_env_file(base_path)
    target_env = parse_env_file(target_path)
    diff = diff_envs(base_env, target_env)

    fmt: str = args.format.lower()
    try:
        if fmt == "json":
            output = export_json(diff)
        elif fmt == "toml":
            output = export_toml(diff)
        elif fmt == "markdown":
            output = export_markdown(
                diff,
                base_label=base_path.name,
                target_label=target_path.name,
            )
        else:
            print(f"error: unknown format '{fmt}'. Choose from: {', '.join(_FORMATS)}", file=sys.stderr)
            return 2
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.output:
        out_path = Path(args.output)
        out_path.write_text(output, encoding="utf-8")
        print(f"Exported to {out_path}")
    else:
        print(output)

    return 0


def add_export_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("export", help="Export diff to JSON, TOML, or Markdown")
    p.add_argument("base", help="Base .env file")
    p.add_argument("target", help="Target .env file")
    p.add_argument(
        "--format", "-f",
        default="json",
        choices=_FORMATS,
        help="Output format (default: json)",
    )
    p.add_argument(
        "--output", "-o",
        default=None,
        help="Write output to this file instead of stdout",
    )
    p.set_defaults(func=run_export)
