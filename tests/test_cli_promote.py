import pytest
from pathlib import Path
from patchwork_env.cli_promote import run_promote


@pytest.fixture
def env_files(tmp_path):
    return tmp_path


def _write(path: Path, content: str):
    path.write_text(content)


class _Args:
    def __init__(self, source, target, keys=None, prefix=None, overwrite=False, output=None, verbose=False):
        self.source = source
        self.target = target
        self.keys = keys
        self.prefix = prefix
        self.overwrite = overwrite
        self.output = output
        self.verbose = verbose


def test_missing_source_returns_two(env_files):
    target = env_files / "target.env"
    _write(target, "KEY=val\n")
    args = _Args(str(env_files / "missing.env"), str(target))
    assert run_promote(args) == 2


def test_missing_target_returns_two(env_files):
    source = env_files / "source.env"
    _write(source, "KEY=val\n")
    args = _Args(str(source), str(env_files / "missing.env"))
    assert run_promote(args) == 2


def test_no_new_keys_returns_zero(env_files):
    source = env_files / "source.env"
    target = env_files / "target.env"
    _write(source, "KEY=val\n")
    _write(target, "KEY=other\n")
    args = _Args(str(source), str(target))
    assert run_promote(args) == 0


def test_new_key_returns_one(env_files):
    source = env_files / "source.env"
    target = env_files / "target.env"
    _write(source, "NEW_KEY=hello\nEXISTING=x\n")
    _write(target, "EXISTING=y\n")
    args = _Args(str(source), str(target))
    assert run_promote(args) == 1


def test_output_file_written(env_files):
    source = env_files / "source.env"
    target = env_files / "target.env"
    out = env_files / "out.env"
    _write(source, "NEW_KEY=hello\n")
    _write(target, "EXISTING=y\n")
    args = _Args(str(source), str(target), output=str(out))
    run_promote(args)
    assert out.exists()
    assert "NEW_KEY" in out.read_text()


def test_overwrite_updates_existing_key(env_files):
    source = env_files / "source.env"
    target = env_files / "target.env"
    _write(source, "KEY=prod_value\n")
    _write(target, "KEY=staging_value\n")
    args = _Args(str(source), str(target), overwrite=True)
    run_promote(args)
    assert "prod_value" in target.read_text()


def test_prefix_filter_limits_promotion(env_files):
    source = env_files / "source.env"
    target = env_files / "target.env"
    _write(source, "DB_HOST=prod-db\nAPP_NAME=myapp\n")
    _write(target, "LOG_LEVEL=info\n")
    args = _Args(str(source), str(target), prefix="DB_")
    run_promote(args)
    content = target.read_text()
    assert "DB_HOST" in content
    assert "APP_NAME" not in content
