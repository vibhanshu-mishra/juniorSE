from __future__ import annotations
import importlib.util, math
from pathlib import Path
from typing import Any, Dict, List, Tuple
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('juniorse_beam_analysis_validator',HERE/'validator.py')
_validator=importlib.util.module_from_spec(spec); spec.loader.exec_module(_validator)
validate=_validator.validate


def _geometry(i:Dict[str,Any]):
    if i.get('spans_ft'):
        xs=[0.0]
        for s in i['spans_ft']: xs.append(xs[-1]+float(s))
        total=xs[-1]
    else:
        total=float(i['span_ft']); xs=[0.0,total]
    if i.get('supports'):
        supports=[{'x_ft':float(s['x_ft']),'type':str(s['type']).lower()} for s in i['supports']]
    else:
        sc=str(i['support_condition']).lower()
        if sc in {'simple','simply_supported','simply supported'}: supports=[{'x_ft':0.0,'type':'pinned'},{'x_ft':total,'type':'roller'}]
        elif sc=='cantilever': supports=[{'x_ft':0.0,'type':'fixed'}]
        elif sc in {'fixed_fixed','fixed-fixed'}: supports=[{'x_ft':0.0,'type':'fixed'},{'x_ft':total,'type':'fixed'}]
        elif sc in {'propped_cantilever','propped-cantilever'}: supports=[{'x_ft':0.0,'type':'fixed'},{'x_ft':total,'type':'roller'}]
        else: supports=[]
    return total,supports


def _loads(i:Dict[str,Any], total:float, category:str):
    pts=[]; uds=[]
    base=float(i.get(f'{category}_load_plf',0.0) or 0.0)
    if base: uds.append({'w_plf':base,'x_start_ft':0.0,'x_end_ft':total})
    for p in i.get('point_loads',[]) or []:
        if str(p.get('category','')).lower()==category: pts.append({'P_lb':float(p['P_lb']),'x_ft':float(p['x_ft'])})
    for u in i.get('uniform_loads',[]) or []:
        if str(u.get('category','')).lower()==category: uds.append({'w_plf':float(u['w_plf']),'x_start_ft':float(u['x_start_ft']),'x_end_ft':float(u['x_end_ft'])})
    return pts,uds


def _mesh(total_ft:float,supports,pts,uds, subdivisions=12):
    key={0.0,total_ft}
    key.update(s['x_ft'] for s in supports); key.update(p['x_ft'] for p in pts)
    for u in uds: key.update([u['x_start_ft'],u['x_end_ft']])
    base=sorted(key); xs=[]
    for a,b in zip(base[:-1],base[1:]):
        n=max(1,subdivisions)
        for j in range(n): xs.append(a+(b-a)*j/n)
    xs.append(base[-1])
    return np.array(sorted(set(round(x,10) for x in xs)),dtype=float)*12.0


