"""CLI entry point for diffing two .env files."""

import sys
from pathlib import Path

from patchwork_env.parser import parse_env_file
from patchwork_env.differ import diff_envs
from patchwork_env.formatter import format_diff, format_summary


def run_diff(args=None):
    """
    Run the diff command.

    Expected args: [base_file, target_file, --summary, --no-color]
    Returns exit code: 0 if no diff, 1 if diff found, 2 on error.
    """
    import argparse

    parser = argparse.ArgumentParser(
        prog="patchwork-env diff",
        description="Diff two .env files and show what changed.",
    )
    parser.add_argument("base", help="Base .env file (e.g. .env.production)")
    parser.add_argument("target", help="Target .env file to compare against base")
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a short summary instead of full diff",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )

    parsed = parser.parse_args(args)

    base_path = Path(parsed.base)
    target_path = Path(parsed.target)

    if not base_path.exists():
        print(f"Error: base file not found: {base_path}", file=sys.stderr)
        return 2

    if not target_path.exists():
        print(f"Error: target file not found: {target_path}", file=sys.stderr)
        return 2

    base_env = parse_env_file(base_path)
    target_env = parse_env_file(target_path)

    diff = diff_envs(base_env, target_env)
    use_color = not parsed.no_color

    if parsed.summary:
        print(format_summary(diff, use_color=use_color))
    else:
        print(format_diff(diff, base_label=str(base_path), target_label=str(target_path), use_color=use_color))

    return 1 if diff.has_diff() else 0


if __name__ == "__main__":
    sys.exit(run_diff())
