import math
from typing import Any,Dict
import importlib.util
from pathlib import Path

def _load_local_validator():
    p = Path(__file__).with_name("validator.py")
    spec = importlib.util.spec_from_file_location(f"juniorse_{p.parent.name}_validator", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.validate

validate = _load_local_validator()
def calculate(i:Dict[str,Any])->Dict[str,Any]:
 v=validate(i)
 if v["status"]!="ready":return {"status":"blocked","validation":v}
 E,Fy,h,tw=map(float,[i["E_ksi"],i["Fy_ksi"],i["h_in"],i["tw_in"]]);lam=h/tw;kv=5.34
 a=1.10*math.sqrt(kv*E/Fy);b=1.37*math.sqrt(kv*E/Fy)
 if lam<=a:Cv=1.0;region="Cv1 = 1.0"
 elif lam<=b:Cv=1.10*math.sqrt(kv*E/Fy)/lam;region="inelastic web shear buckling"
 else:Cv=1.51*kv*E/(Fy*lam**2);region="elastic web shear buckling"
 Aw=h*tw;Vn=0.6*Fy*Aw*Cv;method=str(i["design_method"]).upper();avail=Vn if method=="LRFD" else Vn/1.5;req=float(i["required_shear_kips"]);dcr=req/avail if avail else math.inf
 return {"status":"complete","basis":"AISC 360-16 Chapter G unstiffened web, kv=5.34.","h_over_tw":lam,"kv":kv,"Cv1":Cv,"shear_buckling_region":region,"Aw_in2":Aw,"nominal_strength_Vn_kips":Vn,"available_strength_kips":avail,"required_strength_kips":req,"dcr":dcr,"passes":dcr<=1,"engineer_review_required":True}
