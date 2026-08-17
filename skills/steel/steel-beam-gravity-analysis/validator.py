from __future__ import annotations
import math
from typing import Any, Dict, List

ALLOWED_SUPPORT_TYPES={'pinned','roller','fixed'}
ALLOWED_SHORTHANDS={'simple','simply_supported','simply supported','cantilever','fixed_fixed','fixed-fixed','propped_cantilever','propped-cantilever'}
ALLOWED_CATEGORIES={'dead','live'}


def _num(v):
    try: return float(v)
    except (TypeError, ValueError): return None


def _total_length(inputs:Dict[str,Any])->float:
    spans=inputs.get('spans_ft')
    if isinstance(spans,list) and spans:
        vals=[_num(x) for x in spans]
        return sum(x for x in vals if x is not None)
    return _num(inputs.get('span_ft')) or 0.0


def _stiffness_ready(inputs:Dict[str,Any], total:float)->bool:
    segs=inputs.get('stiffness_segments') or []
    if segs:
        return True
    E=_num(inputs.get('E_ksi')); I=_num(inputs.get('Ix_in4'))
    return E is not None and E>0 and I is not None and I>0


def validate(inputs: Dict[str,Any], rules=None)->Dict[str,Any]:
    errors:List[str]=[]; warnings:List[str]=[]; missing=[]
    load_level=str(inputs.get('load_level','')).lower()
    if not load_level: missing.append('load_level')
    elif load_level not in {'service','factored'}: errors.append('load_level must be service or factored.')

    spans=inputs.get('spans_ft'); span=inputs.get('span_ft')
    if spans in (None,[]) and span in (None,''): missing.append('span_ft or spans_ft')
    if spans not in (None,[]):
        if not isinstance(spans,list) or any((_num(x) is None or _num(x)<=0) for x in spans): errors.append('spans_ft must be a list of positive numbers.')
    elif span not in (None,''):
        n=_num(span)
        if n is None or n<=0: errors.append('span_ft must be positive.')
    total=_total_length(inputs)

    supports=inputs.get('supports')
    shorthand=str(inputs.get('support_condition','')).lower() if inputs.get('support_condition') is not None else ''
    if not supports and not shorthand: missing.append('supports or support_condition')
    if shorthand and shorthand not in ALLOWED_SHORTHANDS: errors.append('Unsupported support_condition shorthand.')
    if supports:
        if not isinstance(supports,list) or len(supports)<1: errors.append('supports must be a nonempty list.')
        else:
            for s in supports:
                if str(s.get('type','')).lower() not in ALLOWED_SUPPORT_TYPES: errors.append('Each support type must be pinned, roller, or fixed.')
                x=_num(s.get('x_ft')); sett=_num(s.get('settlement_in',0.0))
                if x is None or x<0 or (total and x>total): errors.append('Each support x_ft must lie on the beam.')
                if sett is None: errors.append('support settlement_in must be numeric when provided.')
            valid=[s for s in supports if str(s.get('type','')).lower() in ALLOWED_SUPPORT_TYPES]
            xs={float(s['x_ft']) for s in valid if _num(s.get('x_ft')) is not None}
            if not any(str(s.get('type','')).lower()=='fixed' for s in valid) and len(xs)<2:
                errors.append('Support configuration is unstable for beam bending analysis: provide a fixed support or at least two vertical supports at distinct locations.')

    for fld in ('dead_load_plf','live_load_plf'):
        if fld in inputs and inputs[fld] not in (None,''):
            n=_num(inputs[fld])
            if n is None or n<0: errors.append(f'{fld} must be nonnegative.')

    def category_ok(obj,label):
        if str(obj.get('category','')).lower() not in ALLOWED_CATEGORIES: errors.append(f'{label} category must be dead or live.')

    for p in inputs.get('point_loads',[]) or []:
        P=_num(p.get('P_lb')); x=_num(p.get('x_ft')); category_ok(p,'Point-load')
        if P is None or P<0: errors.append('Point loads require nonnegative P_lb.')
        if x is None or x<0 or (total and x>total): errors.append('Point-load x_ft must lie on the beam.')
    for u in inputs.get('uniform_loads',[]) or []:
        w=_num(u.get('w_plf')); a=_num(u.get('x_start_ft')); b=_num(u.get('x_end_ft')); category_ok(u,'Uniform-load')
        if w is None or w<0: errors.append('Uniform loads require nonnegative w_plf.')
        if a is None or b is None or a<0 or b<=a or (total and b>total): errors.append('Uniform-load limits must satisfy 0 <= x_start_ft < x_end_ft <= beam length.')
    for u in inputs.get('linear_loads',[]) or []:
        w1=_num(u.get('w_start_plf')); w2=_num(u.get('w_end_plf')); a=_num(u.get('x_start_ft')); b=_num(u.get('x_end_ft')); category_ok(u,'Linear-load')
        if w1 is None or w2 is None or w1<0 or w2<0: errors.append('Linear loads require nonnegative w_start_plf and w_end_plf.')
        if a is None or b is None or a<0 or b<=a or (total and b>total): errors.append('Linear-load limits must satisfy 0 <= x_start_ft < x_end_ft <= beam length.')
    for m in inputs.get('concentrated_moments',[]) or []:
        M=_num(m.get('M_lb_ft')); x=_num(m.get('x_ft')); category_ok(m,'Concentrated-moment')
        if M is None: errors.append('Concentrated moments require numeric M_lb_ft; sign defines direction.')
        if x is None or x<0 or (total and x>total): errors.append('Concentrated-moment x_ft must lie on the beam.')

    segs=inputs.get('stiffness_segments') or []
    if segs:
        clean=[]
        for s in segs:
            a=_num(s.get('x_start_ft')); b=_num(s.get('x_end_ft')); E=_num(s.get('E_ksi')); I=_num(s.get('Ix_in4'))
            if None in (a,b,E,I) or a<0 or b<=a or (total and b>total) or E<=0 or I<=0:
                errors.append('Each stiffness segment requires valid limits and positive E_ksi and Ix_in4.')
            else: clean.append((a,b))
        if clean:
            clean=sorted(clean)
            if abs(clean[0][0])>1e-9 or abs(clean[-1][1]-total)>1e-9 or any(abs(clean[k][1]-clean[k+1][0])>1e-9 for k in range(len(clean)-1)):
                errors.append('stiffness_segments must cover the full beam continuously without gaps or overlaps.')

    stiffness_ready=_stiffness_ready(inputs,total)
    indeterminate = bool(supports and (len(supports)>2 or any(str(s.get('type','')).lower()=='fixed' for s in supports))) or shorthand in {'fixed_fixed','fixed-fixed','propped_cantilever','propped-cantilever'}
    settlements=any(abs(_num(s.get('settlement_in',0.0)) or 0)>0 for s in (supports or []))
    if (indeterminate or settlements) and not stiffness_ready: errors.append('Beam stiffness is required for indeterminate analysis or support settlement.')
    elif not stiffness_ready: warnings.append('Deflection requires E_ksi/Ix_in4 or stiffness_segments; force results may still be available for statically determinate cases.')

    shear=inputs.get('shear_deformation') or {}
    if shear.get('enabled'):
        G=_num(shear.get('G_ksi')); Av=_num(shear.get('Av_in2'))
        if G is None or G<=0 or Av is None or Av<=0: errors.append('Shear deformation requires positive G_ksi and effective Av_in2; juniorSE will not invent either.')
        if not stiffness_ready: errors.append('Shear deformation also requires bending stiffness.')

    second=inputs.get('second_order') or {}
    if second.get('enabled'):
        P=_num(second.get('axial_force_lb'))
        if P is None: errors.append('Second-order analysis requires numeric axial_force_lb; positive is compression, negative is tension.')
        if not stiffness_ready: errors.append('Second-order analysis requires beam stiffness.')
        # Conservative bounded stability gate for simple pinned-pinned shorthand only.
        if P is not None and P>0 and shorthand in {'simple','simply_supported','simply supported'} and not segs:
            E=_num(inputs.get('E_ksi')); I=_num(inputs.get('Ix_in4'))
            if E and I and total:
                pcr=math.pi**2*(E*1000)*I/(total*12)**2
                if P >= 0.95*pcr:
                    errors.append('Second-order axial force is at or above 95% of the Euler critical load for this bounded simple-span check; rigorous stability analysis is required.')

    for ml in inputs.get('moving_loads',[]) or []:
        category_ok(ml,'Moving-load')
        step=_num(ml.get('step_ft'))
        if step is None or step<=0: errors.append('Each moving-load pattern requires positive step_ft.')
        axles=ml.get('axles') or []
        if not axles: errors.append('Each moving-load pattern requires at least one axle.')
        for a in axles:
            P=_num(a.get('P_lb')); off=_num(a.get('offset_ft'))
            if P is None or P<0 or off is None: errors.append('Moving-load axles require nonnegative P_lb and numeric offset_ft.')

    tors=inputs.get('torsion') or {}
    if tors.get('enabled'):
        G=_num(tors.get('G_ksi')); J=_num(tors.get('J_in4'))
        segt=tors.get('segments') or []
        if not segt and (G is None or G<=0 or J is None or J<=0): errors.append('Saint-Venant torsion requires positive G_ksi and J_in4 or complete torsion segments.')
        restraints=tors.get('restraints') or []
        if not restraints: errors.append('Torsion analysis requires at least one explicit torsional restraint; beam support type does not imply torsional restraint.')
        for x in restraints:
            xx=_num(x)
            if xx is None or xx<0 or (total and xx>total): errors.append('Each torsional restraint must lie on the beam.')
        for t in tors.get('point_torques',[]) or []:
            T=_num(t.get('T_lb_in')); x=_num(t.get('x_ft'))
            if T is None: errors.append('Point torques require numeric T_lb_in; sign defines direction.')
            if x is None or x<0 or (total and x>total): errors.append('Point torque x_ft must lie on the beam.')
        for u in tors.get('distributed_torques',[]) or []:
            t0=_num(u.get('t_start_lb_in_per_ft')); t1=_num(u.get('t_end_lb_in_per_ft')); a=_num(u.get('x_start_ft')); b=_num(u.get('x_end_ft'))
            if t0 is None or t1 is None: errors.append('Distributed torques require numeric start/end torque intensity.')
            if a is None or b is None or a<0 or b<=a or (total and b>total): errors.append('Distributed-torque limits must lie on the beam.')
        for sg in tors.get('segments',[]) or []:
            a=_num(sg.get('x_start_ft')); b=_num(sg.get('x_end_ft')); Gs=_num(sg.get('G_ksi')); Js=_num(sg.get('J_in4'))
            if None in (a,b,Gs,Js) or a<0 or b<=a or (total and b>total) or Gs<=0 or Js<=0: errors.append('Each torsion segment requires valid limits and positive G_ksi and J_in4.')

    if load_level=='factored': warnings.append('Serviceability checks require service-level loads.')
    if second.get('enabled'): warnings.append('Second-order mode is an elastic geometric-stiffness analysis aid, not a complete AISC 360-16 Direct Analysis Method implementation.')
    if tors.get('enabled'): warnings.append('Torsion mode is Saint-Venant torsion only; restrained warping and warping normal stresses are outside this phase.')

    return {'status':'ready' if not missing and not errors else 'blocked','missing_inputs':missing,'errors':errors,'warnings':warnings,'deflection_ready':stiffness_ready,'engineer_review_required':True}
