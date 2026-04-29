"""Tests for patchwork_env.templater."""
from __future__ import annotations

import pytest

from patchwork_env.templater import (
    TemplateResult,
    _hint_for_type,
    generate_template,
    to_template_string,
)
from patchwork_env.validator import EnvSchema


@pytest.fixture()
def basic_env() -> dict:
    return {"DATABASE_URL": "postgres://localhost/db", "DEBUG": "true", "PORT": "8080"}


@pytest.fixture()
def typed_schema() -> EnvSchema:
    return EnvSchema(
        required={"DATABASE_URL", "PORT"},
        optional={"DEBUG"},
        types={"DATABASE_URL": "url", "PORT": "int", "DEBUG": "bool"},
    )


def test_generate_template_key_count(basic_env):
    result = generate_template(basic_env)
    assert result.source_keys == 3
    assert set(result.template.keys()) == set(basic_env.keys())


def test_generate_template_values_empty_without_schema(basic_env):
    result = generate_template(basic_env)
    for val in result.template.values():
        assert val == ""


def test_generate_template_no_hints_without_schema(basic_env):
    result = generate_template(basic_env)
    assert result.filled_hints == 0


def test_generate_template_with_schema_fills_hints(basic_env, typed_schema):
    result = generate_template(basic_env, schema=typed_schema)
    assert result.template["DATABASE_URL"] == "<url>"
    assert result.template["PORT"] == "<integer>"
    assert result.template["DEBUG"] == "<true|false>"


def test_generate_template_filled_hints_count(basic_env, typed_schema):
    result = generate_template(basic_env, schema=typed_schema)
    assert result.filled_hints == 3


def test_hint_for_known_types():
    assert _hint_for_type("str") == "<string>"
    assert _hint_for_type("int") == "<integer>"
    assert _hint_for_type("bool") == "<true|false>"
    assert _hint_for_type("url") == "<url>"
    assert _hint_for_type("path") == "<path>"


def test_hint_for_unknown_type_returns_empty():
    assert _hint_for_type("custom") == ""
    assert _hint_for_type(None) == ""


def test_to_template_string_format(basic_env):
    result = generate_template(basic_env)
    output = to_template_string(result)
    for key in basic_env:
        assert f"{key}=" in output


def test_to_template_string_ends_with_newline(basic_env):
    result = generate_template(basic_env)
    output = to_template_string(result)
    assert output.endswith("\n")


def test_to_template_string_empty_env():
    result = generate_template({})
    assert to_template_string(result) == ""


def test_summary_message(basic_env, typed_schema):
    result = generate_template(basic_env, schema=typed_schema)
    msg = result.summary()
    assert "3 key(s)" in msg
    assert "3 with type hint" in msg
