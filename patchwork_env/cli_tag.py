"""CLI entry-point for the tag subcommand."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .parser import parse_env_file
from .tagger import tag_env, tag_by_prefix


def _parse_tag_pair(raw: str):
    """Parse 'KEY=tag' into (key, tag).  Raises ValueError on bad input."""
    if "=" not in raw:
        raise ValueError(f"Expected KEY=tag, got: {raw!r}")
    key, _, tag = raw.partition("=")
    return key.strip(), tag.strip()


def run_tag(args: argparse.Namespace) -> int:
    env_path = Path(args.env_file)
    if not env_path.exists():
        print(f"error: file not found: {env_path}", file=sys.stderr)
        return 2

    env = parse_env_file(str(env_path))

    if args.prefix:
        prefix_tags: dict[str, str] = {}
        for raw in args.prefix:
            try:
                prefix, tag = _parse_tag_pair(raw)
                prefix_tags[prefix] = tag
            except ValueError as exc:
                print(f"error: {exc}", file=sys.stderr)
                return 2
        result = tag_by_prefix(env, prefix_tags)
    else:
        tag_map: dict[str, list[str]] = {}
        for raw in (args.tag or []):
            try:
                key, tag = _parse_tag_pair(raw)
                tag_map.setdefault(key, []).append(tag)
            except ValueError as exc:
                print(f"error: {exc}", file=sys.stderr)
                return 2
        result = tag_env(env, tag_map)

    print(result.summary())

    if args.show_tagged and result.tagged:
        print("\nTagged keys:")
        for key, tags in sorted(result.tagged.items()):
            print(f"  {key}: {', '.join(tags)}")

    if args.show_untagged and result.untagged:
        print("\nUntagged keys:")
        for key in sorted(result.untagged):
            print(f"  {key}")

    return 0 if result.has_tags() else 1


def add_tag_subparser(subparsers) -> None:
    p = subparsers.add_parser("tag", help="tag env keys with labels")
    p.add_argument("env_file", help="path to .env file")
    p.add_argument(
        "--tag",
        metavar="KEY=label",
        action="append",
        help="assign a tag to a specific key (repeatable)",
    )
    p.add_argument(
        "--prefix",
        metavar="PREFIX=label",
        action="append",
        help="auto-tag keys matching a prefix (repeatable)",
    )
    p.add_argument("--show-tagged", action="store_true", help="print tagged keys")
    p.add_argument("--show-untagged", action="store_true", help="print untagged keys")
    p.set_defaults(func=run_tag)
