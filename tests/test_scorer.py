"""Tests for patchwork_env.scorer."""
import pytest

from patchwork_env.scorer import ScoreResult, score_env
from patchwork_env.validator import EnvSchema


@pytest.fixture()
def clean_env():
    return {"APP_HOST": "localhost", "APP_PORT": "8080", "DB_URL": "postgres://localhost/db"}


@pytest.fixture()
def schema():
    return EnvSchema(required={"APP_HOST", "APP_PORT", "DB_URL"}, optional=set(), types={})


def test_clean_env_scores_100(clean_env, schema):
    result = score_env(clean_env, schema)
    assert result.total == 100


def test_grade_a_for_high_score():
    r = ScoreResult(total=95)
    assert r.grade == "A"


def test_grade_b():
    r = ScoreResult(total=80)
    assert r.grade == "B"


def test_grade_c():
    r = ScoreResult(total=65)
    assert r.grade == "C"


def test_grade_d():
    r = ScoreResult(total=45)
    assert r.grade == "D"


def test_grade_f():
    r = ScoreResult(total=30)
    assert r.grade == "F"


def test_empty_values_reduce_score(schema):
    env = {"APP_HOST": "", "APP_PORT": "", "DB_URL": "postgres://localhost/db"}
    result = score_env(env, schema)
    assert result.total < 100
    assert any("completeness" in k for k in result.deductions)


def test_placeholder_values_reduce_score(schema):
    env = {"APP_HOST": "CHANGE_ME", "APP_PORT": "8080", "DB_URL": "postgres://localhost/db"}
    result = score_env(env, schema)
    assert result.total < 100


def test_missing_required_key_reduces_score():
    schema = EnvSchema(required={"APP_HOST", "APP_PORT", "DB_URL"}, optional=set(), types={})
    env = {"APP_HOST": "localhost"}  # missing APP_PORT and DB_URL
    result = score_env(env, schema)
    assert result.total < 100
    assert any("validation" in k for k in result.deductions)


def test_no_schema_adds_note(clean_env):
    result = score_env(clean_env, schema=None)
    assert any("schema" in n.lower() for n in result.notes)


def test_lint_issue_reduces_score(schema):
    env = {"app_host": "localhost", "APP_PORT": "8080", "DB_URL": "db"}  # lowercase key
    result = score_env(env, schema=None)
    assert result.total < 100
    assert any("lint" in k for k in result.deductions)


def test_summary_contains_score(clean_env, schema):
    result = score_env(clean_env, schema)
    summary = result.summary()
    assert "100" in summary
    assert "Grade" in summary


def test_summary_lists_deductions():
    r = ScoreResult(total=70, deductions={"lint: 2 issue(s)": 10, "completeness: 1 empty value(s)": 20})
    summary = r.summary()
    assert "lint" in summary
    assert "completeness" in summary


def test_total_never_goes_below_zero():
    env = {k: "" for k in [f"KEY_{i}" for i in range(20)]}
    result = score_env(env, schema=None)
    assert result.total >= 0
