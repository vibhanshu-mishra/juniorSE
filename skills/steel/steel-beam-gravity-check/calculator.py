from __future__ import annotations
import importlib.util, math, sys
from pathlib import Path
from typing import Any, Dict

HERE=Path(__file__).resolve().parent; STEEL=HERE.parent

def _load_file(path:Path,key:str):
    spec=importlib.util.spec_from_file_location(key,path); mod=importlib.util.module_from_spec(spec)
    old=list(sys.path); sys.path.insert(0,str(path.parent))
    try: spec.loader.exec_module(mod)
    finally: sys.path[:]=old
    return mod

validate=_load_file(HERE/'validator.py','juniorse_beam_check_validator').validate

def _load(skill:str): return _load_file(STEEL/skill/'calculator.py',f'juniorse_{skill}_calculator')
CLASS=_load('steel-section-classification'); FLEX=_load('steel-flexure-check'); SHEAR=_load('steel-shear-check'); WEBLOCAL=_load('steel-web-local-checks')

def _base_flex(i,c,demand):
    return FLEX.calculate({"design_method":str(i["design_method"]).upper(),"section_symmetry":"doubly_symmetric","E_ksi":i["E_ksi"],"Fy_ksi":i["Fy_ksi"],"Sx_in3":i["Sx_in3"],"Sxt_in3":i["Sx_in3"],"Zx_in3":i["Zx_in3"],"ry_in":i["ry_in"],"rts_in":i["rts_in"],"J_in4":i["J_in4"],"ho_in":i["ho_in"],"Lb_ft":i["Lb_ft"],"Cb":i["Cb"],"bf_in":i["bf_in"],"tf_in":i["tf_in"],"flange_classification":c["flange"]["classification"],"web_classification":c["web"]["classification"],"flange_lambda":c["flange"]["lambda"],"flange_lambda_p":c["flange"]["lambda_p"],"flange_lambda_r":c["flange"]["lambda_r"],"web_lambda":c["web"]["lambda"],"web_lambda_p":c["web"]["lambda_p"],"web_lambda_r":c["web"]["lambda_r"],"h_in":i["h_in"],"hc_in":i["h_in"],"tw_in":i["tw_in"],"required_moment_kip_ft":abs(float(demand))})

def _resolve_support_reaction(ar,x_ft,case_name=None):
    analyses=ar.get('analysis_results') or {}
    names=[case_name] if case_name else ['dead_plus_live','dead_load','live_load']
    candidates=[]
    for name in names:
        case=analyses.get(name)
        if not case: continue
        for r in case.get('support_reactions',[]):
            if abs(float(r.get('x_ft',0))-float(x_ft))<1e-6:
                candidates.append((abs(float(r.get('vertical_lb',0)))/1000.0,name,float(r.get('vertical_lb',0))/1000.0))
    if not candidates: raise ValueError(f'No analyzed support reaction found at x={x_ft} ft.')
    return max(candidates,key=lambda z:z[0])

def _web_local(i,ar):
    cases=[]
    for spec in i.get('web_local_cases',[]) or []:
        src=str(spec['source']).lower()
        if src=='support_reaction':
            mag,case_name,signed=_resolve_support_reaction(ar,float(spec['x_ft']),spec.get('analysis_case')); force=mag
            source_detail={'analysis_case':case_name,'signed_reaction_kips':signed}
        else:
            force=abs(float(spec['force_kips'])); source_detail={}
        result=WEBLOCAL.calculate({'design_method':str(i['design_method']).upper(),'E_ksi':i['E_ksi'],'Fy_ksi':i['Fy_ksi'],'d_in':i['d_in'],'tw_in':i['tw_in'],'tf_in':i['tf_in'],'k_in':spec['k_in'],'bearing_length_N_in':spec['bearing_length_N_in'],'concentrated_force_kips':force,'distance_from_end_in':spec['distance_from_end_in']})
        cases.append({'name':spec.get('name','web local case'),'source':src,'resolved_force_kips':force,**source_detail,'result':result})
    if not cases:return {'status':'not_requested','cases':[]}
    dcrs=[]
    for c in cases:
        r=c['result']
        if r.get('status')=='complete':dcrs += [r['web_local_yielding']['dcr'],r['web_local_crippling']['dcr']]
    return {'status':'complete','cases':cases,'max_dcr':max(dcrs) if dcrs else None,'passes':all(c['result'].get('passes') is True for c in cases)}

def _service_from_analysis(i,ar):
    sar=i.get('service_analysis_result') or ar
    svc=sar.get('serviceability') or {'status':'not_checked'}
    return svc

