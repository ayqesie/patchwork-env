"""Tests for patchwork_env.validator and patchwork_env.schema_loader."""

import pytest

from patchwork_env.validator import EnvSchema, ValidationResult, validate
from patchwork_env.schema_loader import load_schema_from_keys, schema_from_base_env


@pytest.fixture
def basic_schema():
    return EnvSchema(
        required=["DATABASE_URL", "SECRET_KEY"],
        optional=["DEBUG", "LOG_LEVEL"],
        types={"PORT": "int", "DEBUG": "bool"},
    )


def test_valid_env_passes(basic_schema):
    env = {"DATABASE_URL": "postgres://localhost/db", "SECRET_KEY": "abc123"}
    result = validate(env, basic_schema)
    assert result.is_valid


def test_missing_required_key(basic_schema):
    env = {"DATABASE_URL": "postgres://localhost/db"}
    result = validate(env, basic_schema)
    assert "SECRET_KEY" in result.missing_required
    assert not result.is_valid


def test_all_required_missing(basic_schema):
    result = validate({}, basic_schema)
    assert set(result.missing_required) == {"DATABASE_URL", "SECRET_KEY"}


def test_unknown_keys_detected(basic_schema):
    env = {"DATABASE_URL": "x", "SECRET_KEY": "y", "ROGUE_VAR": "z"}
    result = validate(env, basic_schema)
    assert "ROGUE_VAR" in result.unknown_keys
    assert result.is_valid  # unknown keys don't fail validation


def test_invalid_int_type(basic_schema):
    env = {"DATABASE_URL": "x", "SECRET_KEY": "y", "PORT": "not_a_number"}
    result = validate(env, basic_schema)
    assert "PORT" in result.type_errors
    assert not result.is_valid


def test_valid_bool_values(basic_schema):
    for val in ("true", "false", "1", "0", "yes", "no", "True", "False"):
        env = {"DATABASE_URL": "x", "SECRET_KEY": "y", "DEBUG": val}
        result = validate(env, basic_schema)
        assert "DEBUG" not in result.type_errors


def test_invalid_bool_value(basic_schema):
    env = {"DATABASE_URL": "x", "SECRET_KEY": "y", "DEBUG": "maybe"}
    result = validate(env, basic_schema)
    assert "DEBUG" in result.type_errors


def test_summary_all_passed():
    schema = EnvSchema(required=["KEY"])
    result = validate({"KEY": "val"}, schema)
    assert result.summary() == "All checks passed."


def test_summary_contains_missing():
    schema = EnvSchema(required=["MISSING_KEY"])
    result = validate({}, schema)
    assert "MISSING_KEY" in result.summary()


def test_load_schema_from_keys():
    schema = load_schema_from_keys(["A", "B", "C"])
    assert schema.required == ["A", "B", "C"]


def test_schema_from_base_env():
    base = {"HOST": "localhost", "PORT": "5432"}
    schema = schema_from_base_env(base)
    assert set(schema.required) == {"HOST", "PORT"}
