"""Tests for schema_loader.load_schema_from_toml."""

import textwrap
from pathlib import Path

import pytest

from patchwork_env.schema_loader import load_schema_from_toml


@pytest.fixture
def schema_file(tmp_path):
    def _write(content):
        p = tmp_path / "schema.toml"
        p.write_text(textwrap.dedent(content))
        return str(p)
    return _write


def test_load_required_keys(schema_file):
    path = schema_file("""
        [required]
        DATABASE_URL
        SECRET_KEY
    """)
    schema = load_schema_from_toml(path)
    assert "DATABASE_URL" in schema.required
    assert "SECRET_KEY" in schema.required


def test_load_optional_keys(schema_file):
    path = schema_file("""
        [optional]
        DEBUG
        LOG_LEVEL
    """)
    schema = load_schema_from_toml(path)
    assert "DEBUG" in schema.optional
    assert "LOG_LEVEL" in schema.optional


def test_load_types(schema_file):
    path = schema_file("""
        [types]
        PORT = int
        DEBUG = bool
    """)
    schema = load_schema_from_toml(path)
    assert schema.types["PORT"] == "int"
    assert schema.types["DEBUG"] == "bool"


def test_load_combined_schema(schema_file):
    path = schema_file("""
        [required]
        DATABASE_URL

        [optional]
        DEBUG

        [types]
        PORT = int
    """)
    schema = load_schema_from_toml(path)
    assert "DATABASE_URL" in schema.required
    assert "DEBUG" in schema.optional
    assert schema.types.get("PORT") == "int"


def test_comments_ignored(schema_file):
    path = schema_file("""
        # this is a comment
        [required]
        # another comment
        API_KEY
    """)
    schema = load_schema_from_toml(path)
    assert "API_KEY" in schema.required
    assert len(schema.required) == 1
