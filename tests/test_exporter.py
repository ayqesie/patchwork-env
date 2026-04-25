"""Tests for patchwork_env.exporter."""

import json
import pytest

from patchwork_env.differ import EnvDiff
from patchwork_env.exporter import diff_to_dict, export_json, export_markdown


@pytest.fixture()
def diff() -> EnvDiff:
    base = {"HOST": "localhost", "PORT": "5432", "OLD": "gone", "SAME": "yes"}
    target = {"HOST": "prod.example.com", "PORT": "5432", "NEW": "here", "SAME": "yes"}
    from patchwork_env.differ import diff_envs
    return diff_envs(base, target)


# --- diff_to_dict ---

def test_dict_has_all_sections(diff):
    d = diff_to_dict(diff)
    assert set(d.keys()) == {"added", "removed", "changed", "unchanged"}


def test_dict_added_contains_new_key(diff):
    d = diff_to_dict(diff)
    assert "NEW" in d["added"]
    assert d["added"]["NEW"] == "here"


def test_dict_removed_contains_old_key(diff):
    d = diff_to_dict(diff)
    assert "OLD" in d["removed"]


def test_dict_changed_has_base_and_target(diff):
    d = diff_to_dict(diff)
    assert "HOST" in d["changed"]
    assert d["changed"]["HOST"]["base"] == "localhost"
    assert d["changed"]["HOST"]["target"] == "prod.example.com"


def test_dict_unchanged_contains_same_key(diff):
    d = diff_to_dict(diff)
    assert "SAME" in d["unchanged"]


# --- export_json ---

def test_export_json_is_valid_json(diff):
    raw = export_json(diff)
    parsed = json.loads(raw)
    assert isinstance(parsed, dict)


def test_export_json_contains_added_key(diff):
    raw = export_json(diff)
    assert "NEW" in raw


def test_export_json_indent_respected(diff):
    raw = export_json(diff, indent=4)
    # 4-space indent means lines start with "    "
    assert "    " in raw


# --- export_markdown ---

def test_markdown_has_report_header(diff):
    md = export_markdown(diff)
    assert "# Env Diff Report" in md


def test_markdown_shows_added_section(diff):
    md = export_markdown(diff)
    assert "## Added" in md
    assert "`NEW`" in md


def test_markdown_shows_removed_section(diff):
    md = export_markdown(diff)
    assert "## Removed" in md
    assert "`OLD`" in md


def test_markdown_shows_changed_table(diff):
    md = export_markdown(diff)
    assert "## Changed" in md
    assert "`HOST`" in md
    assert "localhost" in md
    assert "prod.example.com" in md


def test_markdown_custom_labels(diff):
    md = export_markdown(diff, base_label="staging", target_label="production")
    assert "staging" in md
    assert "production" in md


def test_markdown_unchanged_section(diff):
    md = export_markdown(diff)
    assert "## Unchanged" in md
    assert "`SAME`" in md
