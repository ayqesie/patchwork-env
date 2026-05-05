"""Tests for patchwork_env.cli_diff_summary."""

import argparse
import pytest

from patchwork_env.cli_diff_summary import run_diff_summary, _parse_pairs


@pytest.fixture
def env_files(tmp_path):
    base = tmp_path / "base.env"
    staging = tmp_path / "staging.env"
    prod = tmp_path / "prod.env"
    base.write_text("FOO=bar\nSHARED=same\n")
    staging.write_text("FOO=baz\nSHARED=same\nNEW=yes\n")
    prod.write_text("FOO=bar\nSHARED=same\n")
    return {"base": str(base), "staging": str(staging), "prod": str(prod)}


def _args(pairs, verbose=False, hotspots=False):
    ns = argparse.Namespace(pairs=pairs, verbose=verbose, hotspots=hotspots)
    return ns


def test_no_diff_returns_zero(env_files):
    pair = f"{env_files['base']}:{env_files['prod']}"
    code = run_diff_summary(_args([pair]))
    assert code == 0


def test_diff_found_returns_one(env_files):
    pair = f"{env_files['base']}:{env_files['staging']}"
    code = run_diff_summary(_args([pair]))
    assert code == 1


def test_missing_base_returns_two(env_files, tmp_path):
    missing = str(tmp_path / "ghost.env")
    pair = f"{missing}:{env_files['staging']}"
    code = run_diff_summary(_args([pair]))
    assert code == 2


def test_missing_target_returns_two(env_files, tmp_path):
    missing = str(tmp_path / "ghost.env")
    pair = f"{env_files['base']}:{missing}"
    code = run_diff_summary(_args([pair]))
    assert code == 2


def test_multiple_pairs(env_files):
    p1 = f"{env_files['base']}:{env_files['staging']}"
    p2 = f"{env_files['base']}:{env_files['prod']}"
    code = run_diff_summary(_args([p1, p2]))
    assert code == 1


def test_verbose_flag_runs_without_error(env_files, capsys):
    pair = f"{env_files['base']}:{env_files['staging']}"
    code = run_diff_summary(_args([pair], verbose=True))
    out = capsys.readouterr().out
    assert "---" in out
    assert code == 1


def test_parse_pairs_valid():
    result = _parse_pairs(["a.env:b.env", "c.env:d.env"])
    assert result == [("a.env", "b.env"), ("c.env", "d.env")]


def test_parse_pairs_invalid_exits():
    with pytest.raises(SystemExit) as exc:
        _parse_pairs(["no-colon-here"])
    assert exc.value.code == 2
