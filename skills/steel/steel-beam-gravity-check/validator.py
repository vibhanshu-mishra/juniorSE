from __future__ import annotations
from typing import Any, Dict, List

SECTION_REQUIRED=["code_family","code_edition","design_method","bracing_condition","steel_grade","member_section","composite_status","E_ksi","Fy_ksi","Ix_in4","Sx_in3","Zx_in3","d_in","h_in","tw_in","bf_in","tf_in","ry_in","rts_in","J_in4","ho_in","Lb_ft","Cb"]
POS=["E_ksi","Fy_ksi","Ix_in4","Sx_in3","Zx_in3","d_in","h_in","tw_in","bf_in","tf_in","ry_in","rts_in","J_in4","ho_in","Lb_ft","Cb"]
LEGACY_REQUIRED=["span_ft","dead_load_plf","live_load_plf","load_level","support_condition"]

def missing(v): return v in (None,"",[])

def validate(i:Dict[str,Any])->Dict[str,Any]:
    envelope_mode=isinstance(i.get("analysis_result"),dict)
    required=list(SECTION_REQUIRED)+( [] if envelope_mode else LEGACY_REQUIRED )
    miss=[k for k in required if missing(i.get(k))]
    e:List[str]=[]; w:List[str]=[]
    method=str(i.get("design_method","")).upper()
    if method not in {"ASD","LRFD"}:e.append("design_method must be ASD or LRFD.")
    if str(i.get("code_family","")).upper()!="AISC":e.append("code_family must be AISC for this skill.")
    if i.get("code_edition") and "360-16" not in str(i["code_edition"]):e.append("This release is intentionally limited to AISC 360-16.")
    if str(i.get("composite_status","")).lower() not in {"noncomposite","non-composite","no","false"}:e.append("Current scope is noncomposite steel members only.")
    for k in POS:
        if k not in miss:
            try:
                if float(i[k])<=0:e.append(f"{k} must be positive.")
            except (TypeError,ValueError):e.append(f"{k} must be numeric.")
    if envelope_mode:
        ar=i.get("analysis_result") or {}; env=ar.get("demand_envelope")
        if ar.get("status")!="complete_general_beam_analysis":e.append("analysis_result must be a completed steel-beam-gravity-analysis result.")
        if not isinstance(env,dict):e.append("analysis_result must contain demand_envelope.")
        else:
            for k in ("max_positive_moment_kip_ft","min_negative_moment_kip_ft","max_abs_shear_kips"):
                if k not in env:e.append(f"analysis_result.demand_envelope missing {k}.")
        if ar.get("torsion_analysis"):
            w.append("Torsional demand is reported separately and is not included in Chapter F/G/J10 adequacy.")
        sar=i.get("service_analysis_result")
        if sar is not None and (not isinstance(sar,dict) or sar.get("status")!="complete_general_beam_analysis"):
            e.append("service_analysis_result must be a completed beam-analysis result when provided.")
        for case in i.get("web_local_cases",[]) or []:
            if str(case.get("source","")).lower() not in {"support_reaction","explicit_force"}:e.append("Each web_local_case source must be support_reaction or explicit_force.")
            for fld in ("bearing_length_N_in","distance_from_end_in","k_in"):
                try:
                    if float(case.get(fld))<0:e.append(f"web_local_case {fld} must be nonnegative.")
                except (TypeError,ValueError):e.append(f"web_local_case requires numeric {fld}.")
            if str(case.get("source","")).lower()=="support_reaction" and case.get("x_ft") is None:e.append("support_reaction web_local_case requires x_ft.")
            if str(case.get("source","")).lower()=="explicit_force" and case.get("force_kips") is None:e.append("explicit_force web_local_case requires force_kips.")
    else:
        w.append("Legacy uniform-load input mode is retained for compatibility; use analysis_result for Phase 2 generalized demand integration.")
    w.append("Connection and bearing-plate design are intentionally outside this skill.")
    return {"status":"ready" if not miss and not e else "blocked","missing_inputs":miss,"errors":e,"warnings":w,"mode":"analysis_result" if envelope_mode else "legacy","engineer_review_required":True}
