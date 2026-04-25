"""Tests for patchwork_env.linter."""

import pytest
from patchwork_env.linter import lint_env, LintResult


@pytest.fixture
def clean_env():
    return {"DATABASE_URL": "postgres://localhost/db", "DEBUG": "false"}


def test_clean_env_has_no_issues(clean_env):
    result = lint_env(clean_env)
    assert not result.has_issues


def test_lowercase_key_flagged():
    result = lint_env({"database_url": "value"})
    assert result.has_issues
    issues = result.all_issues
    assert any("uppercase" in i for i in issues)


def test_mixed_case_key_flagged():
    result = lint_env({"DatabaseUrl": "value"})
    assert result.has_issues


def test_uppercase_key_not_flagged():
    result = lint_env({"DATABASE_URL": "value"})
    assert not result.has_issues


def test_leading_underscore_flagged():
    result = lint_env({"_SECRET": "value"})
    issues = result.all_issues
    assert any("underscore" in i for i in issues)


def test_trailing_underscore_flagged():
    result = lint_env({"SECRET_": "value"})
    issues = result.all_issues
    assert any("underscore" in i for i in issues)


def test_double_underscore_flagged():
    result = lint_env({"MY__VAR": "value"})
    issues = result.all_issues
    assert any("consecutive" in i for i in issues)


def test_leading_whitespace_in_value_flagged():
    result = lint_env({"MY_VAR": "  value"})
    issues = result.all_issues
    assert any("whitespace" in i for i in issues)


def test_trailing_whitespace_in_value_flagged():
    result = lint_env({"MY_VAR": "value  "})
    issues = result.all_issues
    assert any("whitespace" in i for i in issues)


def test_inline_comment_flagged():
    result = lint_env({"MY_VAR": "somevalue # this is a comment"})
    issues = result.all_issues
    assert any("inline comment" in i for i in issues)


def test_quoted_value_with_hash_not_flagged():
    result = lint_env({"MY_VAR": '"somevalue # not a comment"'})
    assert not result.has_issues


def test_summary_no_issues(clean_env):
    result = lint_env(clean_env)
    assert "No lint" in result.summary


def test_summary_with_issues():
    result = lint_env({"bad_key": "  value  "})
    assert "issue" in result.summary


def test_multiple_issues_same_key():
    result = lint_env({"_bad_key": "  value  "})
    assert len(result.issues.get("_bad_key", [])) >= 2