def _solve_case(total_ft:float,supports,pts,uds,Eksi:float|None,Iin4:float|None)->Dict[str,Any]:
    E=(Eksi or 1.0)*1000.0; I=Iin4 or 1.0
    xs=_mesh(total_ft,supports,pts,uds); n=len(xs); nd=2*n
    K=np.zeros((nd,nd)); F=np.zeros(nd); elem=[]
    for e in range(n-1):
        x1,x2=xs[e],xs[e+1]; L=x2-x1
        k=E*I/L**3*np.array([[12,6*L,-12,6*L],[6*L,4*L**2,-6*L,2*L**2],[-12,-6*L,12,-6*L],[6*L,2*L**2,-6*L,4*L**2]],float)
        mid_ft=((x1+x2)/2)/12
        w=sum(u['w_plf'] for u in uds if u['x_start_ft']-1e-9 <= mid_ft <= u['x_end_ft']+1e-9)
        q=-w/12.0
        fe=np.array([q*L/2,q*L**2/12,q*L/2,-q*L**2/12],float)
        do=[2*e,2*e+1,2*(e+1),2*(e+1)+1]
        K[np.ix_(do,do)]+=k; F[do]+=fe; elem.append((do,k,fe,q,L,x1))
    for p in pts:
        idx=int(np.argmin(abs(xs-p['x_ft']*12))); F[2*idx]+=-p['P_lb']
    restrained=[]; sup_nodes=[]
    for s in supports:
        idx=int(np.argmin(abs(xs-s['x_ft']*12))); sup_nodes.append((s,idx)); restrained.append(2*idx)
        if s['type']=='fixed': restrained.append(2*idx+1)
    restrained=sorted(set(restrained)); free=[j for j in range(nd) if j not in restrained]
    d=np.zeros(nd)
    if free:
        d[free]=np.linalg.solve(K[np.ix_(free,free)],F[free])
    R=K@d-F
    reactions=[]
    for s,idx in sup_nodes:
        reactions.append({'x_ft':s['x_ft'],'type':s['type'],'vertical_lb':float(R[2*idx]),'moment_kip_ft':float(R[2*idx+1]/12000) if s['type']=='fixed' else 0.0})
    moments=[]; shears=[]; defls=[]
    for do,k,fe,q,L,x1 in elem:
        de=d[do]; ef=k@de-fe; V0=float(ef[0]); M0=float(-ef[1])
        for t in np.linspace(0,L,9):
            xx=x1+t; V=V0+q*t; M=M0+V0*t+q*t*t/2
            xi=t/L
            N1=1-3*xi**2+2*xi**3; N2=L*(xi-2*xi**2+xi**3); N3=3*xi**2-2*xi**3; N4=L*(-xi**2+xi**3)
            vv=N1*de[0]+N2*de[1]+N3*de[2]+N4*de[3]
            moments.append((xx/12,M/12000)); shears.append((xx/12,V/1000)); defls.append((xx/12,vv))
    maxp=max((m for _,m in moments),default=0); minn=min((m for _,m in moments),default=0)
    maxv=max((abs(v) for _,v in shears),default=0); mindef=min((v for _,v in defls),default=0)
    return {'support_reactions':reactions,'max_positive_moment_kip_ft':float(maxp),'min_negative_moment_kip_ft':float(minn),'max_abs_shear_kips':float(maxv),'max_downward_deflection_in':float(abs(mindef)) if Eksi and Iin4 else None,'stations':{'moment':moments,'shear':shears,'deflection':defls if Eksi and Iin4 else []}}


def _combine(case_a,case_b):
    # Direct re-analysis is preferred; this helper is unused but retained for clarity.
    return None


def calculate(i:Dict[str,Any])->Dict[str,Any]:
    v=validate(i)
    if v['status']!='ready': return {'status':'blocked','validation':v}
    total,supports=_geometry(i); E=float(i['E_ksi']) if i.get('E_ksi') not in (None,'') else None; I=float(i['Ix_in4']) if i.get('Ix_in4') not in (None,'') else None
    results={}
    for cat in ('dead','live'):
        p,u=_loads(i,total,cat); results[f'{cat}_load']=_solve_case(total,supports,p,u,E,I)
    pd,ud=_loads(i,total,'dead'); pl,ul=_loads(i,total,'live')
    results['dead_plus_live']=_solve_case(total,supports,pd+pl,ud+ul,E,I)
    Lin=total*12
    live_delta=results['live_load']['max_downward_deflection_in']; total_delta=results['dead_plus_live']['max_downward_deflection_in']
    service={'status':'checked' if E and I else 'incomplete_without_E_ksi_and_Ix_in4','live_load_limit_in':Lin/240,'dead_plus_live_limit_in':Lin/360}
    if E and I:
        service.update({'live_load_deflection_in':live_delta,'dead_plus_live_deflection_in':total_delta,'live_load_ratio_to_L_over_240':live_delta/(Lin/240),'dead_plus_live_ratio_to_L_over_360':total_delta/(Lin/360),'live_load_passes_L_over_240':live_delta<=Lin/240,'dead_plus_live_passes_L_over_360':total_delta<=Lin/360})
    return {'status':'complete_general_beam_analysis','validation':v,'analysis_method':'Euler-Bernoulli beam stiffness method with direct point/piecewise-uniform loading','manual_alignment':{'AISC_15th_Table_3_22a':'Concentrated loads are analyzed directly; equivalent-uniform-load approximation is not required.','AISC_15th_Table_3_22b':'Cantilever support/load behavior supported directly.','AISC_15th_Table_3_22c':'Continuous multi-span support/load behavior supported directly.','AISC_15th_Table_3_23':'Reactions, shears, moments, and deflections are produced directly and used as benchmark categories.'},'analysis_results':results,'serviceability':service,'qaqc':['Explicit supports and load locations validated.','Point loads and partial uniform loads are not smeared into full-span uniform loads.','Continuous/fixed-end analysis requires member stiffness.','Serviceability remains LL L/240 and D+L L/360 per juniorSE project standard.'],'engineer_review_required':True}
