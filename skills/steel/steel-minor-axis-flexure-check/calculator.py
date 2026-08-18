from __future__ import annotations
import importlib.util, math
from pathlib import Path
from typing import Any, Dict
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('juniorse_minor_flex_validator',HERE/'validator.py'); vmod=importlib.util.module_from_spec(spec); spec.loader.exec_module(vmod)

def calculate(i:Dict[str,Any])->Dict[str,Any]:
    v=vmod.validate(i)
    if v['status']!='ready': return {'status':'blocked','validation':v,'engineer_review_required':True}
    method=str(i['design_method']).upper(); E=float(i['E_ksi']); Fy=float(i['Fy_ksi']); Sy=float(i['Sy_in3']); Zy=float(i['Zy_in3']); bf=float(i['bf_in']); tf=float(i['tf_in']); demand=float(i['required_moment_kip_ft'])
    lam=bf/(2*tf); lp=0.38*math.sqrt(E/Fy); lr=1.0*math.sqrt(E/Fy)
    Mp=min(Fy*Zy,1.6*Fy*Sy)
    candidates={'yielding':Mp}
    if lam<=lp: cls='compact'
    elif lam<=lr:
        cls='noncompact'; candidates['flange_local_buckling']=Mp-(Mp-0.7*Fy*Sy)*(lam-lp)/(lr-lp)
    else:
        cls='slender'; candidates['flange_local_buckling']=0.69*E*Sy/(lam**2)
    gov=min(candidates,key=candidates.get); Mn_in=candidates[gov]; Mn_ft=Mn_in/12.0; avail=0.90*Mn_ft if method=='LRFD' else Mn_ft/1.67; dcr=demand/avail if avail else math.inf
    return {'status':'complete','code_basis':'AISC 360-16 Chapter F6','chapter_f_route':'F6','flange_classification':cls,'flange_lambda':lam,'flange_lambda_p':lp,'flange_lambda_r':lr,'limit_state_nominal_strengths_kip_ft':{k:v/12 for k,v in candidates.items()},'governing_limit_state':gov,'nominal_strength_Mn_kip_ft':Mn_ft,'available_strength_kip_ft':avail,'required_strength_kip_ft':demand,'dcr':dcr,'passes':dcr<=1.0,'engineer_review_required':True}
