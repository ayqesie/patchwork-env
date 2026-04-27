"""Tests for patchwork_env.redactor."""

import pytest
from patchwork_env.redactor import (
    RedactResult,
    REDACT_PLACEHOLDER,
    is_sensitive_key,
    redact_env,
)


@pytest.fixture
def mixed_env():
    return {
        "APP_NAME": "myapp",
        "DATABASE_URL": "postgres://user:pass@host/db",
        "SECRET_KEY": "supersecret",
        "API_KEY": "abc123",
        "DEBUG": "true",
        "AUTH_TOKEN": "tok_xyz",
        "PORT": "8080",
        "PRIVATE_KEY": "-----BEGIN RSA-----",
    }


def test_is_sensitive_key_password():
    assert is_sensitive_key("DB_PASSWORD") is True


def test_is_sensitive_key_token():
    assert is_sensitive_key("AUTH_TOKEN") is True


def test_is_sensitive_key_api_key():
    assert is_sensitive_key("API_KEY") is True


def test_is_sensitive_key_safe():
    assert is_sensitive_key("APP_NAME") is False
    assert is_sensitive_key("PORT") is False
    assert is_sensitive_key("DEBUG") is False


def test_is_sensitive_key_case_insensitive():
    assert is_sensitive_key("db_password") is True
    assert is_sensitive_key("Secret_Key") is True


def test_redact_replaces_sensitive_values(mixed_env):
    result = redact_env(mixed_env)
    assert result.redacted["SECRET_KEY"] == REDACT_PLACEHOLDER
    assert result.redacted["API_KEY"] == REDACT_PLACEHOLDER
    assert result.redacted["AUTH_TOKEN"] == REDACT_PLACEHOLDER
    assert result.redacted["DATABASE_URL"] == REDACT_PLACEHOLDER
    assert result.redacted["PRIVATE_KEY"] == REDACT_PLACEHOLDER


def test_redact_preserves_safe_values(mixed_env):
    result = redact_env(mixed_env)
    assert result.redacted["APP_NAME"] == "myapp"
    assert result.redacted["DEBUG"] == "true"
    assert result.redacted["PORT"] == "8080"


def test_redacted_keys_list(mixed_env):
    result = redact_env(mixed_env)
    assert "SECRET_KEY" in result.redacted_keys
    assert "API_KEY" in result.redacted_keys
    assert "APP_NAME" not in result.redacted_keys


def test_extra_keys_forced_redacted(mixed_env):
    result = redact_env(mixed_env, extra_keys=["APP_NAME"])
    assert result.redacted["APP_NAME"] == REDACT_PLACEHOLDER
    assert "APP_NAME" in result.redacted_keys


def test_extra_keys_case_insensitive(mixed_env):
    result = redact_env(mixed_env, extra_keys=["app_name"])
    assert result.redacted["APP_NAME"] == REDACT_PLACEHOLDER


def test_custom_placeholder(mixed_env):
    result = redact_env(mixed_env, placeholder="[hidden]")
    assert result.redacted["SECRET_KEY"] == "[hidden]"


def test_summary_with_redacted_keys(mixed_env):
    result = redact_env(mixed_env)
    s = result.summary()
    assert "Redacted" in s
    assert str(len(result.redacted_keys)) in s


def test_summary_no_sensitive_keys():
    result = redact_env({"APP_NAME": "myapp", "PORT": "8080"})
    assert result.summary() == "No sensitive keys detected."


def test_empty_env():
    result = redact_env({})
    assert result.redacted == {}
    assert result.redacted_keys == []
