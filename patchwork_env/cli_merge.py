"""CLI command for merging multiple .env files into one."""

import argparse
import sys
from pathlib import Path

from .merger import merge_env_files
from .formatter import _colorize


def run_merge(args: argparse.Namespace) -> int:
    """Merge two or more .env files and write the result to an output file.

    Returns:
        0 — merge succeeded with no conflicts
        1 — merge succeeded but conflicts were detected (last-wins applied)
        2 — usage error (missing files, bad args)
    """
    input_paths = [Path(p) for p in args.inputs]

    # Validate all input files exist
    for path in input_paths:
        if not path.exists():
            print(
                _colorize(f"error: file not found: {path}", "red"),
                file=sys.stderr,
            )
            return 2

    if len(input_paths) < 2:
        print(
            _colorize("error: at least two input files are required", "red"),
            file=sys.stderr,
        )
        return 2

    # Run the merge
    result = merge_env_files(*input_paths)

    # Determine output destination
    output_path = Path(args.output) if args.output else None

    # Build the output content
    lines = []
    for key, value in result.merged.items():
        lines.append(f"{key}={value}")
    output_content = "\n".join(lines) + ("\n" if lines else "")

    # Write output
    if output_path:
        output_path.write_text(output_content)
        print(_colorize(f"merged output written to {output_path}", "green"))
    else:
        print(output_content, end="")

    # Report conflicts
    if result.has_conflicts():
        print(
            _colorize(
                f"\nwarning: {len(result.conflicts)} conflict(s) resolved using last-wins strategy:",
                "yellow",
            ),
            file=sys.stderr,
        )
        for key, sources in result.conflicts.items():
            values_str = " -> ".join(f"{s}: {v!r}" for s, v in sources)
            print(
                _colorize(f"  {key}: {values_str}", "yellow"),
                file=sys.stderr,
            )
        return 1

    return 0


def add_merge_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'merge' subcommand."""
    parser = subparsers.add_parser(
        "merge",
        help="merge multiple .env files into one (last-wins on conflicts)",
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        metavar="FILE",
        help="two or more .env files to merge (in order of priority)",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="OUTPUT",
        default=None,
        help="write merged result to this file (default: stdout)",
    )
    parser.set_defaults(func=run_merge)
