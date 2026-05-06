"""cli_mask.py — CLI interface for the masker module."""
from __future__ import annotations

import argparse
import sys

from patchwork_env.parser import parse_env_file
from patchwork_env.masker import mask_env
from patchwork_env.reconciler import to_env_string


def run_mask(args: argparse.Namespace) -> int:
    """Entry point for ``patchwork-env mask``.

    Returns:
        0  — success, nothing to mask or output written
        1  — keys were masked (useful for CI detection)
        2  — input error (missing file, etc.)
    """
    try:
        env = parse_env_file(args.file)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        print(f"error: could not parse {args.file}: {exc}", file=sys.stderr)
        return 2

    explicit_keys = list(args.keys) if args.keys else []
    result = mask_env(
        env,
        keys=explicit_keys,
        auto_detect=not args.no_auto,
        mask_value=args.mask_value,
    )

    print(result.summary())

    if args.output:
        _write_masked_output(result.masked, args.output)
    elif args.print:
        print(to_env_string(result.masked))

    return 1 if result.has_masked() else 0


def _write_masked_output(masked: dict, output_path: str) -> int:
    """Write masked env content to *output_path*.

    Args:
        masked: Mapping of env keys to (possibly masked) values.
        output_path: Destination file path.

    Returns:
        0 on success, 2 on write error.
    """
    content = to_env_string(masked)
    try:
        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write(content)
        print(f"masked env written to {output_path}")
        return 0
    except OSError as exc:
        print(f"error: could not write output: {exc}", file=sys.stderr)
        return 2


def add_mask_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "mask",
        help="Mask sensitive values in an env file.",
    )
    p.add_argument("file", help="Path to the .env file.")
    p.add_argument(
        "--keys",
        nargs="+",
        metavar="KEY",
        help="Additional keys to mask explicitly.",
    )
    p.add_argument(
        "--no-auto",
        action="store_true",
        default=False,
        help="Disable auto-detection of sensitive key names.",
    )
    p.add_argument(
        "--mask-value",
        default="***",
        metavar="STR",
        help="Replacement string for masked values (default: ***).",
    )
    p.add_argument(
        "--output",
        metavar="FILE",
        help="Write masked env to this file.",
    )
    p.add_argument(
        "--print",
        action="store_true",
        default=False,
        help="Print masked env to stdout.",
    )
    p.set_defaults(func=run_mask)
