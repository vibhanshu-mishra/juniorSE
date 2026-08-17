from typing import Any,Dict
REQ=["design_method","E_ksi","Fy_ksi","h_in","tw_in","required_shear_kips"]
def validate(i:Dict[str,Any])->Dict[str,Any]:
 m=[k for k in REQ if i.get(k) in (None,"")];e=[]
 if str(i.get("design_method","")).upper() not in {"ASD","LRFD"}:e.append("design_method must be ASD or LRFD.")
 for k in ["E_ksi","Fy_ksi","h_in","tw_in"]:
  if k not in m:
   try:
    if float(i[k])<=0:e.append(f"{k} must be positive.")
   except:e.append(f"{k} must be numeric.")
 try:
  if float(i.get("required_shear_kips",0))<0:e.append("required_shear_kips must be nonnegative.")
 except:e.append("required_shear_kips must be numeric.")
 return {"status":"ready" if not m and not e else "blocked","missing_inputs":m,"errors":e,"engineer_review_required":True}
