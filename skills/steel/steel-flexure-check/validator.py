from __future__ import annotations
from typing import Any, Dict

BASE = [
    'design_method','E_ksi','Fy_ksi','Sx_in3','Zx_in3','J_in4','ho_in','Lb_ft','Cb',
    'flange_classification','web_classification','flange_lambda','flange_lambda_p',
    'flange_lambda_r','h_in','tw_in','required_moment_kip_ft'
]

def _positive(v: Any) -> bool:
    try: return float(v) > 0
    except Exception: return False

def validate(i: Dict[str, Any]) -> Dict[str, Any]:
    web = str(i.get('web_classification','')).lower()
    req = list(BASE)
    if web == 'compact':
        req += ['ry_in','rts_in']
    else:
        req += ['bf_in','tf_in','web_lambda','web_lambda_p','web_lambda_r']
    missing = [k for k in req if i.get(k) in (None,'')]
    errors = []
    if str(i.get('design_method','')).upper() not in {'ASD','LRFD'}:
        errors.append('design_method must be ASD or LRFD.')
    if str(i.get('flange_classification','')).lower() not in {'compact','noncompact','slender'}:
        errors.append('Invalid flange classification.')
    if web not in {'compact','noncompact','slender'}:
        errors.append('Invalid web classification.')
    symmetry = str(i.get('section_symmetry','doubly_symmetric')).lower()
    if web in {'noncompact','slender'} and symmetry != 'doubly_symmetric':
        errors.append('Phase 1B validates F4/F5 only for doubly symmetric I-shaped members; singly symmetric members remain blocked.')
    for k in req:
        if k in missing or k in {'flange_classification','web_classification','design_method'}: continue
        if k == 'required_moment_kip_ft':
            try:
                if float(i[k]) < 0: errors.append(f'{k} must be nonnegative.')
            except Exception: errors.append(f'{k} must be numeric.')
        elif not _positive(i[k]):
            errors.append(f'{k} must be positive.')
    if i.get('Sxt_in3') not in (None,'') and not _positive(i['Sxt_in3']): errors.append('Sxt_in3 must be positive.')
    if i.get('hc_in') not in (None,'') and not _positive(i['hc_in']): errors.append('hc_in must be positive.')
    return {'status':'ready' if not missing and not errors else 'blocked','missing_inputs':missing,'errors':errors,'engineer_review_required':True}
