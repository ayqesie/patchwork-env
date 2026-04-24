"""Validate .env files against a schema of required and optional keys."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class ValidationResult:
    missing_required: List[str] = field(default_factory=list)
    unknown_keys: List[str] = field(default_factory=list)
    type_errors: Dict[str, str] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        return not self.missing_required and not self.type_errors

    def summary(self) -> str:
        lines = []
        if self.missing_required:
            lines.append(f"Missing required keys: {', '.join(sorted(self.missing_required))}")
        if self.unknown_keys:
            lines.append(f"Unknown keys: {', '.join(sorted(self.unknown_keys))}")
        if self.type_errors:
            for key, msg in sorted(self.type_errors.items()):
                lines.append(f"Type error for '{key}': {msg}")
        if not lines:
            return "All checks passed."
        return "\n".join(lines)


@dataclass
class EnvSchema:
    required: List[str] = field(default_factory=list)
    optional: List[str] = field(default_factory=list)
    types: Dict[str, str] = field(default_factory=dict)  # key -> 'int' | 'bool' | 'str'

    @property
    def all_known(self) -> Set[str]:
        return set(self.required) | set(self.optional)


TYPE_VALIDATORS = {
    "int": lambda v: v.lstrip("-").isdigit(),
    "bool": lambda v: v.lower() in ("true", "false", "1", "0", "yes", "no"),
    "str": lambda v: True,
}


def validate(env: Dict[str, str], schema: EnvSchema) -> ValidationResult:
    result = ValidationResult()

    for key in schema.required:
        if key not in env:
            result.missing_required.append(key)

    if schema.all_known:
        for key in env:
            if key not in schema.all_known:
                result.unknown_keys.append(key)

    for key, expected_type in schema.types.items():
        if key in env:
            validator = TYPE_VALIDATORS.get(expected_type)
            if validator and not validator(env[key]):
                result.type_errors[key] = f"expected {expected_type}, got '{env[key]}'"

    return result
