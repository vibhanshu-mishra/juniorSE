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
        "steel_grade", "member_section",
    ],
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
    missing = [field for field in rules["required_inputs"] if inputs.get(field) in (None, "", [])]
    errors: List[str] = []
    warnings: List[str] = []

    method = inputs.get("design_method")
    if method and str(method).upper() not in rules.get("allowed_design_methods", ["ASD", "LRFD"]):
        errors.append("design_method must be ASD or LRFD.")

    load_level = inputs.get("load_level")
    if load_level and str(load_level).lower() not in rules.get("allowed_load_levels", ["service", "factored"]):
        errors.append("load_level must be service or factored.")

    if inputs.get("support_condition") and str(inputs["support_condition"]).lower() not in {"simple", "simply_supported", "simply supported"}:
        errors.append("Current executable scope only supports simply supported beams.")

    if inputs.get("point_loads"):
        errors.append("Current executable scope does not support point loads yet.")

    if inputs.get("uniform_load_plf") and (inputs.get("dead_load_plf") or inputs.get("live_load_plf")):
        warnings.append("Both uniform_load_plf and D/L loads were supplied. Calculator will use D + L service load unless told otherwise.")

    if str(load_level).lower() == "factored":
        warnings.append("Loads are marked factored. Calculator reports mechanics demand only and will not apply another load factor.")

    status = "ready" if not missing and not errors else "blocked"
    return {
        "status": status,
        "missing_inputs": missing,
        "errors": errors,
        "warnings": warnings,
        "engineer_review_required": True,
    }
