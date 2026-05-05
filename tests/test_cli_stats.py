"""Tests for patchwork_env.cli_stats."""
import argparse
import pytest
from pathlib import Path
from patchwork_env.cli_stats import run_stats


@pytest.fixture
def env_files(tmp_path):
    base = tmp_path / "base.env"
    base.write_text("PORT=8080\nDEBUG=true\nSECRET=\n")
    other = tmp_path / "other.env"
    other.write_text("HOST=localhost\nRETRIES=3\n")
    return base, other


def _args(files, verbose=False, aggregate=False):
    ns = argparse.Namespace()
    ns.files = [str(f) for f in files]
    ns.verbose = verbose
    ns.aggregate = aggregate
    return ns


def test_single_file_returns_zero(env_files):
    base, _ = env_files
    assert run_stats(_args([base])) == 0


def test_missing_file_returns_two(tmp_path):
    missing = tmp_path / "ghost.env"
    assert run_stats(_args([missing])) == 2


def test_multiple_files_returns_zero(env_files):
    base, other = env_files
    assert run_stats(_args([base, other])) == 0


def test_verbose_flag_accepted(env_files):
    base, _ = env_files
    assert run_stats(_args([base], verbose=True)) == 0


def test_aggregate_flag_accepted(env_files):
    base, other = env_files
    assert run_stats(_args([base, other], aggregate=True)) == 0


def test_output_contains_total(env_files, capsys):
    base, _ = env_files
    run_stats(_args([base]))
    out = capsys.readouterr().out
    assert "total=" in out


def test_verbose_output_contains_empty(env_files, capsys):
    base, _ = env_files
    run_stats(_args([base], verbose=True))
    out = capsys.readouterr().out
    assert "empty:" in out


def test_aggregate_output_contains_aggregate_header(env_files, capsys):
    base, other = env_files
    run_stats(_args([base, other], aggregate=True))
    out = capsys.readouterr().out
    assert "aggregate" in out
