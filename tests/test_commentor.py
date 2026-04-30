"""Tests for patchwork_env.commentor."""

import pytest
from patchwork_env.commentor import (
    CommentResult,
    extract_comments,
    strip_comments,
    add_comment,
    to_commented_string,
)


@pytest.fixture()
def env_with_comments():
    return {
        "HOST": "localhost  # primary host",
        "PORT": "5432  # default postgres port",
        "DEBUG": "true",
        "SECRET": "abc123",
    }


def test_extract_finds_comment_keys(env_with_comments):
    result = extract_comments(env_with_comments)
    assert "HOST" in result.comments
    assert "PORT" in result.comments


def test_extract_ignores_clean_keys(env_with_comments):
    result = extract_comments(env_with_comments)
    assert "DEBUG" not in result.comments
    assert "SECRET" not in result.comments


def test_extracted_comment_text(env_with_comments):
    result = extract_comments(env_with_comments)
    assert result.comments["HOST"] == "primary host"
    assert result.comments["PORT"] == "default postgres port"


def test_stripped_values_have_no_comment(env_with_comments):
    result = extract_comments(env_with_comments)
    assert result.stripped["HOST"] == "localhost"
    assert result.stripped["PORT"] == "5432"


def test_clean_keys_preserved_in_stripped(env_with_comments):
    result = extract_comments(env_with_comments)
    assert result.stripped["DEBUG"] == "true"
    assert result.stripped["SECRET"] == "abc123"


def test_has_comments_true(env_with_comments):
    result = extract_comments(env_with_comments)
    assert result.has_comments() is True


def test_has_comments_false():
    result = extract_comments({"A": "1", "B": "2"})
    assert result.has_comments() is False


def test_summary_with_comments(env_with_comments):
    result = extract_comments(env_with_comments)
    assert "2" in result.summary()


def test_summary_no_comments():
    result = extract_comments({"A": "1"})
    assert "No inline comments" in result.summary()


def test_strip_comments_returns_clean_dict(env_with_comments):
    clean = strip_comments(env_with_comments)
    for value in clean.values():
        assert "#" not in value


def test_add_comment_appends_text():
    env = {"DB": "postgres"}
    updated = add_comment(env, "DB", "main database")
    assert "# main database" in updated["DB"]
    assert updated["DB"].startswith("postgres")


def test_add_comment_replaces_existing_comment():
    env = {"DB": "postgres  # old comment"}
    updated = add_comment(env, "DB", "new comment")
    assert "new comment" in updated["DB"]
    assert "old comment" not in updated["DB"]


def test_add_comment_missing_key_raises():
    with pytest.raises(KeyError):
        add_comment({"A": "1"}, "MISSING", "oops")


def test_to_commented_string_injects_comments():
    env = {"HOST": "localhost", "PORT": "5432"}
    comments = {"HOST": "the host"}
    out = to_commented_string(env, comments)
    assert "HOST=localhost  # the host" in out
    assert "PORT=5432" in out


def test_to_commented_string_no_comments():
    env = {"X": "1", "Y": "2"}
    out = to_commented_string(env)
    assert "#" not in out
