"""Tests for patchwork_env.differ_summary."""

import pytest

from patchwork_env.differ import EnvDiff
from patchwork_env.differ_summary import MultiDiffReport, build_multi_diff


@pytest.fixture
def report_with_diffs():
    d1 = EnvDiff(
        added={"NEW_KEY": "val"},
        removed={"OLD_KEY": "old"},
        changed={"CHANGED": ("a", "b")},
        unchanged={"SAME": "same"},
    )
    d2 = EnvDiff(
        added={},
        removed={},
        changed={},
        unchanged={"SAME": "same"},
    )
    report = MultiDiffReport()
    report.comparisons = [
        ("base.env", "staging.env", d1),
        ("base.env", "prod.env", d2),
    ]
    return report


def test_total_pairs(report_with_diffs):
    assert report_with_diffs.total_pairs() == 2


def test_pairs_with_diff(report_with_diffs):
    assert report_with_diffs.pairs_with_diff() == 1


def test_pairs_with_diff_none():
    d = EnvDiff(added={}, removed={}, changed={}, unchanged={"K": "v"})
    report = MultiDiffReport(comparisons=[("a", "b", d)])
    assert report.pairs_with_diff() == 0


def test_all_changed_keys_counts(report_with_diffs):
    counts = report_with_diffs.all_changed_keys()
    assert counts["NEW_KEY"] == 1
    assert counts["OLD_KEY"] == 1
    assert counts["CHANGED"] == 1


def test_all_changed_keys_accumulates_across_pairs():
    d1 = EnvDiff(added={"K": "v"}, removed={}, changed={}, unchanged={})
    d2 = EnvDiff(added={"K": "v2"}, removed={}, changed={}, unchanged={})
    report = MultiDiffReport(comparisons=[("a", "b", d1), ("b", "c", d2)])
    counts = report.all_changed_keys()
    assert counts["K"] == 2


def test_summary_contains_pair_names(report_with_diffs):
    s = report_with_diffs.summary()
    assert "base.env" in s
    assert "staging.env" in s
    assert "prod.env" in s


def test_summary_shows_counts(report_with_diffs):
    s = report_with_diffs.summary()
    assert "+1" in s
    assert "-1" in s


def test_build_multi_diff(tmp_path):
    base = tmp_path / "base.env"
    target = tmp_path / "target.env"
    base.write_text("FOO=bar\nSHARED=same\n")
    target.write_text("FOO=baz\nSHARED=same\nNEW=yes\n")
    report = build_multi_diff([(str(base), str(target))])
    assert report.total_pairs() == 1
    assert report.pairs_with_diff() == 1
    _, _, d = report.comparisons[0]
    assert "FOO" in d.changed
    assert "NEW" in d.added
    assert "SHARED" in d.unchanged
