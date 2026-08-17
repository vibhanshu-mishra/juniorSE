from __future__ import annotations
import math
from typing import Any, Dict
import importlib.util
from pathlib import Path

def _load_local_validator():
    p = Path(__file__).with_name('validator.py')
    spec = importlib.util.spec_from_file_location(f'juniorse_{p.parent.name}_validator', p)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod.validate
validate = _load_local_validator()

def available(Mn: float, method: str) -> float:
    return 0.90*Mn if method == 'LRFD' else Mn/1.67

def _finish(route: str, candidates_in: Dict[str,float], method: str, demand: float, extra: Dict[str,Any]) -> Dict[str,Any]:
    governing = min(candidates_in, key=candidates_in.get)
    Mn_ft = candidates_in[governing]/12.0
    av = available(Mn_ft, method)
    dcr = demand/av if av else math.inf
    return {
        'status':'complete','chapter_f_route':route,
        'limit_state_nominal_strengths_kip_ft':{k:v/12.0 for k,v in candidates_in.items()},
        'governing_limit_state':governing,'nominal_strength_Mn_kip_ft':Mn_ft,
        'available_strength_kip_ft':av,'required_strength_kip_ft':demand,
        'dcr':dcr,'passes':dcr<=1.0,'engineer_review_required':True,**extra
    }

def _f2_f3(i: Dict[str,Any]) -> Dict[str,Any]:
    web=str(i['web_classification']).lower(); flange=str(i['flange_classification']).lower()
    E,Fy,Sx,Zx,ry,rts,J,ho,Lb,Cb=map(float,[i['E_ksi'],i['Fy_ksi'],i['Sx_in3'],i['Zx_in3'],i['ry_in'],i['rts_in'],i['J_in4'],i['ho_in'],i['Lb_ft'],i['Cb']])
    Lb*=12; Mp=Fy*Zx; Lp=1.76*ry*math.sqrt(E/Fy); term=J/(Sx*ho)
    Lr=1.95*rts*E/(0.7*Fy)*math.sqrt(term+math.sqrt(term**2+6.76*(0.7*Fy/E)**2))
    if Lb<=Lp: Mn_ltb=Mp; region='yielding region, Lb <= Lp'
    elif Lb<=Lr:
        Mn_ltb=min(Cb*(Mp-(Mp-0.7*Fy*Sx)*(Lb-Lp)/(Lr-Lp)),Mp); region='inelastic LTB'
    else:
        Fcr=(Cb*math.pi**2*E/(Lb/rts)**2)*math.sqrt(1+0.078*term*(Lb/rts)**2); Mn_ltb=min(Fcr*Sx,Mp); region='elastic LTB'
    candidates={'yielding':Mp,'lateral_torsional_buckling':Mn_ltb}; route='F2'
    if flange!='compact':
        route='F3'; lam=float(i['flange_lambda']); lp=float(i['flange_lambda_p']); lr=float(i['flange_lambda_r'])
        if flange=='noncompact': Mn_flb=Mp-(Mp-0.7*Fy*Sx)*(lam-lp)/(lr-lp)
        else:
            h,tw=float(i['h_in']),float(i['tw_in']); kc=max(0.35,min(0.76,4.0/math.sqrt(h/tw))); Mn_flb=0.9*E*kc*Sx/(lam**2)
        candidates['compression_flange_local_buckling']=Mn_flb
    return _finish(route,candidates,str(i['design_method']).upper(),float(i['required_moment_kip_ft']),{'ltb_region':region,'Lp_ft':Lp/12,'Lr_ft':Lr/12})

def _common_f4f5(i: Dict[str,Any]):
    E=float(i['E_ksi']); Fy=float(i['Fy_ksi']); Sxc=float(i['Sx_in3']); Sxt=float(i.get('Sxt_in3',Sxc)); Zx=float(i['Zx_in3'])
    J=float(i['J_in4']); ho=float(i['ho_in']); Lb=float(i['Lb_ft'])*12; Cb=float(i['Cb']); bf=float(i['bf_in']); tf=float(i['tf_in']); h=float(i['h_in']); hc=float(i.get('hc_in',h)); tw=float(i['tw_in'])
    lamf=float(i['flange_lambda']); lpf=float(i['flange_lambda_p']); lrf=float(i['flange_lambda_r']); lamw=float(i['web_lambda']); lpw=float(i['web_lambda_p']); lrw=float(i['web_lambda_r'])
    aw=hc*tw/(bf*tf)
    rt=bf/math.sqrt(12.0*(1.0+aw/6.0))
    kc=max(0.35,min(0.76,4.0/math.sqrt(h/tw)))
    Mp=min(Fy*Zx,1.6*Fy*Sxc)
    return E,Fy,Sxc,Sxt,J,ho,Lb,Cb,bf,tf,h,hc,tw,lamf,lpf,lrf,lamw,lpw,lrw,aw,rt,kc,Mp

