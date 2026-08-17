"""Validator for juniorSE select-load-combinations skill.

This module intentionally validates inputs and stop conditions only. It does not
claim to replace code interpretation by a licensed engineer.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None

EMBEDDED_RULES = {
    "required_inputs": ["code_family", "code_edition", "design_method", "load_cases", "load_level"],
    "allowed_design_methods": ["ASD", "LRFD"],
    "allowed_load_levels": ["service", "factored"],
}


def load_rules() -> Dict[str, Any]:
    rules_path = Path(__file__).with_name("rules.yaml")
    if yaml is not None and rules_path.exists():
        return yaml.safe_load(rules_path.read_text())
    return EMBEDDED_RULES


def validate(inputs: Dict[str, Any], rules: Dict[str, Any] | None = None) -> Dict[str, Any]:
    rules = rules or load_rules()
    missing = [field for field in rules["required_inputs"] if not inputs.get(field)]
    errors: List[str] = []
    warnings: List[str] = []

    method = inputs.get("design_method")
    if method and str(method).upper() not in rules.get("allowed_design_methods", []):
        errors.append("design_method must be ASD or LRFD.")

    load_level = inputs.get("load_level")
    if load_level and str(load_level).lower() not in rules.get("allowed_load_levels", []):
        errors.append("load_level must be service or factored.")

    if str(load_level).lower() == "factored":
        warnings.append("Loads are already factored. Do not re-factor unless explicitly justified.")

    status = "ready" if not missing and not errors else "blocked"
    return {
        "status": status,
        "missing_inputs": missing,
        "errors": errors,
        "warnings": warnings,
        "engineer_review_required": True,
    }
