"""Score an .env file for overall health and completeness."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .auditor import audit_env
from .linter import lint_env
from .validator import EnvSchema, validate_env

_MAX_SCORE = 100


@dataclass
class ScoreResult:
    total: int
    deductions: Dict[str, int] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)

    @property
    def grade(self) -> str:
        if self.total >= 90:
            return "A"
        if self.total >= 75:
            return "B"
        if self.total >= 60:
            return "C"
        if self.total >= 40:
            return "D"
        return "F"

    def summary(self) -> str:
        lines = [f"Score: {self.total}/{_MAX_SCORE}  (Grade: {self.grade})"]
        for reason, pts in self.deductions.items():
            lines.append(f"  -{pts:>3}  {reason}")
        if self.notes:
            lines.append("Notes:")
            for note in self.notes:
                lines.append(f"  • {note}")
        return "\n".join(lines)


def score_env(
    env: Dict[str, str],
    schema: EnvSchema | None = None,
    *,
    audit_weight: int = 30,
    lint_weight: int = 20,
    validation_weight: int = 30,
    completeness_weight: int = 20,
) -> ScoreResult:
    """Return a ScoreResult for *env* based on audit, lint, validation and completeness."""
    deductions: Dict[str, int] = {}
    notes: List[str] = []

    # --- audit penalties ---
    audit = audit_env(env)
    if audit.has_issues():
        flagged = len(audit.all_flagged_keys())
        penalty = min(audit_weight, round(audit_weight * flagged / max(len(env), 1)))
        deductions[f"audit: {flagged} flagged key(s)"] = penalty

    # --- lint penalties ---
    lint = lint_env(env)
    if lint.has_issues():
        count = len(lint.all_issues())
        penalty = min(lint_weight, round(lint_weight * count / max(len(env), 1)))
        deductions[f"lint: {count} issue(s)"] = penalty

    # --- validation penalties ---
    if schema is not None:
        vr = validate_env(env, schema)
        if not vr.is_valid():
            missing = len(vr.missing)
            penalty = min(validation_weight, round(validation_weight * missing / max(len(schema.required), 1)))
            deductions[f"validation: {missing} missing required key(s)"] = penalty
            if vr.unknown:
                notes.append(f"{len(vr.unknown)} unknown key(s) not in schema")
    else:
        notes.append("No schema provided; validation skipped")

    # --- completeness penalties (empty values) ---
    empty = sum(1 for v in env.values() if v.strip() == "")
    if empty:
        penalty = min(completeness_weight, round(completeness_weight * empty / max(len(env), 1)))
        deductions[f"completeness: {empty} empty value(s)"] = penalty

    total = max(0, _MAX_SCORE - sum(deductions.values()))
    return ScoreResult(total=total, deductions=deductions, notes=notes)
