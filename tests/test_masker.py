"""Tests for patchwork_env.masker."""
import pytest
from patchwork_env.masker import MaskResult, _is_sensitive, mask_env


@pytest.fixture()
def mixed_env() -> dict:
    return {
        "DB_PASSWORD": "s3cr3t",
        "API_TOKEN": "tok_abc123",
        "APP_NAME": "myapp",
        "SECRET_KEY": "xyz",
        "DEBUG": "true",
        "AWS_SECRET_ACCESS_KEY": "aws_secret",
    }


# --- _is_sensitive ---

def test_is_sensitive_password():
    assert _is_sensitive("DB_PASSWORD") is True

def test_is_sensitive_token():
    assert _is_sensitive("API_TOKEN") is True

def test_is_sensitive_key():
    assert _is_sensitive("SECRET_KEY") is True

def test_is_sensitive_safe_key():
    assert _is_sensitive("APP_NAME") is False

def test_is_sensitive_debug():
    assert _is_sensitive("DEBUG") is False


# --- mask_env auto-detect ---

def test_auto_detect_masks_sensitive_keys(mixed_env):
    result = mask_env(mixed_env)
    assert result.masked["DB_PASSWORD"] == "***"
    assert result.masked["API_TOKEN"] == "***"
    assert result.masked["SECRET_KEY"] == "***"
    assert result.masked["AWS_SECRET_ACCESS_KEY"] == "***"

def test_auto_detect_leaves_safe_keys(mixed_env):
    result = mask_env(mixed_env)
    assert result.masked["APP_NAME"] == "myapp"
    assert result.masked["DEBUG"] == "true"

def test_masked_keys_list_populated(mixed_env):
    result = mask_env(mixed_env)
    assert "DB_PASSWORD" in result.masked_keys
    assert "APP_NAME" not in result.masked_keys

def test_has_masked_true(mixed_env):
    result = mask_env(mixed_env)
    assert result.has_masked() is True

def test_has_masked_false():
    result = mask_env({"APP_NAME": "myapp", "DEBUG": "true"})
    assert result.has_masked() is False


# --- explicit keys ---

def test_explicit_key_masked_regardless_of_name(mixed_env):
    result = mask_env(mixed_env, keys=["APP_NAME"], auto_detect=False)
    assert result.masked["APP_NAME"] == "***"
    assert result.masked["DB_PASSWORD"] == "s3cr3t"  # auto_detect off

def test_custom_mask_value(mixed_env):
    result = mask_env(mixed_env, mask_value="[REDACTED]")
    assert result.masked["DB_PASSWORD"] == "[REDACTED]"


# --- original preserved ---

def test_original_is_unchanged(mixed_env):
    result = mask_env(mixed_env)
    assert result.original["DB_PASSWORD"] == "s3cr3t"

def test_result_is_copy(mixed_env):
    result = mask_env(mixed_env)
    result.masked["APP_NAME"] = "changed"
    assert mixed_env["APP_NAME"] == "myapp"


# --- summary ---

def test_summary_lists_masked_keys(mixed_env):
    result = mask_env(mixed_env)
    s = result.summary()
    assert "masked" in s
    assert str(len(result.masked_keys)) in s

def test_summary_no_masked_keys():
    result = mask_env({"APP_NAME": "myapp"})
    assert result.summary() == "No keys masked."
