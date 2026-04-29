"""Transform .env values in bulk using rules like prefix, suffix, upper, lower, replace."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TransformResult:
    original: Dict[str, str]
    transformed: Dict[str, str]
    applied: List[str] = field(default_factory=list)

    def summary(self) -> str:
        n = len(self.applied)
        return f"{n} transformation(s) applied" if n else "no transformations applied"

    def has_changes(self) -> bool:
        return self.original != self.transformed


def _apply_rule(value: str, rule: str, arg: Optional[str] = None) -> str:
    if rule == "upper":
        return value.upper()
    if rule == "lower":
        return value.lower()
    if rule == "prefix" and arg is not None:
        return f"{arg}{value}"
    if rule == "suffix" and arg is not None:
        return f"{value}{arg}"
    if rule == "strip":
        return value.strip()
    if rule == "replace" and arg is not None:
        parts = arg.split(",", 1)
        if len(parts) == 2:
            return value.replace(parts[0], parts[1])
    return value


def transform_env(
    env: Dict[str, str],
    rules: List[Dict],
    keys: Optional[List[str]] = None,
) -> TransformResult:
    """Apply a list of transformation rules to env values.

    Each rule is a dict with 'rule' (str) and optional 'arg' (str).
    If `keys` is provided, only those keys are transformed.
    """
    result = dict(env)
    applied: List[str] = []
    target_keys = keys if keys is not None else list(env.keys())

    for key in target_keys:
        if key not in result:
            continue
        original_val = result[key]
        new_val = original_val
        for rule_def in rules:
            rule = rule_def.get("rule", "")
            arg = rule_def.get("arg")
            new_val = _apply_rule(new_val, rule, arg)
        if new_val != original_val:
            applied.append(key)
        result[key] = new_val

    return TransformResult(original=env, transformed=result, applied=applied)
