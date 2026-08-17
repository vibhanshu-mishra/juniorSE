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

def _avail(Rn:float,method:str,phi:float,omega:float)->float:return phi*Rn if method=="LRFD" else Rn/omega

def calculate(i:Dict[str,Any])->Dict[str,Any]:
 v=validate(i)
 if v["status"]!="ready":return {"status":"blocked","validation":v}
 method=str(i["design_method"]).upper();E,Fy,d,tw,tf,k,N,P,x=map(float,[i["E_ksi"],i["Fy_ksi"],i["d_in"],i["tw_in"],i["tf_in"],i["k_in"],i["bearing_length_N_in"],i["concentrated_force_kips"],i["distance_from_end_in"]])
 # J10.2 web local yielding: interior if force is farther than d from member end.
 if x>d: Rn_y=(5*k+N)*Fy*tw; ycase="interior (> d from end)"
 else: Rn_y=(2.5*k+N)*Fy*tw; ycase="end (<= d from end)"
 Ry=_avail(Rn_y,method,1.0,1.5);dy=P/Ry if Ry else math.inf
 # J10.3 web local crippling. Interior if farther than d/2 from end.
 ratio=(tw/tf)**1.5;root=math.sqrt(E*Fy*tf/tw)
 if x>d/2:
  Rn_c=0.80*tw**2*(1+3*(N/d)*ratio)*root;c_case="interior (> d/2 from end)"
 else:
  if N/d<=0.2: bracket=1+3*(N/d)*ratio
  else: bracket=1+(4*N/d-0.2)*ratio
  Rn_c=0.40*tw**2*bracket*root;c_case="end (<= d/2 from end)"
 Rc=_avail(Rn_c,method,0.75,2.0);dc=P/Rc if Rc else math.inf
 governing="web_local_yielding" if dy>=dc else "web_local_crippling"
 return {"status":"complete","basis":"AISC 360-16 J10.2 web local yielding and J10.3 web local crippling.","web_local_yielding":{"case":ycase,"nominal_strength_Rn_kips":Rn_y,"available_strength_kips":Ry,"required_force_kips":P,"dcr":dy,"passes":dy<=1},"web_local_crippling":{"case":c_case,"nominal_strength_Rn_kips":Rn_c,"available_strength_kips":Rc,"required_force_kips":P,"dcr":dc,"passes":dc<=1},"governing_limit_state":governing,"passes":max(dy,dc)<=1,"engineer_review_required":True}
