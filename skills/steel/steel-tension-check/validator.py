from __future__ import annotations
from typing import Any, Dict

REQUIRED = ['design_method', 'Fy_ksi', 'Fu_ksi', 'Ag_in2', 'required_tension_kip']


def _num(v: Any):
    try:
        return float(v)
    except Exception:
        return None


def validate(i: Dict[str, Any]) -> Dict[str, Any]:
    missing = [k for k in REQUIRED if i.get(k) in (None, '')]
    errors = []

    method = str(i.get('design_method', '')).upper()
    if method not in {'ASD', 'LRFD'}:
        errors.append('design_method must be ASD or LRFD.')

    for k in ['Fy_ksi', 'Fu_ksi', 'Ag_in2']:
        if k in missing:
            continue
        v = _num(i.get(k))
        if v is None or v <= 0:
            errors.append(f'{k} must be positive.')

    if 'required_tension_kip' not in missing:
        v = _num(i.get('required_tension_kip'))
        if v is None or v < 0:
            errors.append('required_tension_kip must be nonnegative.')

    # A complete Chapter D tensile strength check must include a valid effective-net-area path.
    ae = i.get('Ae_in2')
    an = i.get('An_in2')
    u = i.get('U')
    if ae in (None, ''):
        if an in (None, ''):
            errors.append('Provide Ae_in2 directly or provide An_in2 together with U for net-section rupture.')
        if u in (None, ''):
            errors.append('Provide U when Ae_in2 is not supplied; juniorSE will not invent a shear-lag factor.')

    ag = _num(i.get('Ag_in2'))
    if ae not in (None, ''):
        aev = _num(ae)
        if aev is None or aev <= 0:
            errors.append('Ae_in2 must be positive.')
        elif ag is not None and aev > ag:
            errors.append('Ae_in2 cannot exceed Ag_in2.')

    if an not in (None, ''):
        anv = _num(an)
        if anv is None or anv <= 0:
            errors.append('An_in2 must be positive.')
        elif ag is not None and anv > ag:
            errors.append('An_in2 cannot exceed Ag_in2.')

    if u not in (None, ''):
        uv = _num(u)
        if uv is None or not (0 < uv <= 1):
            errors.append('U must be numeric with 0 < U <= 1.0.')

    # Optional slenderness advisory inputs must appear as a pair.
    L = i.get('member_length_in')
    r = i.get('r_min_in')
    if (L in (None, '')) ^ (r in (None, '')):
        errors.append('member_length_in and r_min_in must be provided together for the optional slenderness advisory.')
    if L not in (None, '') and (_num(L) is None or _num(L) <= 0):
        errors.append('member_length_in must be positive.')
    if r not in (None, '') and (_num(r) is None or _num(r) <= 0):
        errors.append('r_min_in must be positive.')

    return {
        'status': 'ready' if not missing and not errors else 'blocked',
        'missing_inputs': missing,
        'errors': errors,
        'engineer_review_required': True,
    }
