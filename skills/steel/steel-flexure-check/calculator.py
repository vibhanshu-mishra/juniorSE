from __future__ import annotations
import math
from typing import Any, Dict
import importlib.util
from pathlib import Path

def _load_local_validator():
    p = Path(__file__).with_name("validator.py")
    spec = importlib.util.spec_from_file_location(f"juniorse_{p.parent.name}_validator", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.validate

validate = _load_local_validator()

def available(Mn:float,method:str)->float:
    return 0.90*Mn if method=="LRFD" else Mn/1.67

def calculate(i:Dict[str,Any])->Dict[str,Any]:
    v=validate(i)
    if v["status"]!="ready": return {"status":"blocked","validation":v}
    web=str(i["web_classification"]).lower(); flange=str(i["flange_classification"]).lower()
    if web!="compact":
        return {"status":"blocked_chapter_f_route","required_route":"F4" if web=="noncompact" else "F5","message":"This release does not apply F2/F3 equations to a noncompact or slender web.","engineer_review_required":True}
    E,Fy,Sx,Zx,ry,rts,J,ho,Lb,Cb=map(float,[i["E_ksi"],i["Fy_ksi"],i["Sx_in3"],i["Zx_in3"],i["ry_in"],i["rts_in"],i["J_in4"],i["ho_in"],i["Lb_ft"],i["Cb"]])
    Lb*=12; Mp=Fy*Zx; Lp=1.76*ry*math.sqrt(E/Fy); term=J/(Sx*ho)
    Lr=1.95*rts*E/(0.7*Fy)*math.sqrt(term+math.sqrt(term**2+6.76*(0.7*Fy/E)**2))
    if Lb<=Lp: Mn_ltb=Mp; ltb="yielding region, Lb <= Lp"
    elif Lb<=Lr:
        Mn_ltb=min(Cb*(Mp-(Mp-0.7*Fy*Sx)*(Lb-Lp)/(Lr-Lp)),Mp); ltb="inelastic LTB"
    else:
        Fcr=(Cb*math.pi**2*E/(Lb/rts)**2)*math.sqrt(1+0.078*term*(Lb/rts)**2); Mn_ltb=min(Fcr*Sx,Mp); ltb="elastic LTB"
    candidates={"yielding":Mp,"lateral_torsional_buckling":Mn_ltb}
    route="F2"
    if flange!="compact":
        route="F3"; lam=float(i["flange_lambda"]); lp=float(i["flange_lambda_p"]); lr=float(i["flange_lambda_r"])
        if flange=="noncompact": Mn_flb=Mp-(Mp-0.7*Fy*Sx)*(lam-lp)/(lr-lp)
        else:
            h,tw=float(i["h_in"]),float(i["tw_in"]); kc=max(0.35,min(0.76,4.0/math.sqrt(h/tw))); Mn_flb=0.9*E*kc*Sx/(lam**2)
        candidates["compression_flange_local_buckling"]=Mn_flb
    governing=min(candidates,key=candidates.get); Mn=candidates[governing]/12.0; avail=available(Mn,str(i["design_method"]).upper()); demand=float(i["required_moment_kip_ft"]); dcr=demand/avail if avail else math.inf
    return {"status":"complete","chapter_f_route":route,"limit_state_nominal_strengths_kip_ft":{k:v/12 for k,v in candidates.items()},"ltb_region":ltb,"Lp_ft":Lp/12,"Lr_ft":Lr/12,"governing_limit_state":governing,"nominal_strength_Mn_kip_ft":Mn,"available_strength_kip_ft":avail,"required_strength_kip_ft":demand,"dcr":dcr,"passes":dcr<=1,"engineer_review_required":True}
