"""Validator for juniorSE assumption-guardrails skill."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None

EMBEDDED_RULES = {
    "critical_assumption_fields": ["code_edition", "material_grade", "design_method", "load_level", "support_condition", "bracing_condition"],
    "forbidden_silent_assumptions": ["material_grade", "bracing_condition", "design_method", "load_level", "code_edition", "support_condition"],
    "allowed_assumption_statuses": ["user_provided", "explicitly_assumed_preliminary", "not_required_for_scope"],
}


def load_rules() -> Dict[str, Any]:
    rules_path = Path(__file__).with_name("rules.yaml")
    if yaml is not None and rules_path.exists():
        return yaml.safe_load(rules_path.read_text())
    return EMBEDDED_RULES


def validate(inputs: Dict[str, Any], rules: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Validate assumption records.

    Expected input shape:
    {
      "required_for_scope": ["design_method", "bracing_condition"],
      "assumptions": {
        "design_method": {"value": "LRFD", "status": "user_provided"},
        "bracing_condition": {"value": "continuous", "status": "explicitly_assumed_preliminary"}
      }
    }
    """
    rules = rules or load_rules()
    required_for_scope = set(inputs.get("required_for_scope", []))
    assumptions = inputs.get("assumptions", {}) or {}
    allowed_statuses = set(rules.get("allowed_assumption_statuses", []))
    forbidden_silent = set(rules.get("forbidden_silent_assumptions", []))

    errors: List[str] = []
    warnings: List[str] = []
    missing_required: List[str] = []

    for field in required_for_scope:
        record = assumptions.get(field)
        if not record or record.get("value") in (None, "", []):
            missing_required.append(field)
            errors.append(f"Critical assumption/input is required for this scope and is missing: {field}.")
            continue
        status = record.get("status")
        if status not in allowed_statuses:
            errors.append(f"Assumption {field} has invalid status: {status}.")
        if field in forbidden_silent and status != "user_provided" and status != "explicitly_assumed_preliminary":
            errors.append(f"Forbidden silent assumption detected: {field}.")
        if field in forbidden_silent and status == "explicitly_assumed_preliminary":
            warnings.append(f"{field} is preliminary and must be verified by the engineer/user.")

    return {
        "status": "ready" if not errors else "blocked",
        "missing_required": missing_required,
        "errors": errors,
        "warnings": warnings,
        "engineer_review_required": True,
    }
