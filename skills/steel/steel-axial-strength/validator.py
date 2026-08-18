from __future__ import annotations
from typing import Any, Dict

REQUIRED = ['sign_convention', 'required_axial_kip', 'member_inputs']
ALLOWED_SIGN_CONVENTIONS = {'tension_positive'}


def _num(v: Any):
    try:
        return float(v)
    except Exception:
        return None


def validate(i: Dict[str, Any]) -> Dict[str, Any]:
    missing = [k for k in REQUIRED if i.get(k) is None]
    errors = []

    if i.get('sign_convention') not in ALLOWED_SIGN_CONVENTIONS:
        errors.append('sign_convention must be tension_positive for Phase 3C.')

    force = _num(i.get('required_axial_kip'))
    if 'required_axial_kip' not in missing and force is None:
        errors.append('required_axial_kip must be numeric.')

    member_inputs = i.get('member_inputs')
    if 'member_inputs' not in missing and not isinstance(member_inputs, dict):
        errors.append('member_inputs must be an object/dictionary.')

    if isinstance(member_inputs, dict) and force is not None:
        if force > 0 and 'required_tension_kip' in member_inputs:
            errors.append('member_inputs must not include required_tension_kip; the orchestrator derives it from required_axial_kip.')
        if force < 0 and 'required_compression_kip' in member_inputs:
            errors.append('member_inputs must not include required_compression_kip; the orchestrator derives it from required_axial_kip.')

    return {
        'status': 'ready' if not missing and not errors else 'blocked',
        'missing_inputs': missing,
        'errors': errors,
        'engineer_review_required': True,
    }
