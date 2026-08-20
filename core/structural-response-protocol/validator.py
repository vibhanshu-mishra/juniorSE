"""Validator for juniorSE structural-response-protocol outputs."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None

EMBEDDED_RULES = {
    "required_output_sections": [
        "task_classification", "input_summary", "missing_inputs", "assumptions",
        "code_design_basis", "selected_skill_path", "calculation_or_reasoning",
        "qaqc_review", "engineer_review_notes",
    ],
    "blocked_if_missing": ["task_classification", "selected_skill_path", "engineer_review_notes"],
    "forbidden_phrases": ["final approved design", "safe for construction", "stamped design", "no engineer review needed"],
    "required_flags": {"engineer_review_required": True},
}


def load_rules() -> Dict[str, Any]:
    rules_path = Path(__file__).with_name("rules.yaml")
    if yaml is not None and rules_path.exists():
        return yaml.safe_load(rules_path.read_text())
    return EMBEDDED_RULES


def _combined_text(output: Dict[str, Any]) -> str:
    parts: List[str] = []
    for value in output.values():
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, (list, tuple)):
            parts.extend(str(item) for item in value)
        elif isinstance(value, dict):
            parts.extend(str(item) for item in value.values())
    return "\n".join(parts).lower()


def validate(output: Dict[str, Any], rules: Dict[str, Any] | None = None) -> Dict[str, Any]:
    rules = rules or load_rules()
    required = rules.get("required_output_sections", [])
    missing_sections = [field for field in required if output.get(field) in (None, "", [])]

    errors: List[str] = []
    warnings: List[str] = []

    for field in rules.get("blocked_if_missing", []):
        if output.get(field) in (None, "", []):
            errors.append(f"Missing critical response section: {field}.")

    combined = _combined_text(output)
    for phrase in rules.get("forbidden_phrases", []):
        if phrase.lower() in combined:
            errors.append(f"Forbidden final-design language detected: {phrase}.")

    required_flags = rules.get("required_flags", {})
    for flag, expected in required_flags.items():
        if output.get(flag) is not expected:
            errors.append(f"{flag} must be {expected}.")

    if missing_sections and not errors:
        warnings.append("Response is incomplete but not blocked by a critical section rule.")

    return {
        "status": "ready" if not errors else "blocked",
        "missing_sections": missing_sections,
        "errors": errors,
        "warnings": warnings,
        "engineer_review_required": True,
    }
