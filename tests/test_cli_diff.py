"""Tests for the diff CLI command."""

import pytest
from pathlib import Path

from patchwork_env.cli_diff import run_diff


@pytest.fixture
def env_files(tmp_path):
    base = tmp_path / ".env.base"
    target = tmp_path / ".env.target"
    return base, target


def test_no_diff_returns_zero(env_files):
    base, target = env_files
    base.write_text("FOO=bar\nBAZ=qux\n")
    target.write_text("FOO=bar\nBAZ=qux\n")
    result = run_diff([str(base), str(target), "--no-color"])
    assert result == 0


def test_diff_found_returns_one(env_files):
    base, target = env_files
    base.write_text("FOO=bar\n")
    target.write_text("FOO=changed\n")
    result = run_diff([str(base), str(target), "--no-color"])
    assert result == 1


def test_missing_base_returns_two(env_files, tmp_path):
    _, target = env_files
    target.write_text("FOO=bar\n")
    result = run_diff([str(tmp_path / "nonexistent.env"), str(target), "--no-color"])
    assert result == 2


def test_missing_target_returns_two(env_files):
    base, target = env_files
    base.write_text("FOO=bar\n")
    result = run_diff([str(base), str(target), "--no-color"])
    assert result == 2


def test_summary_flag_runs_without_error(env_files, capsys):
    base, target = env_files
    base.write_text("FOO=bar\nREMOVED=yes\n")
    target.write_text("FOO=bar\nADDED=yes\n")
    result = run_diff([str(base), str(target), "--summary", "--no-color"])
    captured = capsys.readouterr()
    assert result == 1
    assert len(captured.out) > 0


def test_output_contains_file_labels(env_files, capsys):
    base, target = env_files
    base.write_text("KEY=one\n")
    target.write_text("KEY=two\n")
    run_diff([str(base), str(target), "--no-color"])
    captured = capsys.readouterr()
    assert str(base) in captured.out or str(target) in captured.out


def test_added_key_shown_in_output(env_files, capsys):
    base, target = env_files
    base.write_text("EXISTING=yes\n")
    target.write_text("EXISTING=yes\nNEW_KEY=hello\n")
    run_diff([str(base), str(target), "--no-color"])
    captured = capsys.readouterr()
    assert "NEW_KEY" in captured.out


def test_removed_key_shown_in_output(env_files, capsys):
    base, target = env_files
    base.write_text("GONE=bye\nKEEP=yes\n")
    target.write_text("KEEP=yes\n")
    run_diff([str(base), str(target), "--no-color"])
    captured = capsys.readouterr()
    assert "GONE" in captured.out
