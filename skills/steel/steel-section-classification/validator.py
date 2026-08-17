from __future__ import annotations
from typing import Any, Dict

REQUIRED = ["E_ksi", "Fy_ksi", "bf_in", "tf_in", "h_in", "tw_in"]

def _positive(v: Any) -> bool:
    try:
        return float(v) > 0
    except (TypeError, ValueError):
        return False

def validate(inputs: Dict[str, Any]) -> Dict[str, Any]:
    missing = [k for k in REQUIRED if inputs.get(k) in (None, "")]
    errors = [f"{k} must be a positive number." for k in REQUIRED if k not in missing and not _positive(inputs.get(k))]
    return {"status": "ready" if not missing and not errors else "blocked", "missing_inputs": missing, "errors": errors, "engineer_review_required": True}
