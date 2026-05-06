"""CLI entry point for the encrypt subcommand."""

from __future__ import annotations

import argparse
import sys

from patchwork_env.encryptor import decrypt_env, encrypt_env, generate_key
from patchwork_env.formatter import _colorize
from patchwork_env.parser import parse_env_file
from patchwork_env.reconciler import to_env_string


def run_encrypt(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.file)
    except FileNotFoundError:
        print(_colorize(f"Error: file not found: {args.file}", "red"), file=sys.stderr)
        return 2

    if args.generate_key:
        try:
            key = generate_key()
        except RuntimeError as exc:
            print(_colorize(str(exc), "red"), file=sys.stderr)
            return 2
        print(f"Generated key: {key}")
        return 0

    if not args.key:
        print(_colorize("Error: --key is required (or use --generate-key)", "red"), file=sys.stderr)
        return 2

    try:
        if args.decrypt:
            result_env = decrypt_env(env, args.key)
            output = to_env_string(result_env)
            if args.output:
                with open(args.output, "w") as fh:
                    fh.write(output)
            else:
                print(output)
            print(_colorize(f"Decrypted {len(result_env)} key(s).", "green"))
        else:
            result = encrypt_env(env, args.key, sensitive_only=not args.all)
            merged = {**env, **result.encrypted}
            output = to_env_string(merged)
            if args.output:
                with open(args.output, "w") as fh:
                    fh.write(output)
            else:
                print(output)
            print(_colorize(result.summary(), "green"))
            if not result.has_encrypted():
                return 1
    except RuntimeError as exc:
        print(_colorize(str(exc), "red"), file=sys.stderr)
        return 2

    return 0


def add_encrypt_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("encrypt", help="Encrypt or decrypt sensitive values in a .env file")
    p.add_argument("file", nargs="?", default=".env", help="Path to .env file")
    p.add_argument("--key", default="", help="Fernet key for encryption/decryption")
    p.add_argument("--generate-key", action="store_true", help="Generate and print a new Fernet key")
    p.add_argument("--decrypt", action="store_true", help="Decrypt instead of encrypt")
    p.add_argument("--all", action="store_true", help="Encrypt all keys, not just sensitive ones")
    p.add_argument("--output", default="", help="Write result to this file instead of stdout")
    p.set_defaults(func=run_encrypt)
