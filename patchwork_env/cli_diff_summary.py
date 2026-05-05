"""CLI entry point for the multi-file diff summary command."""

import argparse
import sys
from typing import List

from patchwork_env.differ_summary import build_multi_diff
from patchwork_env.formatter import format_diff


def _parse_pairs(args_pairs: List[str]):
    """Parse 'base:target' strings into (base, target) tuples."""
    pairs = []
    for token in args_pairs:
        if ":" not in token:
            print(f"[error] invalid pair '{token}' — expected base:target format", file=sys.stderr)
            sys.exit(2)
        base, _, target = token.partition(":")
        pairs.append((base.strip(), target.strip()))
    return pairs


def run_diff_summary(args: argparse.Namespace) -> int:
    pairs = _parse_pairs(args.pairs)

    missing = []
    for base, target in pairs:
        import os
        if not os.path.isfile(base):
            missing.append(base)
        if not os.path.isfile(target):
            missing.append(target)

    if missing:
        for path in missing:
            print(f"[error] file not found: {path}", file=sys.stderr)
        return 2

    report = build_multi_diff(pairs)
    print(report.summary())

    if args.verbose:
        for base_name, target_name, d in report.comparisons:
            print(f"\n--- {base_name} vs {target_name} ---")
            print(format_diff(d, base_label=base_name, target_label=target_name))

    changed_counts = report.all_changed_keys()
    if changed_counts and args.hotspots:
        print("\nHotspot keys (changed in multiple pairs):")
        hot = sorted(changed_counts.items(), key=lambda x: -x[1])
        for key, count in hot:
            if count > 1:
                print(f"  {key}: {count} pair(s)")

    return 1 if report.pairs_with_diff() > 0 else 0


def add_diff_summary_subparser(subparsers):
    p = subparsers.add_parser(
        "diff-summary",
        help="Summarise diffs across multiple base:target env file pairs",
    )
    p.add_argument(
        "pairs",
        nargs="+",
        metavar="BASE:TARGET",
        help="One or more base:target file pairs",
    )
    p.add_argument("-v", "--verbose", action="store_true", help="Show full diff per pair")
    p.add_argument("--hotspots", action="store_true", help="Show keys changed in multiple pairs")
    p.set_defaults(func=run_diff_summary)
    return p
