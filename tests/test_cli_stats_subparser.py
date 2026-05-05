"""Integration-level tests: stats subparser wired into the main CLI parser."""
import argparse
import pytest
from patchwork_env.cli_stats import add_stats_subparser


@pytest.fixture
def parser():
    root = argparse.ArgumentParser(prog="patchwork-env")
    sub = root.add_subparsers(dest="command")
    add_stats_subparser(sub)
    return root


def test_stats_subcommand_registered(parser):
    ns = parser.parse_args(["stats", "a.env"])
    assert ns.command == "stats"


def test_stats_files_captured(parser):
    ns = parser.parse_args(["stats", "a.env", "b.env"])
    assert ns.files == ["a.env", "b.env"]


def test_verbose_default_false(parser):
    ns = parser.parse_args(["stats", "a.env"])
    assert ns.verbose is False


def test_verbose_flag_sets_true(parser):
    ns = parser.parse_args(["stats", "--verbose", "a.env"])
    assert ns.verbose is True


def test_aggregate_default_false(parser):
    ns = parser.parse_args(["stats", "a.env"])
    assert ns.aggregate is False


def test_aggregate_short_flag(parser):
    ns = parser.parse_args(["stats", "-a", "a.env", "b.env"])
    assert ns.aggregate is True


def test_func_is_callable(parser):
    ns = parser.parse_args(["stats", "a.env"])
    assert callable(ns.func)
