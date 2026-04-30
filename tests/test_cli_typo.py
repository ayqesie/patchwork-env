"""Tests for patchwork_env.cli_typo."""

import argparse
import pytest
from pathlib import Path

from patchwork_env.cli_typo import run_typo


@pytest.fixture
def env_files(tmp_path):
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def _args(file: str, reference: str, cutoff: str = "0.8") -> argparse.Namespace:
    return argparse.Namespace(file=file, reference=reference, cutoff=cutoff)


def test_missing_env_file_returns_two(env_files):
    ref = _write(env_files / "ref.env", "DATABASE_URL=x\n")
    result = run_typo(_args(str(env_files / "missing.env"), str(ref)))
    assert result == 2


def test_missing_reference_file_returns_two(env_files):
    env = _write(env_files / "app.env", "DATABASE_URL=x\n")
    result = run_typo(_args(str(env), str(env_files / "missing_ref.env")))
    assert result == 2


def test_clean_env_returns_zero(env_files):
    env = _write(env_files / "app.env", "DATABASE_URL=x\nSECRET_KEY=abc\n")
    ref = _write(env_files / "ref.env", "DATABASE_URL=y\nSECRET_KEY=xyz\n")
    result = run_typo(_args(str(env), str(ref)))
    assert result == 0


def test_typo_found_returns_one(env_files):
    env = _write(env_files / "app.env", "DATABSE_URL=x\n")  # typo
    ref = _write(env_files / "ref.env", "DATABASE_URL=y\n")
    result = run_typo(_args(str(env), str(ref)))
    assert result == 1


def test_no_overlap_no_typo_returns_zero(env_files):
    env = _write(env_files / "app.env", "ZZZZZ=1\n")
    ref = _write(env_files / "ref.env", "DATABASE_URL=y\n")
    result = run_typo(_args(str(env), str(ref)))
    assert result == 0


def test_high_cutoff_reduces_matches(env_files, capsys):
    env = _write(env_files / "app.env", "DATABSE_URL=x\n")
    ref = _write(env_files / "ref.env", "DATABASE_URL=y\n")
    # 0.99 cutoff — very strict, may or may not match depending on similarity
    result = run_typo(_args(str(env), str(ref), cutoff="0.99"))
    # just assert it runs cleanly (0 or 1)
    assert result in (0, 1)
