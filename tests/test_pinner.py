import pytest
from patchwork_env.pinner import PinResult, pin_keys, apply_pins


@pytest.fixture
def base_env():
    return {
        "APP_ENV": "development",
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "SECRET_KEY": "dev-secret",
    }


def test_pin_known_key_updates_value(base_env):
    result = pin_keys(base_env, {"APP_ENV": "production"})
    assert result.pinned["APP_ENV"] == "production"


def test_pin_multiple_keys(base_env):
    result = pin_keys(base_env, {"APP_ENV": "staging", "DB_HOST": "prod-db"})
    assert len(result.pinned) == 2
    assert result.pinned["DB_HOST"] == "prod-db"


def test_unknown_key_goes_to_not_found(base_env):
    result = pin_keys(base_env, {"MISSING_KEY": "value"})
    assert "MISSING_KEY" in result.not_found
    assert "MISSING_KEY" not in result.pinned


def test_skip_if_match_skips_equal_value(base_env):
    result = pin_keys(base_env, {"DB_PORT": "5432"}, skip_if_match=True)
    assert "DB_PORT" in result.skipped
    assert "DB_PORT" not in result.pinned


def test_skip_if_match_pins_different_value(base_env):
    result = pin_keys(base_env, {"DB_PORT": "3306"}, skip_if_match=True)
    assert "DB_PORT" in result.pinned
    assert "DB_PORT" not in result.skipped


def test_has_pins_true_when_pinned(base_env):
    result = pin_keys(base_env, {"APP_ENV": "production"})
    assert result.has_pins() is True


def test_has_pins_false_when_all_not_found():
    result = pin_keys({}, {"GHOST": "value"})
    assert result.has_pins() is False


def test_summary_includes_pinned_count(base_env):
    result = pin_keys(base_env, {"APP_ENV": "production", "DB_HOST": "prod"})
    assert "2 pinned" in result.summary()


def test_summary_includes_not_found(base_env):
    result = pin_keys(base_env, {"NOPE": "x"})
    assert "not found" in result.summary()


def test_summary_includes_skipped(base_env):
    result = pin_keys(base_env, {"DB_PORT": "5432"}, skip_if_match=True)
    assert "skipped" in result.summary()


def test_apply_pins_merges_into_env(base_env):
    result = pin_keys(base_env, {"APP_ENV": "production"})
    updated = apply_pins(base_env, result)
    assert updated["APP_ENV"] == "production"
    assert updated["DB_HOST"] == "localhost"


def test_apply_pins_does_not_mutate_original(base_env):
    result = pin_keys(base_env, {"APP_ENV": "production"})
    apply_pins(base_env, result)
    assert base_env["APP_ENV"] == "development"


def test_empty_pins_returns_unchanged_env(base_env):
    result = pin_keys(base_env, {})
    updated = apply_pins(base_env, result)
    assert updated == base_env
