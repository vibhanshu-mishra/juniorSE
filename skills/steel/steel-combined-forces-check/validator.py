from __future__ import annotations
from typing import Any, Dict
REQ=['design_method','analysis_basis']
ALLOWED_BASIS={'second_order_or_chapter_c_compatible','chapter_c_demands_provided'}
def validate(i:Dict[str,Any])->Dict[str,Any]:
    missing=[k for k in REQ if i.get(k) is None]
    errors=[]
    if str(i.get('design_method','')).upper() not in {'LRFD','ASD'}: errors.append('design_method must be LRFD or ASD.')
    if i.get('analysis_basis') is not None and i.get('analysis_basis') not in ALLOWED_BASIS: errors.append('analysis_basis must acknowledge that required strengths come from an appropriate Chapter C-compatible or second-order analysis basis.')
    result_keys=['axial_strength_result','major_axis_flexure_result','minor_axis_flexure_result']
    nested_keys=['axial_inputs','major_axis_flexure_inputs','minor_axis_flexure_inputs']
    if not all(i.get(k) is not None for k in result_keys) and not all(i.get(k) is not None for k in nested_keys):
        missing.append('strength_results_or_all_nested_skill_inputs')
    return {'status':'ready' if not missing and not errors else 'blocked','missing_inputs':missing,'errors':errors,'engineer_review_required':True}
