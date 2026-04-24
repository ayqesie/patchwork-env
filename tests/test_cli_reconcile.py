"""Tests for cli_reconcile.run_reconcile."""

import pytest
from pathlib import Path

from patchwork_env.cli_reconcile import run_reconcile


@pytest.fixture
def env_files(tmp_path):
    base = tmp_path / "base.env"
    target = tmp_path / "target.env"
    output = tmp_path / "output.env"
    return base, target, output


def test_no_diff_returns_zero(env_files):
    base, target, _ = env_files
    base.write_text("FOO=bar\nBAZ=qux\n")
    target.write_text("FOO=bar\nBAZ=qux\n")
    assert run_reconcile(str(base), str(target)) == 0


def test_diff_found_returns_one(env_files):
    base, target, _ = env_files
    base.write_text("FOO=bar\nNEW=value\n")
    target.write_text("FOO=bar\n")
    assert run_reconcile(str(base), str(target), dry_run=True) == 1


def test_missing_base_returns_two(env_files):
    _, target, _ = env_files
    target.write_text("FOO=bar\n")
    assert run_reconcile("nonexistent.env", str(target)) == 2


def test_missing_target_returns_two(env_files):
    base, _, _ = env_files
    base.write_text("FOO=bar\n")
    assert run_reconcile(str(base), "nonexistent.env") == 2


def test_invalid_strategy_returns_two(env_files):
    base, target, _ = env_files
    base.write_text("FOO=bar\n")
    target.write_text("FOO=baz\n")
    assert run_reconcile(str(base), str(target), strategy="bogus") == 2


def test_writes_to_output_path(env_files):
    base, target, output = env_files
    base.write_text("FOO=bar\nNEW=added\n")
    target.write_text("FOO=bar\n")
    result = run_reconcile(str(base), str(target), output_path=str(output))
    assert result == 1
    assert output.exists()
    content = output.read_text()
    assert "NEW" in content


def test_dry_run_does_not_write(env_files):
    base, target, output = env_files
    base.write_text("FOO=bar\nEXTRA=yes\n")
    target.write_text("FOO=bar\n")
    run_reconcile(str(base), str(target), output_path=str(output), dry_run=True)
    assert not output.exists()


def test_overwrites_target_by_default(env_files):
    base, target, _ = env_files
    base.write_text("FOO=frombase\nNEW=added\n")
    target.write_text("FOO=fromtarget\n")
    run_reconcile(str(base), str(target), strategy="merge")
    content = target.read_text()
    assert "NEW" in content
    # merge keeps target value for conflicts
    assert "fromtarget" in content
