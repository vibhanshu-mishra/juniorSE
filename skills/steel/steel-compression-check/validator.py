from __future__ import annotations
from typing import Any, Dict

REQUIRED = [
    'design_method','section_type','Fy_ksi','E_ksi','Ag_in2','required_compression_kip',
    'Lx_in','Ly_in','Kx','Ky','rx_in','ry_in','bf_in','tf_in','h_in','tw_in',
    'e4_review_status'
]

ALLOWED_SECTIONS = {'rolled_I','built_up_I'}
ALLOWED_E4 = {'checked_separately_non_governing','not_required_for_this_case'}


def _num(v: Any):
    try:
        return float(v)
    except Exception:
        return None


def validate(i: Dict[str, Any]) -> Dict[str, Any]:
    missing = [k for k in REQUIRED if i.get(k) in (None, '')]
    errors = []

    method = str(i.get('design_method','')).upper()
    if method not in {'ASD','LRFD'}:
        errors.append('design_method must be ASD or LRFD.')

    if i.get('section_type') not in ALLOWED_SECTIONS:
        errors.append('Phase 3B supports section_type rolled_I or built_up_I only.')

    if i.get('e4_review_status') not in ALLOWED_E4:
        errors.append('e4_review_status must explicitly confirm that Chapter E4 torsional/flexural-torsional buckling is not governing or not required for this case.')

    positive = ['Fy_ksi','E_ksi','Ag_in2','Lx_in','Ly_in','Kx','Ky','rx_in','ry_in','bf_in','tf_in','h_in','tw_in']
    for k in positive:
        if k in missing:
            continue
        v = _num(i.get(k))
        if v is None or v <= 0:
            errors.append(f'{k} must be positive.')

    if 'required_compression_kip' not in missing:
        v = _num(i.get('required_compression_kip'))
        if v is None or v < 0:
            errors.append('required_compression_kip must be nonnegative.')

    return {
        'status': 'ready' if not missing and not errors else 'blocked',
        'missing_inputs': missing,
        'errors': errors,
        'engineer_review_required': True,
    }
