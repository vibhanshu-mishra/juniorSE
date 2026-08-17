from __future__ import annotations
from typing import Any, Dict, List

ALLOWED_SUPPORT_TYPES={'pinned','roller','fixed'}
ALLOWED_SHORTHANDS={'simple','simply_supported','simply supported','cantilever','fixed_fixed','fixed-fixed','propped_cantilever','propped-cantilever'}


def _num(v):
    try: return float(v)
    except (TypeError, ValueError): return None


def validate(inputs: Dict[str,Any], rules=None)->Dict[str,Any]:
    errors:List[str]=[]; warnings:List[str]=[]; missing=[]
    load_level=str(inputs.get('load_level','')).lower()
    if not load_level: missing.append('load_level')
    elif load_level not in {'service','factored'}: errors.append('load_level must be service or factored.')

    spans=inputs.get('spans_ft')
    span=inputs.get('span_ft')
    if spans in (None,[]) and span in (None,''): missing.append('span_ft or spans_ft')
    if spans not in (None,[]):
        if not isinstance(spans,list) or any((_num(x) is None or _num(x)<=0) for x in spans): errors.append('spans_ft must be a list of positive numbers.')
        total=sum(float(x) for x in spans) if isinstance(spans,list) and spans else 0
    else:
        n=_num(span); total=n or 0
        if span not in (None,'') and (n is None or n<=0): errors.append('span_ft must be positive.')

    supports=inputs.get('supports')
    shorthand=str(inputs.get('support_condition','')).lower() if inputs.get('support_condition') is not None else ''
    if not supports and not shorthand: missing.append('supports or support_condition')
    if shorthand and shorthand not in ALLOWED_SHORTHANDS: errors.append('Unsupported support_condition shorthand.')
    if supports:
        if not isinstance(supports,list) or len(supports)<1: errors.append('supports must be a nonempty list.')
        else:
            for s in supports:
                if str(s.get('type','')).lower() not in ALLOWED_SUPPORT_TYPES: errors.append('Each support type must be pinned, roller, or fixed.')
                x=_num(s.get('x_ft'))
                if x is None or x<0 or (total and x>total): errors.append('Each support x_ft must lie on the beam.')
            valid_supports=[s for s in supports if str(s.get('type','')).lower() in ALLOWED_SUPPORT_TYPES]
            distinct_x={float(s['x_ft']) for s in valid_supports if _num(s.get('x_ft')) is not None}
            has_fixed=any(str(s.get('type','')).lower()=='fixed' for s in valid_supports)
            if not has_fixed and len(distinct_x)<2:
                errors.append('Support configuration is unstable for beam bending analysis: provide a fixed support or at least two vertical supports at distinct locations.')

    for fld in ('dead_load_plf','live_load_plf'):
        if fld in inputs and inputs[fld] not in (None,''):
            n=_num(inputs[fld]);
            if n is None or n<0: errors.append(f'{fld} must be nonnegative.')
    for p in inputs.get('point_loads',[]) or []:
        P=_num(p.get('P_lb')); x=_num(p.get('x_ft'))
        if P is None or P<0: errors.append('Point loads require nonnegative P_lb.')
        if x is None or x<0 or (total and x>total): errors.append('Point-load x_ft must lie on the beam.')
        if str(p.get('category','')).lower() not in {'dead','live'}: errors.append('Point-load category must be dead or live.')
    for u in inputs.get('uniform_loads',[]) or []:
        w=_num(u.get('w_plf')); a=_num(u.get('x_start_ft')); b=_num(u.get('x_end_ft'))
        if w is None or w<0: errors.append('Uniform loads require nonnegative w_plf.')
        if a is None or b is None or a<0 or b<=a or (total and b>total): errors.append('Uniform-load limits must satisfy 0 <= x_start_ft < x_end_ft <= beam length.')
        if str(u.get('category','')).lower() not in {'dead','live'}: errors.append('Uniform-load category must be dead or live.')

    E=_num(inputs.get('E_ksi')); I=_num(inputs.get('Ix_in4'))
    stiffness_ready=E is not None and E>0 and I is not None and I>0
    indeterminate = bool(supports and (len(supports)>2 or any(str(s.get('type','')).lower()=='fixed' for s in supports))) or shorthand in {'fixed_fixed','fixed-fixed','propped_cantilever','propped-cantilever'}
    if indeterminate and not stiffness_ready: errors.append('E_ksi and Ix_in4 are required for indeterminate beam analysis and deflection.')
    elif not stiffness_ready: warnings.append('Deflection requires E_ksi and Ix_in4; force results may still be available for statically determinate cases.')
    if load_level=='factored': warnings.append('Serviceability checks require service-level loads.')
    return {'status':'ready' if not missing and not errors else 'blocked','missing_inputs':missing,'errors':errors,'warnings':warnings,'deflection_ready':stiffness_ready,'engineer_review_required':True}
