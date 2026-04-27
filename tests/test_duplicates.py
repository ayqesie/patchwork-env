"""Tests for patchwork_env.duplicates and cli_duplicates."""

import argparse
import pytest
from pathlib import Path

from patchwork_env.duplicates import find_duplicates, DuplicateResult
from patchwork_env.cli_duplicates import run_duplicates


# --- find_duplicates unit tests ---

def test_no_duplicates_clean():
    text = "FOO=bar\nBAZ=qux\n"
    result = find_duplicates(text)
    assert not result.has_issues()


def test_single_duplicate_key():
    text = "FOO=first\nFOO=second\n"
    result = find_duplicates(text)
    assert result.has_issues()
    assert "FOO" in result.duplicates
    assert result.duplicates["FOO"] == ["first", "second"]


def test_triple_duplicate_key():
    text = "KEY=a\nKEY=b\nKEY=c\n"
    result = find_duplicates(text)
    assert len(result.duplicates["KEY"]) == 3


def test_multiple_duplicate_keys():
    text = "A=1\nB=2\nA=3\nB=4\n"
    result = find_duplicates(text)
    assert set(result.all_duplicate_keys()) == {"A", "B"}


def test_comments_ignored():
    text = "# FOO=bar\nFOO=real\n"
    result = find_duplicates(text)
    assert not result.has_issues()


def test_blank_lines_ignored():
    text = "\nFOO=bar\n\nBAZ=qux\n"
    result = find_duplicates(text)
    assert not result.has_issues()


def test_summary_no_issues():
    result = DuplicateResult()
    assert "No duplicate" in result.summary()


def test_summary_with_issues():
    result = DuplicateResult(duplicates={"FOO": ["a", "b"]})
    assert "FOO" in result.summary()
    assert "Duplicate" in result.summary()


# --- CLI tests ---

@pytest.fixture
def env_files(tmp_path):
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def _args(file: str) -> argparse.Namespace:
    return argparse.Namespace(file=file)


def test_missing_file_returns_two(env_files):
    result = run_duplicates(_args(str(env_files / "missing.env")))
    assert result == 2


def test_clean_env_returns_zero(env_files):
    f = _write(env_files / ".env", "FOO=bar\nBAZ=qux\n")
    assert run_duplicates(_args(str(f))) == 0


def test_duplicate_key_returns_one(env_files):
    f = _write(env_files / ".env", "FOO=first\nFOO=second\n")
    assert run_duplicates(_args(str(f))) == 1
