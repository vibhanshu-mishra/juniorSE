from __future__ import annotations
from typing import Any, Dict
REQ=["design_method","E_ksi","Fy_ksi","Sx_in3","Zx_in3","ry_in","rts_in","J_in4","ho_in","Lb_ft","Cb","flange_classification","web_classification","flange_lambda","flange_lambda_p","flange_lambda_r","h_in","tw_in","required_moment_kip_ft"]
NUM=["E_ksi","Fy_ksi","Sx_in3","Zx_in3","ry_in","rts_in","J_in4","ho_in","Lb_ft","Cb","flange_lambda","flange_lambda_p","flange_lambda_r","h_in","tw_in"]
def pos(v):
    try:return float(v)>0
    except:return False
def validate(i:Dict[str,Any])->Dict[str,Any]:
    miss=[k for k in REQ if i.get(k) in (None,"")]; err=[]
    if str(i.get("design_method","")).upper() not in {"ASD","LRFD"}: err.append("design_method must be ASD or LRFD.")
    for k in NUM:
        if k not in miss and not pos(i.get(k)): err.append(f"{k} must be positive.")
    if str(i.get("flange_classification","")).lower() not in {"compact","noncompact","slender"}: err.append("Invalid flange classification.")
    if str(i.get("web_classification","")).lower() not in {"compact","noncompact","slender"}: err.append("Invalid web classification.")
    try:
        if float(i.get("required_moment_kip_ft",0))<0: err.append("required_moment_kip_ft must be nonnegative.")
    except: err.append("required_moment_kip_ft must be numeric.")
    return {"status":"ready" if not miss and not err else "blocked","missing_inputs":miss,"errors":err,"engineer_review_required":True}
