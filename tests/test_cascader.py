"""Tests for patchwork_env.cascader."""
import pytest
from patchwork_env.cascader import cascade_env_files, CascadeResult


@pytest.fixture
def three_files():
    return [
        ("base.env", {"APP_ENV": "development", "DB_HOST": "localhost", "PORT": "8000"}),
        ("staging.env", {"APP_ENV": "staging", "DB_HOST": "staging-db"}),
        ("override.env", {"APP_ENV": "production", "SECRET": "s3cr3t"}),
    ]


def test_last_file_wins_for_shared_key(three_files):
    result = cascade_env_files(three_files)
    assert result.final["APP_ENV"] == "production"


def test_intermediate_override_captured(three_files):
    result = cascade_env_files(three_files)
    assert result.final["DB_HOST"] == "staging-db"


def test_base_only_key_preserved(three_files):
    result = cascade_env_files(three_files)
    assert result.final["PORT"] == "8000"


def test_new_key_from_last_file(three_files):
    result = cascade_env_files(three_files)
    assert result.final["SECRET"] == "s3cr3t"


def test_all_keys_present(three_files):
    result = cascade_env_files(three_files)
    assert set(result.final.keys()) == {"APP_ENV", "DB_HOST", "PORT", "SECRET"}


def test_sources_track_winning_file(three_files):
    result = cascade_env_files(three_files)
    assert result.sources["APP_ENV"] == "override.env"
    assert result.sources["DB_HOST"] == "staging.env"
    assert result.sources["PORT"] == "base.env"


def test_overrides_recorded(three_files):
    result = cascade_env_files(three_files)
    keys_overridden = [o[0] for o in result.overrides]
    assert "APP_ENV" in keys_overridden
    assert "DB_HOST" in keys_overridden


def test_no_override_for_unique_keys(three_files):
    result = cascade_env_files(three_files)
    keys_overridden = [o[0] for o in result.overrides]
    assert "PORT" not in keys_overridden
    assert "SECRET" not in keys_overridden


def test_has_overrides_true(three_files):
    result = cascade_env_files(three_files)
    assert result.has_overrides() is True


def test_has_overrides_false_when_no_overlap():
    files = [
        ("a.env", {"KEY_A": "1"}),
        ("b.env", {"KEY_B": "2"}),
    ]
    result = cascade_env_files(files)
    assert result.has_overrides() is False


def test_file_order_preserved(three_files):
    result = cascade_env_files(three_files)
    assert result.file_order == ["base.env", "staging.env", "override.env"]


def test_summary_contains_override_count(three_files):
    result = cascade_env_files(three_files)
    s = result.summary()
    assert "Overrides applied:" in s


def test_single_file_no_overrides():
    files = [("only.env", {"A": "1", "B": "2"})]
    result = cascade_env_files(files)
    assert result.final == {"A": "1", "B": "2"}
    assert result.has_overrides() is False


def test_empty_files_list():
    result = cascade_env_files([])
    assert result.final == {}
    assert result.overrides == []
