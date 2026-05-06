"""Tests for patchwork_env.encryptor."""

import pytest

pytest.importorskip("cryptography", reason="cryptography not installed")

from patchwork_env.encryptor import (
    EncryptResult,
    decrypt_env,
    encrypt_env,
    generate_key,
    _is_sensitive,
)


@pytest.fixture()
def fkey():
    return generate_key()


@pytest.fixture()
def mixed_env():
    return {
        "DB_PASSWORD": "hunter2",
        "API_KEY": "abc123",
        "APP_NAME": "myapp",
        "PORT": "8080",
    }


def test_generate_key_returns_string(fkey):
    assert isinstance(fkey, str)
    assert len(fkey) > 0


def test_is_sensitive_password():
    assert _is_sensitive("DB_PASSWORD") is True


def test_is_sensitive_token():
    assert _is_sensitive("AUTH_TOKEN") is True


def test_is_sensitive_api_key():
    assert _is_sensitive("API_KEY") is True


def test_is_sensitive_safe_key():
    assert _is_sensitive("APP_NAME") is False


def test_encrypt_sensitive_only(fkey, mixed_env):
    result = encrypt_env(mixed_env, fkey, sensitive_only=True)
    assert "DB_PASSWORD" in result.encrypted
    assert "API_KEY" in result.encrypted
    assert "APP_NAME" in result.skipped
    assert "PORT" in result.skipped


def test_encrypt_all_keys(fkey, mixed_env):
    result = encrypt_env(mixed_env, fkey, sensitive_only=False)
    assert set(result.encrypted.keys()) == set(mixed_env.keys())
    assert result.skipped == []


def test_encrypted_value_differs_from_original(fkey, mixed_env):
    result = encrypt_env(mixed_env, fkey)
    assert result.encrypted["DB_PASSWORD"] != mixed_env["DB_PASSWORD"]


def test_decrypt_roundtrip(fkey, mixed_env):
    result = encrypt_env(mixed_env, fkey, sensitive_only=False)
    decrypted = decrypt_env(result.encrypted, fkey)
    assert decrypted == mixed_env


def test_decrypt_leaves_plaintext_unchanged(fkey):
    plain = {"APP_NAME": "myapp"}
    decrypted = decrypt_env(plain, fkey)
    assert decrypted["APP_NAME"] == "myapp"


def test_has_encrypted_true(fkey, mixed_env):
    result = encrypt_env(mixed_env, fkey)
    assert result.has_encrypted() is True


def test_has_encrypted_false_when_all_skipped(fkey):
    env = {"APP_NAME": "myapp", "PORT": "8080"}
    result = encrypt_env(env, fkey, sensitive_only=True)
    assert result.has_encrypted() is False


def test_summary_contains_counts(fkey, mixed_env):
    result = encrypt_env(mixed_env, fkey)
    s = result.summary()
    assert "Encrypted" in s
    assert "skipped" in s


def test_key_used_stored(fkey, mixed_env):
    result = encrypt_env(mixed_env, fkey)
    assert result.key_used == fkey
