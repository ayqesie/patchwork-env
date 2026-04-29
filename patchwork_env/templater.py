"""Generate a .env template from an existing env dict or schema.

A template replaces all values with empty strings or type hints,
making it easy to share a safe skeleton of a config file.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from patchwork_env.validator import EnvSchema


@dataclass
class TemplateResult:
    template: Dict[str, str] = field(default_factory=dict)
    source_keys: int = 0
    filled_hints: int = 0

    def summary(self) -> str:
        return (
            f"{self.source_keys} key(s) templated, "
            f"{self.filled_hints} with type hint(s)"
        )


def _hint_for_type(type_str: Optional[str]) -> str:
    """Return a placeholder comment-style hint for a given type string."""
    hints = {
        "str": "<string>",
        "int": "<integer>",
        "bool": "<true|false>",
        "url": "<url>",
        "path": "<path>",
    }
    return hints.get((type_str or "").lower(), "")


def generate_template(
    env: Dict[str, str],
    schema: Optional[EnvSchema] = None,
) -> TemplateResult:
    """Build a template dict from *env*, optionally enriched by *schema* hints."""
    result = TemplateResult(source_keys=len(env))
    for key in env:
        hint = ""
        if schema is not None:
            type_str = schema.types.get(key)
            hint = _hint_for_type(type_str)
        result.template[key] = hint
        if hint:
            result.filled_hints += 1
    return result


def to_template_string(result: TemplateResult) -> str:
    """Serialise a TemplateResult to a .env-style string."""
    lines = []
    for key, hint in result.template.items():
        lines.append(f"{key}={hint}")
    return "\n".join(lines) + ("\n" if lines else "")
