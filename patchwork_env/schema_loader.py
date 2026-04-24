"""Load EnvSchema definitions from TOML or plain text schema files."""

import re
from pathlib import Path
from typing import Dict, List

from patchwork_env.validator import EnvSchema


def load_schema_from_toml(path: str) -> EnvSchema:
    """Parse a minimal TOML-like schema file without external deps."""
    content = Path(path).read_text()
    required: List[str] = []
    optional: List[str] = []
    types: Dict[str, str] = {}

    section = None
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        section_match = re.match(r"^\[([\w]+)\]$", line)
        if section_match:
            section = section_match.group(1)
            continue
        if section == "required":
            key = line.strip('"').strip("'")
            if key:
                required.append(key)
        elif section == "optional":
            key = line.strip('"').strip("'")
            if key:
                optional.append(key)
        elif section == "types":
            if "=" in line:
                k, v = line.split("=", 1)
                types[k.strip()] = v.strip().strip('"').strip("'")

    return EnvSchema(required=required, optional=optional, types=types)


def load_schema_from_keys(keys: List[str]) -> EnvSchema:
    """Build a simple schema that just requires the given keys."""
    return EnvSchema(required=keys)


def schema_from_base_env(env: Dict[str, str]) -> EnvSchema:
    """Treat all keys in a base env as required for downstream envs."""
    return EnvSchema(required=list(env.keys()))