def _f4(i: Dict[str,Any]) -> Dict[str,Any]:
    E,Fy,Sxc,Sxt,J,ho,Lb,Cb,bf,tf,h,hc,tw,lamf,lpf,lrf,lamw,lpw,lrw,aw,rt,kc,Mp=_common_f4f5(i)
    Myc=Fy*Sxc; ratio=Mp/Myc
    Rpc=ratio if lamw<=lpw else ratio-(ratio-1.0)*(lamw-lpw)/(lrw-lpw)
    Rpc=min(Rpc,ratio)
    FL=0.7*Fy
    Mn_cfy=Rpc*Myc
    Lp=1.1*rt*math.sqrt(E/Fy)
    jt=J/(Sxc*ho)
    Lr=1.95*rt*E/FL*math.sqrt(jt+math.sqrt(jt**2+6.76*(FL/E)**2))
    if Lb<=Lp:
        Mn_ltb=Mn_cfy; region='Lb <= Lp'
    elif Lb<=Lr:
        Mn_ltb=min(Cb*(Mn_cfy-(Mn_cfy-FL*Sxc)*(Lb-Lp)/(Lr-Lp)),Mn_cfy); region='Lp < Lb <= Lr'
    else:
        Fcr=(Cb*math.pi**2*E/(Lb/rt)**2)*math.sqrt(1+0.078*jt*(Lb/rt)**2)
        Mn_ltb=min(Fcr*Sxc,Mn_cfy); region='Lb > Lr'
    candidates={'compression_flange_yielding':Mn_cfy,'lateral_torsional_buckling':Mn_ltb}
    flange=str(i['flange_classification']).lower()
    if flange=='noncompact':
        Mn_flb=Mn_cfy-(Mn_cfy-FL*Sxc)*(lamf-lpf)/(lrf-lpf); candidates['compression_flange_local_buckling']=Mn_flb
    elif flange=='slender':
        candidates['compression_flange_local_buckling']=0.9*E*kc*Sxc/(lamf**2)
    if Sxt < Sxc:
        # Singly symmetric path is intentionally blocked by validator in Phase 1B.
        candidates['tension_flange_yielding']=Fy*Sxt
    return _finish('F4',candidates,str(i['design_method']).upper(),float(i['required_moment_kip_ft']),{'Rpc':Rpc,'aw':aw,'rt_in':rt,'Lp_ft':Lp/12,'Lr_ft':Lr/12,'f4_ltb_region':region,'FL_ksi':FL})

def _f5(i: Dict[str,Any]) -> Dict[str,Any]:
    E,Fy,Sxc,Sxt,J,ho,Lb,Cb,bf,tf,h,hc,tw,lamf,lpf,lrf,lamw,lpw,lrw,aw,rt,kc,Mp=_common_f4f5(i)
    aw_rpg=min(aw,10.0)
    Rpg=min(1.0,1.0-aw_rpg/(1200.0+300.0*aw_rpg)*(hc/tw-5.7*math.sqrt(E/Fy)))
    Rpg=max(0.0,Rpg)
    Mn_cfy=Rpg*Fy*Sxc
    Lp=1.1*rt*math.sqrt(E/Fy)
    Lr=math.pi*rt*math.sqrt(E/(0.7*Fy))
    if Lb<=Lp:
        Fcr_ltb=Fy; region='Lb <= Lp'
    elif Lb<=Lr:
        Fcr_ltb=min(Cb*(Fy-0.3*Fy*(Lb-Lp)/(Lr-Lp)),Fy); region='Lp < Lb <= Lr'
    else:
        Fcr_ltb=min(Cb*math.pi**2*E/(Lb/rt)**2,Fy); region='Lb > Lr'
    Mn_ltb=Rpg*Fcr_ltb*Sxc
    candidates={'compression_flange_yielding':Mn_cfy,'lateral_torsional_buckling':Mn_ltb}
    flange=str(i['flange_classification']).lower()
    if flange=='noncompact':
        Fcr_flb=Fy-0.3*Fy*(lamf-lpf)/(lrf-lpf); candidates['compression_flange_local_buckling']=Rpg*Fcr_flb*Sxc
    elif flange=='slender':
        Fcr_flb=0.9*E*kc/(lamf**2); candidates['compression_flange_local_buckling']=Rpg*Fcr_flb*Sxc
    if Sxt < Sxc: candidates['tension_flange_yielding']=Fy*Sxt
    return _finish('F5',candidates,str(i['design_method']).upper(),float(i['required_moment_kip_ft']),{'Rpg':Rpg,'aw':aw,'rt_in':rt,'Lp_ft':Lp/12,'Lr_ft':Lr/12,'f5_ltb_region':region})

def calculate(i:Dict[str,Any])->Dict[str,Any]:
    v=validate(i)
    if v['status']!='ready': return {'status':'blocked','validation':v}
    web=str(i['web_classification']).lower()
    if web=='compact': return _f2_f3(i)
    if web=='noncompact': return _f4(i)
    return _f5(i)
