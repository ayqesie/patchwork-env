"""Tests for patchwork_env.auditor."""

import pytest
from patchwork_env.auditor import audit_env, AuditResult


@pytest.fixture
def clean_env():
    return {"HOST": "localhost", "PORT": "8080", "DEBUG": "false"}


def test_clean_env_has_no_issues(clean_env):
    result = audit_env(clean_env)
    assert not result.has_issues()


def test_empty_value_detected():
    env = {"HOST": "localhost", "SECRET": ""}
    result = audit_env(env)
    assert "SECRET" in result.empty_values


def test_placeholder_value_detected():
    env = {"API_KEY": "changeme"}
    result = audit_env(env)
    assert "API_KEY" in result.placeholder_values


def test_placeholder_todo_detected():
    env = {"TOKEN": "TODO"}
    result = audit_env(env)
    assert "TOKEN" in result.placeholder_values


def test_placeholder_angle_bracket_detected():
    env = {"SECRET": "<your-secret>"}
    result = audit_env(env)
    assert "SECRET" in result.placeholder_values


def test_suspicious_short_password():
    env = {"DB_PASSWORD": "abc"}
    result = audit_env(env)
    assert "DB_PASSWORD" in result.suspicious_values


def test_password_long_enough_not_suspicious():
    env = {"DB_PASSWORD": "supersecret123"}
    result = audit_env(env)
    assert "DB_PASSWORD" not in result.suspicious_values


def test_duplicate_keys_detected():
    raw_lines = ["HOST=a", "PORT=1", "HOST=b"]
    env = {"HOST": "b", "PORT": "1"}
    result = audit_env(env, raw_lines=raw_lines)
    assert "HOST" in result.duplicate_keys


def test_no_duplicate_keys_when_unique():
    raw_lines = ["HOST=a", "PORT=1"]
    env = {"HOST": "a", "PORT": "1"}
    result = audit_env(env, raw_lines=raw_lines)
    assert result.duplicate_keys == []


def test_summary_no_issues():
    result = AuditResult()
    assert result.summary() == "no issues found"


def test_summary_with_issues():
    result = AuditResult(empty_values=["A"], duplicate_keys=["B", "C"])
    summary = result.summary()
    assert "1 empty" in summary
    assert "2 duplicate" in summary


def test_has_issues_false_when_clean():
    result = AuditResult()
    assert not result.has_issues()


def test_has_issues_true_when_dirty():
    result = AuditResult(suspicious_values=["SECRET_KEY"])
    assert result.has_issues()
