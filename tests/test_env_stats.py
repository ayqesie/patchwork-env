"""Tests for patchwork_env.env_stats."""
import pytest
from patchwork_env.env_stats import EnvStats, compute_env_stats, merge_stats


@pytest.fixture
def mixed_env():
    return {
        "DATABASE_URL": "postgres://localhost:5432/mydb",
        "DEBUG": "true",
        "PORT": "8080",
        "SECRET_KEY": "",
        "APP_NAME": "myapp",
        "LONG_VAR": "x" * 90,
        "ENABLED": "yes",
        "RETRY_COUNT": "3",
    }


def test_total_keys(mixed_env):
    stats = compute_env_stats(mixed_env)
    assert stats.total_keys == 8


def test_empty_key_detected(mixed_env):
    stats = compute_env_stats(mixed_env)
    assert stats.empty_keys == 1


def test_numeric_keys_detected(mixed_env):
    stats = compute_env_stats(mixed_env)
    # PORT=8080 and RETRY_COUNT=3 are numeric
    assert stats.numeric_keys == 2


def test_boolean_keys_detected(mixed_env):
    stats = compute_env_stats(mixed_env)
    # DEBUG=true and ENABLED=yes
    assert stats.boolean_keys == 2


def test_url_keys_detected(mixed_env):
    stats = compute_env_stats(mixed_env)
    assert stats.url_keys == 1


def test_long_value_detected(mixed_env):
    stats = compute_env_stats(mixed_env)
    assert stats.long_value_keys == 1


def test_key_lengths_populated(mixed_env):
    stats = compute_env_stats(mixed_env)
    assert len(stats.key_lengths) == 8


def test_value_lengths_populated(mixed_env):
    stats = compute_env_stats(mixed_env)
    assert len(stats.value_lengths) == 8


def test_empty_env_returns_zero_stats():
    stats = compute_env_stats({})
    assert stats.total_keys == 0
    assert stats.empty_keys == 0
    assert stats.numeric_keys == 0


def test_summary_contains_totals(mixed_env):
    stats = compute_env_stats(mixed_env)
    s = stats.summary()
    assert "total=8" in s
    assert "empty=1" in s


def test_merge_stats_sums_totals():
    a = compute_env_stats({"A": "1", "B": ""})
    b = compute_env_stats({"C": "true", "D": "hello"})
    merged = merge_stats([a, b])
    assert merged.total_keys == 4
    assert merged.empty_keys == 1
    assert merged.boolean_keys == 1


def test_merge_empty_list_returns_zero_stats():
    merged = merge_stats([])
    assert merged.total_keys == 0


def test_https_url_detected():
    stats = compute_env_stats({"API": "https://api.example.com/v1"})
    assert stats.url_keys == 1


def test_ftp_url_detected():
    stats = compute_env_stats({"BACKUP": "ftp://files.example.com"})
    assert stats.url_keys == 1
