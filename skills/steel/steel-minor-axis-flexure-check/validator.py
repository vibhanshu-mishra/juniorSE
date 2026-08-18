from __future__ import annotations
from typing import Any, Dict
REQ=['design_method','E_ksi','Fy_ksi','Sy_in3','Zy_in3','bf_in','tf_in','required_moment_kip_ft']
def validate(i:Dict[str,Any])->Dict[str,Any]:
    missing=[k for k in REQ if i.get(k) is None]
    errors=[]
    if str(i.get('design_method','')).upper() not in {'LRFD','ASD'}: errors.append('design_method must be LRFD or ASD.')
    for k in [x for x in REQ if x!='design_method']:
        if i.get(k) is not None:
            try:
                if float(i[k])<=0 and k!='required_moment_kip_ft': errors.append(f'{k} must be > 0.')
                if k=='required_moment_kip_ft' and float(i[k])<0: errors.append('required_moment_kip_ft must be >= 0.')
            except Exception: errors.append(f'{k} must be numeric.')
    return {'status':'ready' if not missing and not errors else 'blocked','missing_inputs':missing,'errors':errors,'engineer_review_required':True}
