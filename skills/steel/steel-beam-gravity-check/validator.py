"""Validator for juniorSE steel-beam-gravity-check skill."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None

EMBEDDED_RULES = {
    "required_inputs": [
        "code_family", "code_edition", "design_method", "span_ft", "dead_load_plf",
        "live_load_plf", "load_level", "support_condition", "bracing_condition",
        "steel_grade", "member_section", "composite_status",
    ],
    "required_for_serviceability": ["E_ksi", "Ix_in4"],
    "allowed_design_methods": ["ASD", "LRFD"],
    "allowed_load_levels": ["service", "factored"],
}


def load_rules() -> Dict[str, Any]:
    rules_path = Path(__file__).with_name("rules.yaml")
    if yaml is not None and rules_path.exists():
        return yaml.safe_load(rules_path.read_text())
    return EMBEDDED_RULES


def _is_missing(value: Any) -> bool:
    return value in (None, "", [])


def _is_positive_number(value: Any) -> bool:
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False


def _is_nonnegative_number(value: Any) -> bool:
    try:
        return float(value) >= 0
    except (TypeError, ValueError):
        return False


def validate(inputs: Dict[str, Any], rules: Dict[str, Any] | None = None) -> Dict[str, Any]:
    rules = rules or load_rules()
    missing = [field for field in rules["required_inputs"] if _is_missing(inputs.get(field))]
    serviceability_missing = [field for field in rules.get("required_for_serviceability", []) if _is_missing(inputs.get(field))]
    errors: List[str] = []
    warnings: List[str] = []

    method = inputs.get("design_method")
    if method and str(method).upper() not in rules.get("allowed_design_methods", ["ASD", "LRFD"]):
        errors.append("design_method must be ASD or LRFD.")

    load_level = inputs.get("load_level")
    if load_level and str(load_level).lower() not in rules.get("allowed_load_levels", ["service", "factored"]):
        errors.append("load_level must be service or factored.")

    if not _is_missing(inputs.get("span_ft")) and not _is_positive_number(inputs.get("span_ft")):
        errors.append("span_ft must be a positive number.")

    for field in ("dead_load_plf", "live_load_plf"):
        if not _is_missing(inputs.get(field)) and not _is_nonnegative_number(inputs.get(field)):
            errors.append(f"{field} must be a nonnegative number.")

    if inputs.get("support_condition") and str(inputs["support_condition"]).lower() not in {"simple", "simply_supported", "simply supported"}:
        errors.append("Current executable scope only supports simply supported beams.")

    if inputs.get("point_loads"):
        errors.append("Current executable scope does not support point loads yet.")

    if serviceability_missing:
        errors.append("Cannot complete current serviceability check without E_ksi and Ix_in4.")
    else:
        for field in rules.get("required_for_serviceability", []):
            if not _is_positive_number(inputs.get(field)):
                errors.append(f"{field} must be a positive number for serviceability calculation.")

    if str(load_level).lower() == "factored":
        warnings.append("Loads are marked factored. Serviceability deflection checks should normally use service-level loads.")

    warnings.append("Current executable scope does not perform AISC strength adequacy checks yet.")

    status = "ready" if not missing and not errors else "blocked"
    return {
        "status": status,
        "missing_inputs": missing,
        "serviceability_missing_inputs": serviceability_missing,
        "errors": errors,
        "warnings": warnings,
        "strength_check_status": "not_implemented_current_version",
        "engineer_review_required": True,
    }
