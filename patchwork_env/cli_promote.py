"""CLI entry point for the promote subcommand."""

import argparse
import sys
from pathlib import Path

from patchwork_env.parser import parse_env_file
from patchwork_env.promoter import promote_env
from patchwork_env.reconciler import to_env_string


def run_promote(args: argparse.Namespace) -> int:
    source_path = Path(args.source)
    target_path = Path(args.target)

    if not source_path.exists():
        print(f"error: source file not found: {source_path}", file=sys.stderr)
        return 2

    if not target_path.exists():
        print(f"error: target file not found: {target_path}", file=sys.stderr)
        return 2

    source = parse_env_file(str(source_path))
    target = parse_env_file(str(target_path))

    keys = args.keys if args.keys else None
    prefix = args.prefix or None

    result = promote_env(
        source,
        target,
        keys=keys,
        overwrite=args.overwrite,
        prefix=prefix,
    )

    if args.verbose:
        print(result.summary())
        if result.overwritten:
            print("\nOverwritten:")
            for k, (old, new) in result.overwritten.items():
                print(f"  {k}: {old!r} -> {new!r}")
        if result.not_found:
            print("\nNot found in source:")
            for k in result.not_found:
                print(f"  {k}")

    if not result.has_changes():
        print("Nothing to promote.")
        return 0

    merged = dict(target)
    merged.update(result.promoted)

    output_path = Path(args.output) if args.output else target_path
    output_path.write_text(to_env_string(merged))
    print(f"Promoted {len(result.promoted)} key(s) -> {output_path}")
    return 1


def add_promote_subparser(subparsers) -> None:
    p = subparsers.add_parser("promote", help="Promote env values from source to target")
    p.add_argument("source", help="Source .env file")
    p.add_argument("target", help="Target .env file")
    p.add_argument("--keys", nargs="+", metavar="KEY", help="Specific keys to promote")
    p.add_argument("--prefix", help="Only promote keys with this prefix")
    p.add_argument("--overwrite", action="store_true", help="Overwrite existing keys in target")
    p.add_argument("--output", "-o", help="Write result to this file (default: overwrite target)")
    p.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    p.set_defaults(func=run_promote)
