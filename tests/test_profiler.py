"""Tests for patchwork_env.profiler."""

import pytest
from patchwork_env.profiler import profile_env, EnvProfile


@pytest.fixture()
def mixed_env():
    return {
        "APP_NAME": "myapp",
        "DEBUG": "true",
        "PORT": "8080",
        "DATABASE_URL": "https://db.example.com/prod",
        "SECRET_KEY": "",
        "API_KEY": "CHANGE_ME",
        "LONG_VAR": "x" * 120,
        "RATIO": "3.14",
        "ENABLED": "yes",
    }


def test_total_keys(mixed_env):
    p = profile_env(mixed_env)
    assert p.total_keys == len(mixed_env)


def test_empty_value_detected(mixed_env):
    p = profile_env(mixed_env)
    assert "SECRET_KEY" in p.empty_values


def test_placeholder_detected(mixed_env):
    p = profile_env(mixed_env)
    assert "API_KEY" in p.placeholder_values


def test_url_detected(mixed_env):
    p = profile_env(mixed_env)
    assert "DATABASE_URL" in p.url_values


def test_numeric_integer(mixed_env):
    p = profile_env(mixed_env)
    assert "PORT" in p.numeric_values


def test_numeric_float(mixed_env):
    p = profile_env(mixed_env)
    assert "RATIO" in p.numeric_values


def test_boolean_true(mixed_env):
    p = profile_env(mixed_env)
    assert "DEBUG" in p.boolean_values


def test_boolean_yes(mixed_env):
    p = profile_env(mixed_env)
    assert "ENABLED" in p.boolean_values


def test_long_value_detected(mixed_env):
    p = profile_env(mixed_env)
    assert "LONG_VAR" in p.long_values


def test_type_counts_sum_to_total(mixed_env):
    p = profile_env(mixed_env)
    total = sum(p.type_counts.values())
    assert total == p.total_keys


def test_clean_env_has_no_issues():
    env = {"APP_NAME": "myapp", "REGION": "us-east-1"}
    p = profile_env(env)
    assert len(p.empty_values) == 0
    assert len(p.placeholder_values) == 0


def test_summary_contains_total():
    env = {"KEY": "value"}
    p = profile_env(env)
    assert "1" in p.summary()


def test_empty_env():
    p = profile_env({})
    assert p.total_keys == 0
    assert p.type_counts["other"] == 0
