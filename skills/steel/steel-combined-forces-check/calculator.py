from __future__ import annotations
import importlib.util
from pathlib import Path
from typing import Any, Dict
HERE=Path(__file__).resolve().parent; STEEL=HERE.parent

def _load(path:Path,key:str):
    spec=importlib.util.spec_from_file_location(key,path); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
VAL=_load(HERE/'validator.py','juniorse_h_validator')
AXIAL=_load(STEEL/'steel-axial-strength'/'calculator.py','juniorse_h_axial')
MAJOR=_load(STEEL/'steel-flexure-check'/'calculator.py','juniorse_h_major')
MINOR=_load(STEEL/'steel-minor-axis-flexure-check'/'calculator.py','juniorse_h_minor')

def _resolve(i:Dict[str,Any]):
    if all(i.get(k) is not None for k in ['axial_strength_result','major_axis_flexure_result','minor_axis_flexure_result']):
        return i['axial_strength_result'],i['major_axis_flexure_result'],i['minor_axis_flexure_result'],{'mode':'precomputed_results'}
    a=AXIAL.calculate(i['axial_inputs']); x=MAJOR.calculate(i['major_axis_flexure_inputs']); y=MINOR.calculate(i['minor_axis_flexure_inputs'])
    if a.get('status')!='complete' or x.get('status')!='complete' or y.get('status')!='complete':
        return None,None,None,{'mode':'nested_skill_execution','child_results':{'axial':a,'major_axis':x,'minor_axis':y}}
    return a['axial_strength_result'],x,y,{'mode':'nested_skill_execution','child_results':{'axial':a,'major_axis':x,'minor_axis':y}}

def calculate(i:Dict[str,Any])->Dict[str,Any]:
    v=VAL.validate(i)
    if v['status']!='ready': return {'status':'blocked','validation':v,'engineer_review_required':True}
    a,x,y,meta=_resolve(i)
    if a is None: return {'status':'blocked','validation':{'status':'blocked','missing_inputs':[],'errors':['One or more child strength skills blocked.']},**meta,'engineer_review_required':True}
    for name,r in [('axial',a),('major_axis_flexure',x),('minor_axis_flexure',y)]:
        if r.get('status') not in (None,'complete') and name!='axial': return {'status':'blocked','validation':{'status':'blocked','missing_inputs':[],'errors':[f'{name} result is not complete.']},'engineer_review_required':True}
    pr=float(a.get('required_strength_kip',0.0)); pc=a.get('available_strength_kip')
    if pc in (None,0):
        axial_ratio=0.0 if pr==0 else float('inf')
    else: axial_ratio=abs(pr)/float(pc)
    mx_ratio=float(x.get('required_strength_kip_ft',0.0))/float(x['available_strength_kip_ft']) if float(x.get('required_strength_kip_ft',0.0)) else 0.0
    my_ratio=float(y.get('required_strength_kip_ft',0.0))/float(y['available_strength_kip_ft']) if float(y.get('required_strength_kip_ft',0.0)) else 0.0
    if axial_ratio>=0.2:
        eq='H1-1a'; interaction=axial_ratio+(8.0/9.0)*(mx_ratio+my_ratio)
    else:
        eq='H1-1b'; interaction=axial_ratio/2.0+mx_ratio+my_ratio
    return {'status':'complete','code_basis':'AISC 360-16 Chapter H1','chapter_h_route':'H1','interaction_equation':eq,'force_type':a.get('force_type','none'),'ratios':{'Pr_over_Pc':axial_ratio,'Mrx_over_Mcx':mx_ratio,'Mry_over_Mcy':my_ratio},'interaction_ratio':interaction,'passes':interaction<=1.0,'strength_results':{'axial':a,'major_axis_flexure':x,'minor_axis_flexure':y},'analysis_basis':i['analysis_basis'],'chapter_c_note':'This skill evaluates member interaction only. It does not independently certify global Chapter C stability-analysis compliance.',**meta,'engineer_review_required':True}
