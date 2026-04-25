"""Tests for patchwork_env.cli_export."""

import json
from pathlib import Path

import pytest

from patchwork_env.cli_export import run_export


@pytest.fixture()
def env_files(tmp_path: Path):
    base = tmp_path / ".env.base"
    target = tmp_path / ".env.target"
    base.write_text("HOST=localhost\nPORT=5432\nSHARED=same\n")
    target.write_text("HOST=prod.db\nPORT=5432\nNEWKEY=hello\nSHARED=same\n")
    return base, target, tmp_path


class _Args:
    def __init__(self, base, target, fmt="json", output=None):
        self.base = str(base)
        self.target = str(target)
        self.format = fmt
        self.output = output


def test_missing_base_returns_two(env_files):
    _, target, _ = env_files
    code = run_export(_Args("nonexistent.env", target))
    assert code == 2


def test_missing_target_returns_two(env_files):
    base, _, _ = env_files
    code = run_export(_Args(base, "nonexistent.env"))
    assert code == 2


def test_json_export_returns_zero(env_files, capsys):
    base, target, _ = env_files
    code = run_export(_Args(base, target, fmt="json"))
    assert code == 0


def test_json_output_is_valid(env_files, capsys):
    base, target, _ = env_files
    run_export(_Args(base, target, fmt="json"))
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "added" in data
    assert "changed" in data


def test_markdown_export_returns_zero(env_files, capsys):
    base, target, _ = env_files
    code = run_export(_Args(base, target, fmt="markdown"))
    assert code == 0


def test_markdown_output_contains_header(env_files, capsys):
    base, target, _ = env_files
    run_export(_Args(base, target, fmt="markdown"))
    captured = capsys.readouterr()
    assert "# Env Diff Report" in captured.out


def test_export_to_file(env_files):
    base, target, tmp = env_files
    out_file = tmp / "diff.json"
    code = run_export(_Args(base, target, fmt="json", output=str(out_file)))
    assert code == 0
    assert out_file.exists()
    data = json.loads(out_file.read_text())
    assert "changed" in data


def test_export_to_markdown_file(env_files):
    base, target, tmp = env_files
    out_file = tmp / "diff.md"
    code = run_export(_Args(base, target, fmt="markdown", output=str(out_file)))
    assert code == 0
    content = out_file.read_text()
    assert "# Env Diff Report" in content
