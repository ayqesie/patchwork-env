import pytest
from patchwork_env.freezer import freeze_env, check_drift, FreezeResult


@pytest.fixture
def base_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "API_KEY": "secret",
        "DEBUG": "false",
    }


def test_freeze_all_keys_by_default(base_env):
    frozen, result = freeze_env(base_env)
    assert set(frozen.keys()) == set(base_env.keys())


def test_freeze_subset_of_keys(base_env):
    frozen, result = freeze_env(base_env, keys=["DB_HOST", "DB_PORT"])
    assert list(frozen.keys()) == ["DB_HOST", "DB_PORT"]
    assert "API_KEY" not in frozen


def test_frozen_values_match_source(base_env):
    frozen, result = freeze_env(base_env)
    for key, val in base_env.items():
        assert frozen[key] == val


def test_freeze_result_tracks_frozen_keys(base_env):
    _, result = freeze_env(base_env, keys=["DB_HOST"])
    assert "DB_HOST" in result.frozen_keys


def test_freeze_result_tracks_unfrozen_keys(base_env):
    _, result = freeze_env(base_env, keys=["DB_HOST"])
    assert "API_KEY" in result.unfrozen_keys
    assert "DEBUG" in result.unfrozen_keys


def test_freeze_unknown_key_skipped(base_env):
    frozen, result = freeze_env(base_env, keys=["DOES_NOT_EXIST"])
    assert "DOES_NOT_EXIST" not in frozen
    assert result.frozen_keys == []


def test_no_drift_when_identical(base_env):
    frozen, _ = freeze_env(base_env)
    result = check_drift(frozen, base_env)
    assert not result.has_drift()


def test_drift_detected_for_changed_value(base_env):
    frozen, _ = freeze_env(base_env)
    current = {**base_env, "DB_HOST": "prod-db.example.com"}
    result = check_drift(frozen, current)
    assert result.has_drift()
    assert "DB_HOST" in result.drifted_keys
    assert result.drifted_keys["DB_HOST"] == ("localhost", "prod-db.example.com")


def test_drift_detected_for_missing_key(base_env):
    frozen, _ = freeze_env(base_env)
    current = {k: v for k, v in base_env.items() if k != "API_KEY"}
    result = check_drift(frozen, current)
    assert "API_KEY" in result.drifted_keys
    assert result.drifted_keys["API_KEY"][1] == "<missing>"


def test_unfrozen_keys_in_drift_result(base_env):
    frozen, _ = freeze_env(base_env, keys=["DB_HOST"])
    current = {**base_env, "NEW_KEY": "new_value"}
    result = check_drift(frozen, current)
    assert "DB_PORT" in result.unfrozen_keys
    assert "NEW_KEY" in result.unfrozen_keys


def test_summary_shows_drift(base_env):
    frozen, _ = freeze_env(base_env)
    current = {**base_env, "DB_HOST": "changed"}
    result = check_drift(frozen, current)
    summary = result.summary()
    assert "Drifted keys" in summary
    assert "DB_HOST" in summary


def test_summary_no_drift(base_env):
    frozen, _ = freeze_env(base_env)
    result = check_drift(frozen, base_env)
    summary = result.summary()
    assert "Drifted keys  : 0" in summary
