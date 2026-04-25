"""CLI entry point for the audit command."""

import sys
from pathlib import Path

from patchwork_env.parser import parse_env_file
from patchwork_env.auditor import audit_env
from patchwork_env.formatter import format_audit


def run_audit(env_path: str, strict: bool = False) -> int:
    """Audit an env file for common issues.

    Returns:
        0 — no issues found
        1 — issues found
        2 — file not found or parse error
    """
    path = Path(env_path)
    if not path.exists():
        print(f"error: file not found: {env_path}", file=sys.stderr)
        return 2

    try:
        raw_lines = path.read_text().splitlines()
        env = parse_env_file(str(path))
    except Exception as exc:  # noqa: BLE001
        print(f"error: could not parse {env_path}: {exc}", file=sys.stderr)
        return 2

    result = audit_env(env, raw_lines=raw_lines)
    print(format_audit(result, env_path))

    if result.has_issues():
        if strict and result.suspicious_values:
            return 1
        if not strict:
            return 1

    return 0
