"""Tests for cli_patch.run_patch."""

import pytest
from pathlib import Path

from patchwork_env.cli_patch import run_patch


@pytest.fixture
def env_files(tmp_path):
    base = tmp_path / "base.env"
    target = tmp_path / "target.env"
    output = tmp_path / "output.env"
    return base, target, output


def _write(path: Path, content: str):
    path.write_text(content)


def test_no_diff_returns_zero(env_files):
    base, target, output = env_files
    _write(base, "KEY=value\nFOO=bar\n")
    _write(target, "KEY=value\nFOO=bar\n")
    assert run_patch(str(base), str(target), quiet=True) == 0


def test_patch_applied_returns_one(env_files):
    base, target, output = env_files
    _write(base, "KEY=value\nNEW_KEY=added\n")
    _write(target, "KEY=value\n")
    result = run_patch(str(base), str(target), output_path=str(output), quiet=True)
    assert result == 1


def test_patch_writes_output_file(env_files):
    base, target, output = env_files
    _write(base, "KEY=value\nNEW_KEY=added\n")
    _write(target, "KEY=value\n")
    run_patch(str(base), str(target), output_path=str(output), quiet=True)
    assert output.exists()
    content = output.read_text()
    assert "NEW_KEY" in content


def test_merge_keeps_target_values(env_files):
    base, target, output = env_files
    _write(base, "KEY=base_value\n")
    _write(target, "KEY=target_value\n")
    run_patch(str(base), str(target), output_path=str(output), strategy="merge", quiet=True)
    assert "target_value" in output.read_text()


def test_overwrite_applies_base_values(env_files):
    base, target, output = env_files
    _write(base, "KEY=base_value\n")
    _write(target, "KEY=target_value\n")
    run_patch(str(base), str(target), output_path=str(output), strategy="overwrite", quiet=True)
    assert "base_value" in output.read_text()


def test_missing_base_returns_two(env_files):
    base, target, _ = env_files
    _write(target, "KEY=value\n")
    assert run_patch(str(base), str(target), quiet=True) == 2


def test_missing_target_returns_two(env_files):
    base, target, _ = env_files
    _write(base, "KEY=value\n")
    assert run_patch(str(base), str(target), quiet=True) == 2


def test_invalid_strategy_returns_three(env_files):
    base, target, _ = env_files
    _write(base, "KEY=value\n")
    _write(target, "KEY=value\n")
    assert run_patch(str(base), str(target), strategy="bogus", quiet=True) == 3


def test_patch_defaults_to_overwrite_target_in_place(env_files):
    base, target, _ = env_files
    _write(base, "KEY=value\nEXTRA=added\n")
    _write(target, "KEY=value\n")
    run_patch(str(base), str(target), quiet=True)
    assert "EXTRA" in target.read_text()
