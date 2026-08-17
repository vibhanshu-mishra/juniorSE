from __future__ import annotations
import importlib.util, math, sys
from pathlib import Path
from typing import Any, Dict
from validator import validate

HERE=Path(__file__).resolve().parent; STEEL=HERE.parent

def _load(skill:str,name:str="calculator"):
    p=STEEL/skill/f"{name}.py"; key=f"juniorse_{skill}_{name}"; spec=importlib.util.spec_from_file_location(key,p); mod=importlib.util.module_from_spec(spec)
    old=list(sys.path); sys.path.insert(0,str(p.parent))
    try: spec.loader.exec_module(mod)
    finally: sys.path[:]=old
    return mod

CLASS=_load("steel-section-classification")
FLEX=_load("steel-flexure-check")
SHEAR=_load("steel-shear-check")
WEBLOCAL=_load("steel-web-local-checks")

def _uniform(w:float,L:float):
    return {"uniform_load_plf":w,"reaction_each_end_lb":w*L/2,"max_shear_lb":w*L/2,"max_moment_kip_ft":w*L**2/8000}

def _delta(w:float,Lft:float,Eksi:float,I:float):
    L=Lft*12; return 5*(w/12)*L**4/(384*(Eksi*1000)*I)

def calculate(i:Dict[str,Any])->Dict[str,Any]:
    v=validate(i)
    if v["status"]!="ready":return {"status":"blocked","validation":v}
    method=str(i["design_method"]).upper();L=float(i["span_ft"]);D=float(i["dead_load_plf"]);LL=float(i["live_load_plf"]);service=D+LL
    strength_w=float(i.get("strength_uniform_load_plf",service));service_a=_uniform(service,L);strength_a=_uniform(strength_w,L)
    live_delta=_delta(LL,L,float(i["E_ksi"]),float(i["Ix_in4"]));total_delta=_delta(service,L,float(i["E_ksi"]),float(i["Ix_in4"]));Lin=L*12
    serviceability={"live_load_deflection_in":live_delta,"live_load_limit_in":Lin/240,"live_load_dcr":live_delta/(Lin/240),"live_load_passes_L_over_240":live_delta<=Lin/240,"dead_plus_live_deflection_in":total_delta,"dead_plus_live_limit_in":Lin/360,"dead_plus_live_dcr":total_delta/(Lin/360),"dead_plus_live_passes_L_over_360":total_delta<=Lin/360}
    c=CLASS.calculate({k:i[k] for k in ["E_ksi","Fy_ksi","bf_in","tf_in","h_in","tw_in"]})
    f=FLEX.calculate({"design_method":method,"E_ksi":i["E_ksi"],"Fy_ksi":i["Fy_ksi"],"Sx_in3":i["Sx_in3"],"Zx_in3":i["Zx_in3"],"ry_in":i["ry_in"],"rts_in":i["rts_in"],"J_in4":i["J_in4"],"ho_in":i["ho_in"],"Lb_ft":i["Lb_ft"],"Cb":i["Cb"],"flange_classification":c["flange"]["classification"],"web_classification":c["web"]["classification"],"flange_lambda":c["flange"]["lambda"],"flange_lambda_p":c["flange"]["lambda_p"],"flange_lambda_r":c["flange"]["lambda_r"],"h_in":i["h_in"],"tw_in":i["tw_in"],"required_moment_kip_ft":strength_a["max_moment_kip_ft"]})
    s=SHEAR.calculate({"design_method":method,"E_ksi":i["E_ksi"],"Fy_ksi":i["Fy_ksi"],"h_in":i["h_in"],"tw_in":i["tw_in"],"required_shear_kips":strength_a["max_shear_lb"]/1000})
    if all(i.get(k) not in (None,"") for k in ["concentrated_force_kips","bearing_length_N_in","distance_from_end_in","k_in"]):
        wl=WEBLOCAL.calculate({"design_method":method,"E_ksi":i["E_ksi"],"Fy_ksi":i["Fy_ksi"],"d_in":i["d_in"],"tw_in":i["tw_in"],"tf_in":i["tf_in"],"k_in":i["k_in"],"bearing_length_N_in":i["bearing_length_N_in"],"concentrated_force_kips":i["concentrated_force_kips"],"distance_from_end_in":i["distance_from_end_in"]})
    else: wl={"status":"not_requested"}
    checks=[serviceability["live_load_dcr"],serviceability["dead_plus_live_dcr"],s.get("dcr",0)]
    if f.get("status")=="complete":checks.append(f["dcr"])
    if wl.get("status")=="complete":checks.extend([wl["web_local_yielding"]["dcr"],wl["web_local_crippling"]["dcr"]])
    blocked=f.get("status")!="complete"
    passed=(not blocked and serviceability["live_load_passes_L_over_240"] and serviceability["dead_plus_live_passes_L_over_360"] and s.get("passes") is True and (wl.get("status")!="complete" or wl.get("passes") is True))
    return {"status":"blocked_chapter_f_route" if blocked else "complete_phase_1_bounded_check","validation":v,"analysis_results":{"dead_plus_live_service":service_a,"strength_uniform_load":strength_a},"serviceability":serviceability,"strength_checks":{"chapter_b_classification":c,"chapter_f_flexure":f,"chapter_g_shear":s,"chapter_j10_web_local":wl},"overall":{"passes_current_bounded_scope":passed,"max_reported_dcr":max(checks) if checks else None},"engineer_review_required":True}
