"""Tests for patchwork_env.cli_encrypt."""

import pytest

pytest.importorskip("cryptography", reason="cryptography not installed")

from pathlib import Path

from patchwork_env.cli_encrypt import run_encrypt
from patchwork_env.encryptor import generate_key


@pytest.fixture()
def env_files(tmp_path):
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def _args(**kwargs):
    import argparse
    defaults = dict(
        file=".env",
        key="",
        generate_key=False,
        decrypt=False,
        all=False,
        output="",
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_missing_file_returns_two(env_files):
    args = _args(file=str(env_files / "missing.env"))
    assert run_encrypt(args) == 2


def test_generate_key_returns_zero(env_files):
    f = _write(env_files / ".env", "APP=hello\n")
    args = _args(file=str(f), generate_key=True)
    assert run_encrypt(args) == 0


def test_no_key_returns_two(env_files):
    f = _write(env_files / ".env", "APP=hello\n")
    args = _args(file=str(f), key="")
    assert run_encrypt(args) == 2


def test_encrypt_sensitive_returns_zero(env_files):
    f = _write(env_files / ".env", "DB_PASSWORD=secret\nAPP=hello\n")
    key = generate_key()
    args = _args(file=str(f), key=key)
    assert run_encrypt(args) == 0


def test_encrypt_no_sensitive_returns_one(env_files):
    f = _write(env_files / ".env", "APP=hello\nPORT=8080\n")
    key = generate_key()
    args = _args(file=str(f), key=key)
    assert run_encrypt(args) == 1


def test_encrypt_writes_output_file(env_files):
    f = _write(env_files / ".env", "DB_PASSWORD=hunter2\n")
    out = env_files / "out.env"
    key = generate_key()
    args = _args(file=str(f), key=key, output=str(out))
    run_encrypt(args)
    assert out.exists()
    content = out.read_text()
    assert "DB_PASSWORD" in content
    assert "hunter2" not in content


def test_decrypt_roundtrip(env_files):
    from patchwork_env.encryptor import encrypt_env
    from patchwork_env.reconciler import to_env_string

    env = {"DB_PASSWORD": "hunter2"}
    key = generate_key()
    result = encrypt_env(env, key, sensitive_only=False)
    enc_content = to_env_string(result.encrypted)
    f = _write(env_files / "enc.env", enc_content)
    out = env_files / "dec.env"
    args = _args(file=str(f), key=key, decrypt=True, output=str(out))
    code = run_encrypt(args)
    assert code == 0
    assert "hunter2" in out.read_text()
