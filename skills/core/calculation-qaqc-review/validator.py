"""Validator for juniorSE calculation-qaqc-review outputs."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None

EMBEDDED_RULES = {
    "required_calc_sections": ["task_classification", "input_summary", "assumptions", "code_design_basis", "load_combination_basis", "calculation_steps", "limit_state_checks", "serviceability_checks", "governing_result", "qaqc_review", "engineer_review_notes"],
    "required_qaqc_checks": ["input_completeness_checked", "units_checked", "code_basis_stated", "design_method_consistent", "load_level_consistent", "governing_result_reported", "engineer_review_required"],
    "blocked_if_missing": ["code_design_basis", "calculation_steps", "governing_result", "engineer_review_notes"],
}


def load_rules() -> Dict[str, Any]:
    rules_path = Path(__file__).with_name("rules.yaml")
    if yaml is not None and rules_path.exists():
        return yaml.safe_load(rules_path.read_text())
    return EMBEDDED_RULES


def validate(calc_output: Dict[str, Any], rules: Dict[str, Any] | None = None) -> Dict[str, Any]:
    rules = rules or load_rules()
    missing_sections = [field for field in rules.get("required_calc_sections", []) if calc_output.get(field) in (None, "", [])]
    errors: List[str] = []
    warnings: List[str] = []

    for field in rules.get("blocked_if_missing", []):
        if calc_output.get(field) in (None, "", []):
            errors.append(f"Missing critical calculation section: {field}.")

    qaqc = calc_output.get("qaqc_review", {}) or {}
    if isinstance(qaqc, list):
        completed = set(qaqc)
    elif isinstance(qaqc, dict):
        completed = {key for key, value in qaqc.items() if value is True}
    else:
        completed = set()

    missing_qaqc = [check for check in rules.get("required_qaqc_checks", []) if check not in completed]
    if missing_qaqc:
        errors.append(f"Missing required QA/QC checks: {', '.join(missing_qaqc)}.")

    if calc_output.get("engineer_review_required") is not True:
        errors.append("engineer_review_required must be True.")

    if missing_sections and not errors:
        warnings.append("Calculation output has missing non-critical sections.")

    return {
        "status": "ready" if not errors else "blocked",
        "missing_sections": missing_sections,
        "missing_qaqc_checks": missing_qaqc,
        "errors": errors,
        "warnings": warnings,
        "engineer_review_required": True,
    }
