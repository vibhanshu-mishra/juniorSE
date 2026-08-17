from typing import Any,Dict
REQ=["design_method","E_ksi","Fy_ksi","d_in","tw_in","tf_in","k_in","bearing_length_N_in","concentrated_force_kips","distance_from_end_in"]
def validate(i:Dict[str,Any])->Dict[str,Any]:
 m=[k for k in REQ if i.get(k) in (None,"")];e=[]
 if str(i.get("design_method","")).upper() not in {"ASD","LRFD"}:e.append("design_method must be ASD or LRFD.")
 for k in ["E_ksi","Fy_ksi","d_in","tw_in","tf_in","k_in","bearing_length_N_in"]:
  if k not in m:
   try:
    if float(i[k])<=0:e.append(f"{k} must be positive.")
   except:e.append(f"{k} must be numeric.")
 for k in ["concentrated_force_kips","distance_from_end_in"]:
  if k not in m:
   try:
    if float(i[k])<0:e.append(f"{k} must be nonnegative.")
   except:e.append(f"{k} must be numeric.")
 return {"status":"ready" if not m and not e else "blocked","missing_inputs":m,"errors":e,"engineer_review_required":True}
