from __future__ import annotations
from typing import Any, Dict, List
REQUIRED=["code_family","code_edition","design_method","span_ft","dead_load_plf","live_load_plf","load_level","support_condition","bracing_condition","steel_grade","member_section","composite_status","E_ksi","Fy_ksi","Ix_in4","Sx_in3","Zx_in3","d_in","h_in","tw_in","bf_in","tf_in","ry_in","rts_in","J_in4","ho_in","Lb_ft","Cb"]
POS=["span_ft","E_ksi","Fy_ksi","Ix_in4","Sx_in3","Zx_in3","d_in","h_in","tw_in","bf_in","tf_in","ry_in","rts_in","J_in4","ho_in","Lb_ft","Cb"]
def missing(v): return v in (None,"",[])
def validate(i:Dict[str,Any])->Dict[str,Any]:
    miss=[k for k in REQUIRED if missing(i.get(k))];e:List[str]=[];w:List[str]=[]
    if str(i.get("design_method","")).upper() not in {"ASD","LRFD"}:e.append("design_method must be ASD or LRFD.")
    if str(i.get("code_family","")).upper()!="AISC":e.append("code_family must be AISC for this skill.")
    if i.get("code_edition") and "360-16" not in str(i["code_edition"]):e.append("This release is intentionally limited to AISC 360-16.")
    if str(i.get("load_level","")).lower() not in {"service","factored"}:e.append("load_level must be service or factored.")
    if i.get("support_condition") and str(i["support_condition"]).lower() not in {"simple","simply supported","simply_supported"}:e.append("Current analysis scope is simply supported uniform-load beams.")
    if i.get("point_loads"):e.append("Point-load analysis belongs to Phase 2 and is not implemented yet.")
    if str(i.get("composite_status","")).lower() not in {"noncomposite","non-composite","no","false"}:e.append("Current scope is noncomposite steel beams only.")
    for k in POS:
        if k not in miss:
            try:
                if float(i[k])<=0:e.append(f"{k} must be positive.")
            except:e.append(f"{k} must be numeric.")
    for k in ["dead_load_plf","live_load_plf"]:
        if k not in miss:
            try:
                if float(i[k])<0:e.append(f"{k} must be nonnegative.")
            except:e.append(f"{k} must be numeric.")
    local_fields=["concentrated_force_kips","bearing_length_N_in","distance_from_end_in","k_in"]
    if any(not missing(i.get(k)) for k in local_fields):
        lm=[k for k in local_fields if missing(i.get(k))]
        if lm:e.append("Web local checks require all of concentrated_force_kips, bearing_length_N_in, distance_from_end_in, and k_in when any are provided.")
    w.append("Connection and bearing-plate design are intentionally outside this skill.")
    return {"status":"ready" if not miss and not e else "blocked","missing_inputs":miss,"errors":e,"warnings":w,"engineer_review_required":True}
