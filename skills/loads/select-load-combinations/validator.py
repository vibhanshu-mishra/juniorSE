"""Validator for juniorSE select-load-combinations skill.

This module validates whether load-combination selection can proceed. It is
not a substitute for project-specific code interpretation by a licensed
engineer.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None

EMBEDDED_RULES: Dict[str, Any] = {
    "required_inputs": ["code_family", "code_edition", "design_method", "load_level", "loads", "objective"],
    "allowed_code_families": ["ASCE 7"],
    "allowed_code_editions": ["ASCE 7-16", "ASCE 7-22"],
    "allowed_design_methods": ["ASD", "LRFD"],
    "allowed_load_levels": ["service", "factored"],
    "supported_load_cases": ["D", "L", "Lr", "S", "R", "W", "E"],
}


def load_rules() -> Dict[str, Any]:
    rules_path = Path(__file__).with_name("rules.yaml")
    if yaml is not None and rules_path.exists():
        return yaml.safe_load(rules_path.read_text())
    return EMBEDDED_RULES


def _normalize_method(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip().upper()
    return text or None


def _normalize_load_level(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip().lower()
    return text or None


def _load_dict(inputs: Dict[str, Any]) -> Dict[str, Any]:
    loads = inputs.get("loads")
    if isinstance(loads, dict):
        return loads
    # Backward compatibility with earlier v0.2 examples that used load_cases.
    load_cases = inputs.get("load_cases")
    if isinstance(load_cases, list):
        return {str(case): None for case in load_cases}
    return {}


def validate(inputs: Dict[str, Any], rules: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Validate readiness for load-combination selection.

    The validator blocks unsupported load cases and missing required metadata.
    Numeric magnitudes are required for combination evaluation, but nonnumeric
    load cases are still reported separately so the caller can request values.
    """
    rules = rules or load_rules()
    required = rules.get("required_inputs", EMBEDDED_RULES["required_inputs"])

    missing: List[str] = []
    for field in required:
        if field == "loads":
            if not _load_dict(inputs):
                missing.append(field)
        elif not inputs.get(field):
            missing.append(field)

    errors: List[str] = []
    warnings: List[str] = []

    code_family = inputs.get("code_family")
    if code_family and str(code_family).strip() not in rules.get("allowed_code_families", ["ASCE 7"]):
        errors.append("code_family is not supported by this skill version.")

    code_edition = inputs.get("code_edition")
    if code_edition and str(code_edition).strip() not in rules.get("allowed_code_editions", ["ASCE 7-16", "ASCE 7-22"]):
        warnings.append("code_edition is not explicitly supported; treat output as preliminary.")

    method = _normalize_method(inputs.get("design_method"))
    if method and method not in rules.get("allowed_design_methods", ["ASD", "LRFD"]):
        errors.append("design_method must be ASD or LRFD.")

    load_level = _normalize_load_level(inputs.get("load_level"))
    if load_level and load_level not in rules.get("allowed_load_levels", ["service", "factored"]):
        errors.append("load_level must be service or factored.")
    if load_level == "factored":
        warnings.append("Loads are already factored. Do not re-factor unless explicitly justified.")

    loads = _load_dict(inputs)
    supported = set(rules.get("supported_load_cases", EMBEDDED_RULES["supported_load_cases"]))
    unsupported_load_cases = sorted(case for case in loads if case not in supported)
    if unsupported_load_cases:
        errors.append("Unsupported load cases are present for this skill version.")

    nonnumeric_load_cases: List[str] = []
    for case, value in loads.items():
        if case in unsupported_load_cases:
            continue
        if value is None:
            nonnumeric_load_cases.append(case)
            continue
        try:
            float(value)
        except (TypeError, ValueError):
            nonnumeric_load_cases.append(case)
    if nonnumeric_load_cases:
        errors.append("All supported load cases must have numeric magnitudes for combination evaluation.")

    if inputs.get("objective") == "serviceability" and method == "LRFD":
        warnings.append("Serviceability usually uses service-level combinations/criteria, not LRFD strength demand.")

    status = "ready" if not missing and not errors else "blocked"
    return {
        "status": status,
        "missing_inputs": missing,
        "errors": errors,
        "warnings": warnings,
        "unsupported_load_cases": unsupported_load_cases,
        "nonnumeric_load_cases": nonnumeric_load_cases,
        "engineer_review_required": True,
    }
