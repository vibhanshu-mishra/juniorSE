"""Validator for juniorSE steel-beam-gravity-analysis skill."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None

EMBEDDED_RULES = {
    "required_inputs": ["span_ft", "dead_load_plf", "live_load_plf", "load_level", "support_condition"],
    "required_for_deflection": ["E_ksi", "Ix_in4"],
    "allowed_load_levels": ["service", "factored"],
    "allowed_support_conditions": ["simple", "simply_supported", "simply supported"],
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
    errors: List[str] = []
    warnings: List[str] = []

    if not _is_missing(inputs.get("span_ft")) and not _is_positive_number(inputs.get("span_ft")):
        errors.append("span_ft must be a positive number.")

    for field in ("dead_load_plf", "live_load_plf"):
        if not _is_missing(inputs.get(field)) and not _is_nonnegative_number(inputs.get(field)):
            errors.append(f"{field} must be a nonnegative number.")

    load_level = inputs.get("load_level")
    if load_level and str(load_level).lower() not in rules.get("allowed_load_levels", []):
        errors.append("load_level must be service or factored.")

    support_condition = inputs.get("support_condition")
    if support_condition and str(support_condition).lower() not in set(rules.get("allowed_support_conditions", [])):
        errors.append("Current executable scope only supports simply supported beams.")

    if inputs.get("point_loads"):
        errors.append("Current executable scope does not support point loads yet.")
    if inputs.get("partial_uniform_loads"):
        errors.append("Current executable scope does not support partial uniform loads yet.")

    deflection_missing = [field for field in rules.get("required_for_deflection", []) if _is_missing(inputs.get(field))]
    if deflection_missing:
        warnings.append("Deflection check is incomplete unless E_ksi and Ix_in4 are provided.")
    else:
        for field in rules.get("required_for_deflection", []):
            if not _is_positive_number(inputs.get(field)):
                errors.append(f"{field} must be a positive number for deflection calculation.")

    if str(load_level).lower() == "factored":
        warnings.append("Loads are marked factored. Serviceability comparisons should normally use service-level loads.")

    status = "ready" if not missing and not errors else "blocked"
    return {
        "status": status,
        "missing_inputs": missing,
        "errors": errors,
        "warnings": warnings,
        "deflection_ready": not deflection_missing and not any(field in err for field in ("E_ksi", "Ix_in4") for err in errors),
        "engineer_review_required": True,
    }