def _calculate_envelope(i,v):
    ar=i['analysis_result']; env=ar['demand_envelope']; method=str(i['design_method']).upper()
    c=CLASS.calculate({k:i[k] for k in ['E_ksi','Fy_ksi','bf_in','tf_in','h_in','tw_in']})
    pos=max(0.0,float(env.get('max_positive_moment_kip_ft',0.0))); neg=min(0.0,float(env.get('min_negative_moment_kip_ft',0.0)))
    fp=_base_flex(i,c,pos); fp['demand_sign']='positive'; fp['demand_location_ft']=env.get('max_positive_moment_location_ft'); fp['demand_case']=env.get('max_positive_moment_case')
    fn=_base_flex(i,c,abs(neg)); fn['demand_sign']='negative'; fn['demand_location_ft']=env.get('min_negative_moment_location_ft'); fn['demand_case']=env.get('min_negative_moment_case')
    shear=SHEAR.calculate({'design_method':method,'E_ksi':i['E_ksi'],'Fy_ksi':i['Fy_ksi'],'h_in':i['h_in'],'tw_in':i['tw_in'],'required_shear_kips':float(env['max_abs_shear_kips'])})
    shear['demand_location_ft']=env.get('max_abs_shear_location_ft'); shear['demand_case']=env.get('max_abs_shear_case')
    wl=_web_local(i,ar); service=_service_from_analysis(i,ar)
    dcrs=[fp.get('dcr',0),fn.get('dcr',0),shear.get('dcr',0)]
    if wl.get('max_dcr') is not None:dcrs.append(wl['max_dcr'])
    if service.get('status')=='checked':
        dcrs += [service.get('live_load_ratio_to_L_over_240',0),service.get('dead_plus_live_ratio_to_L_over_360',0)]
    strength_pass=fp.get('passes') is True and fn.get('passes') is True and shear.get('passes') is True and (wl.get('status')!='complete' or wl.get('passes') is True)
    service_pass=True if service.get('status')!='checked' else service.get('live_load_passes_L_over_240') is True and service.get('dead_plus_live_passes_L_over_360') is True
    torsion=ar.get('torsion_analysis')
    return {'status':'complete_envelope_strength_check','validation':v,'demand_source':'analysis_result.demand_envelope','analysis_metadata':{'analysis_method':ar.get('analysis_method'),'moving_load_envelope_used':ar.get('moving_load_envelope') is not None,'torsion_present':torsion is not None},'demand_envelope':env,'serviceability':service,'strength_checks':{'chapter_b_classification':c,'chapter_f_flexure':{'positive':fp,'negative':fn,'governing_sign':'positive' if fp.get('dcr',0)>=fn.get('dcr',0) else 'negative'},'chapter_g_shear':shear,'chapter_j10_web_local':wl},'torsion_status':{'status':'reported_not_checked_by_F_G_J10','analysis':torsion} if torsion else {'status':'not_present'},'overall':{'passes_current_scope':strength_pass and service_pass,'max_reported_dcr':max(dcrs) if dcrs else None},'engineer_review_required':True}

def _uniform(w,L):return {'max_moment_kip_ft':w*L**2/8000,'max_shear_kips':w*L/2000}

def _legacy_delta(w,Lft,Eksi,I):
    L=Lft*12.0
    return 5.0*(w/12.0)*L**4/(384.0*(Eksi*1000.0)*I)

def _calculate_legacy(i,v):
    # Backward-compatible Phase 1 simple-span UDL path. Generalized work should use analysis_result mode.
    method=str(i['design_method']).upper(); L=float(i['span_ft']); D=float(i['dead_load_plf']); LL=float(i['live_load_plf']); service=D+LL; strength_w=float(i.get('strength_uniform_load_plf',service))
    dem=_uniform(strength_w,L); Lin=L*12.0
    live_delta=_legacy_delta(LL,L,float(i['E_ksi']),float(i['Ix_in4'])); total_delta=_legacy_delta(service,L,float(i['E_ksi']),float(i['Ix_in4']))
    serviceability={'live_load_deflection_in':live_delta,'live_load_limit_in':Lin/240.0,'live_load_dcr':live_delta/(Lin/240.0),'live_load_passes_L_over_240':live_delta<=Lin/240.0,'dead_plus_live_deflection_in':total_delta,'dead_plus_live_limit_in':Lin/360.0,'dead_plus_live_dcr':total_delta/(Lin/360.0),'dead_plus_live_passes_L_over_360':total_delta<=Lin/360.0}
    c=CLASS.calculate({k:i[k] for k in ['E_ksi','Fy_ksi','bf_in','tf_in','h_in','tw_in']})
    f=_base_flex(i,c,dem['max_moment_kip_ft'])
    shear=SHEAR.calculate({'design_method':method,'E_ksi':i['E_ksi'],'Fy_ksi':i['Fy_ksi'],'h_in':i['h_in'],'tw_in':i['tw_in'],'required_shear_kips':dem['max_shear_kips']})
    old_local=['concentrated_force_kips','bearing_length_N_in','distance_from_end_in','k_in']
    if all(i.get(k) not in (None,'') for k in old_local):
        wl=WEBLOCAL.calculate({'design_method':method,'E_ksi':i['E_ksi'],'Fy_ksi':i['Fy_ksi'],'d_in':i['d_in'],'tw_in':i['tw_in'],'tf_in':i['tf_in'],'k_in':i['k_in'],'bearing_length_N_in':i['bearing_length_N_in'],'concentrated_force_kips':i['concentrated_force_kips'],'distance_from_end_in':i['distance_from_end_in']})
    else: wl={'status':'not_requested'}
    dcrs=[serviceability['live_load_dcr'],serviceability['dead_plus_live_dcr'],f.get('dcr',0),shear.get('dcr',0)]
    if wl.get('status')=='complete': dcrs += [wl['web_local_yielding']['dcr'],wl['web_local_crippling']['dcr']]
    passes=f.get('passes') is True and shear.get('passes') is True and serviceability['live_load_passes_L_over_240'] and serviceability['dead_plus_live_passes_L_over_360'] and (wl.get('status')!='complete' or wl.get('passes') is True)
    return {'status':'complete_phase_1_bounded_check','validation':v,'demand_source':'legacy_simple_span_uniform_load','serviceability':serviceability,'strength_checks':{'chapter_b_classification':c,'chapter_f_flexure':f,'chapter_g_shear':shear,'chapter_j10_web_local':wl},'overall':{'passes_current_bounded_scope':passes,'max_reported_dcr':max(dcrs)},'engineer_review_required':True}

def calculate(i:Dict[str,Any])->Dict[str,Any]:
    v=validate(i)
    if v['status']!='ready':return {'status':'blocked','validation':v}
    return _calculate_envelope(i,v) if v['mode']=='analysis_result' else _calculate_legacy(i,v)
