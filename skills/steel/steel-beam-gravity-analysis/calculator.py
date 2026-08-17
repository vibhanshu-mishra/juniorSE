from __future__ import annotations
import importlib.util, math
from pathlib import Path
from typing import Any, Dict, List
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
        supports=[{'x_ft':float(s['x_ft']),'type':str(s['type']).lower(),'settlement_in':float(s.get('settlement_in',0.0) or 0.0)} for s in i['supports']]
    else:
        sc=str(i['support_condition']).lower()
        if sc in {'simple','simply_supported','simply supported'}: supports=[{'x_ft':0.0,'type':'pinned','settlement_in':0.0},{'x_ft':total,'type':'roller','settlement_in':0.0}]
        elif sc=='cantilever': supports=[{'x_ft':0.0,'type':'fixed','settlement_in':0.0}]
        elif sc in {'fixed_fixed','fixed-fixed'}: supports=[{'x_ft':0.0,'type':'fixed','settlement_in':0.0},{'x_ft':total,'type':'fixed','settlement_in':0.0}]
        elif sc in {'propped_cantilever','propped-cantilever'}: supports=[{'x_ft':0.0,'type':'fixed','settlement_in':0.0},{'x_ft':total,'type':'roller','settlement_in':0.0}]
        else: supports=[]
    return total,supports


def _category_loads(i,total,category):
    pts=[]; dist=[]; moments=[]
    base=float(i.get(f'{category}_load_plf',0.0) or 0.0)
    if base: dist.append({'w0':base,'w1':base,'a':0.0,'b':total})
    for p in i.get('point_loads',[]) or []:
        if str(p.get('category','')).lower()==category: pts.append({'P_lb':float(p['P_lb']),'x_ft':float(p['x_ft'])})
    for u in i.get('uniform_loads',[]) or []:
        if str(u.get('category','')).lower()==category: dist.append({'w0':float(u['w_plf']),'w1':float(u['w_plf']),'a':float(u['x_start_ft']),'b':float(u['x_end_ft'])})
    for u in i.get('linear_loads',[]) or []:
        if str(u.get('category','')).lower()==category: dist.append({'w0':float(u['w_start_plf']),'w1':float(u['w_end_plf']),'a':float(u['x_start_ft']),'b':float(u['x_end_ft'])})
    for m in i.get('concentrated_moments',[]) or []:
        if str(m.get('category','')).lower()==category: moments.append({'M_lb_in':float(m['M_lb_ft'])*12.0,'x_ft':float(m['x_ft'])})
    return pts,dist,moments


def _key_points(total,supports,pts,dist,moments,stiffness_segments=None,extra=None):
    key={0.0,total}; key.update(s['x_ft'] for s in supports); key.update(p['x_ft'] for p in pts); key.update(m['x_ft'] for m in moments)
    for u in dist: key.update([u['a'],u['b']])
    for s in stiffness_segments or []: key.update([float(s['x_start_ft']),float(s['x_end_ft'])])
    for x in extra or []: key.add(float(x))
    return sorted(key)


def _mesh(total,supports,pts,dist,moments,stiffness_segments=None,extra=None,subdivisions=12):
    base=_key_points(total,supports,pts,dist,moments,stiffness_segments,extra); xs=[]
    for a,b in zip(base[:-1],base[1:]):
        for j in range(max(1,subdivisions)): xs.append(a+(b-a)*j/max(1,subdivisions))
    xs.append(base[-1])
    return np.array(sorted(set(round(x,10) for x in xs)),dtype=float)*12.0


def _EI_at(i,x_ft):
    segs=i.get('stiffness_segments') or []
    if segs:
        for s in segs:
            if float(s['x_start_ft'])-1e-9 <= x_ft <= float(s['x_end_ft'])+1e-9:
                return float(s['E_ksi'])*1000.0,float(s['Ix_in4'])
        raise ValueError(f'No stiffness segment covers x={x_ft} ft')
    return float(i.get('E_ksi') or 1.0)*1000.0,float(i.get('Ix_in4') or 1.0)


def _q_plf(dist,x_ft):
    q=0.0
    for u in dist:
        if u['a']-1e-9 <= x_ft <= u['b']+1e-9:
            if abs(u['b']-u['a'])<1e-12: continue
            r=(x_ft-u['a'])/(u['b']-u['a'])
            q += u['w0']+(u['w1']-u['w0'])*r
    return q


def _consistent_load_linear(dist,x1_in,x2_in):
    L=x2_in-x1_in
    # 3-point Gauss exactly integrates cubic shape functions times linear q.
    gps=[(-math.sqrt(3/5),5/9),(0.0,8/9),(math.sqrt(3/5),5/9)]
    fe=np.zeros(4)
    for g,wgt in gps:
        t=(g+1)*L/2; xi=t/L; x_ft=(x1_in+t)/12.0
        N=np.array([1-3*xi**2+2*xi**3, L*(xi-2*xi**2+xi**3), 3*xi**2-2*xi**3, L*(-xi**2+xi**3)])
        q=-_q_plf(dist,x_ft)/12.0
        fe += N*q*wgt*L/2
    return fe


def _beam_k(E,I,L,shear=None):
    if shear and shear.get('enabled'):
        G=float(shear['G_ksi'])*1000.0; Av=float(shear['Av_in2']); phi=12*E*I/(G*Av*L**2)
        c=E*I/(L**3*(1+phi))
        return c*np.array([[12,6*L,-12,6*L],[6*L,(4+phi)*L**2,-6*L,(2-phi)*L**2],[-12,-6*L,12,-6*L],[6*L,(2-phi)*L**2,-6*L,(4+phi)*L**2]],float)
    return E*I/L**3*np.array([[12,6*L,-12,6*L],[6*L,4*L**2,-6*L,2*L**2],[-12,-6*L,12,-6*L],[6*L,2*L**2,-6*L,4*L**2]],float)


def _geom_k(Pcomp,L):
    if abs(Pcomp)<1e-12: return np.zeros((4,4))
    return Pcomp/(30*L)*np.array([[36,3*L,-36,3*L],[3*L,4*L**2,-3*L,-L**2],[-36,-3*L,36,-3*L],[3*L,-L**2,-3*L,4*L**2]],float)


def _solve_case(i,total,supports,pts,dist,moments):
    segs=i.get('stiffness_segments') or []
    xs=_mesh(total,supports,pts,dist,moments,segs); n=len(xs); nd=2*n
    K=np.zeros((nd,nd)); F=np.zeros(nd); elem=[]
    shear=i.get('shear_deformation') or {}; second=i.get('second_order') or {}; Pcomp=float(second.get('axial_force_lb',0.0) or 0.0) if second.get('enabled') else 0.0
    for e in range(n-1):
        x1,x2=xs[e],xs[e+1]; L=x2-x1; mid=(x1+x2)/24.0
        E,I=_EI_at(i,mid); kel=_beam_k(E,I,L,shear); k=kel-_geom_k(Pcomp,L)
        fe=_consistent_load_linear(dist,x1,x2); do=[2*e,2*e+1,2*(e+1),2*(e+1)+1]
        K[np.ix_(do,do)]+=k; F[do]+=fe; elem.append((do,kel,k,fe,L,x1))
    for p in pts:
        idx=int(np.argmin(abs(xs-p['x_ft']*12))); F[2*idx]+=-p['P_lb']
    for m in moments:
        idx=int(np.argmin(abs(xs-m['x_ft']*12))); F[2*idx+1]+=m['M_lb_in']
    restrained=[]; prescribed={}; sup_nodes=[]
    for s in supports:
        idx=int(np.argmin(abs(xs-s['x_ft']*12))); sup_nodes.append((s,idx)); restrained.append(2*idx); prescribed[2*idx]=float(s.get('settlement_in',0.0))
        if s['type']=='fixed': restrained.append(2*idx+1); prescribed[2*idx+1]=0.0
    restrained=sorted(set(restrained)); free=[j for j in range(nd) if j not in restrained]
    d=np.zeros(nd)
    for dof,val in prescribed.items(): d[dof]=val
    if free:
        Krf=K[np.ix_(free,restrained)] if restrained else np.zeros((len(free),0))
        rhs=F[free]-(Krf@d[restrained] if restrained else 0)
        try: d[free]=np.linalg.solve(K[np.ix_(free,free)],rhs)
        except np.linalg.LinAlgError as exc: raise ValueError('Beam stiffness matrix is singular or unstable for the requested analysis.') from exc
    R=K@d-F
    reactions=[{'x_ft':s['x_ft'],'type':s['type'],'vertical_lb':float(R[2*idx]),'moment_kip_ft':float(R[2*idx+1]/12000) if s['type']=='fixed' else 0.0,'settlement_in':float(s.get('settlement_in',0.0))} for s,idx in sup_nodes]
    moments_out=[]; shears=[]; defls=[]
    for do,kel,k,fe,L,x1 in elem:
        de=d[do]; ef=kel@de-fe; V0=float(ef[0]); M0=float(-ef[1]); q0=-_q_plf(dist,x1/12)/12; q1=-_q_plf(dist,(x1+L)/12)/12
        for t in np.linspace(0,L,9):
            xx=x1+t; dq=(q1-q0); V=V0+q0*t+dq*t*t/(2*L); M=M0+V0*t+q0*t*t/2+dq*t**3/(6*L)
            xi=t/L; N1=1-3*xi**2+2*xi**3; N2=L*(xi-2*xi**2+xi**3); N3=3*xi**2-2*xi**3; N4=L*(-xi**2+xi**3)
            vv=N1*de[0]+N2*de[1]+N3*de[2]+N4*de[3]
            moments_out.append((xx/12,M/12000)); shears.append((xx/12,V/1000)); defls.append((xx/12,vv))
    p_pair=max(moments_out,key=lambda z:z[1]) if moments_out else (0.0,0.0)
    n_pair=min(moments_out,key=lambda z:z[1]) if moments_out else (0.0,0.0)
    v_pair=max(shears,key=lambda z:abs(z[1])) if shears else (0.0,0.0)
    d_pair=max(defls,key=lambda z:abs(min(z[1],0.0))) if defls else (0.0,0.0)
    ad_pair=max(defls,key=lambda z:abs(z[1])) if defls else (0.0,0.0)
    return {'support_reactions':reactions,
            'max_positive_moment_kip_ft':float(p_pair[1]),'max_positive_moment_location_ft':float(p_pair[0]),
            'min_negative_moment_kip_ft':float(n_pair[1]),'min_negative_moment_location_ft':float(n_pair[0]),
            'max_abs_shear_kips':float(abs(v_pair[1])),'max_abs_shear_location_ft':float(v_pair[0]),'max_abs_shear_signed_kips':float(v_pair[1]),
            'max_downward_deflection_in':float(abs(min(d_pair[1],0.0))),'max_downward_deflection_location_ft':float(d_pair[0]),
            'max_abs_deflection_in':float(abs(ad_pair[1])),'max_abs_deflection_location_ft':float(ad_pair[0]),
            'stations':{'moment':moments_out,'shear':shears,'deflection':defls}}


def _moving_envelope(i,total,supports):
    patterns=i.get('moving_loads') or []
    if not patterns: return None
    best={'max_positive_moment_kip_ft':-1e99,'min_negative_moment_kip_ft':1e99,'max_abs_shear_kips':0.0,'max_downward_deflection_in':0.0,'governing_positions':{}}
    for pat in patterns:
        axles=pat['axles']; offs=[float(a['offset_ft']) for a in axles]; step=float(pat['step_ft']); lead=-max(offs); end=total-min(offs)
        nsteps=int(math.floor((end-lead)/step+1e-9))+1
        for k in range(nsteps+1):
            xlead=min(lead+k*step,end); pts=[]
            for a in axles:
                x=xlead+float(a['offset_ft'])
                if -1e-9 <= x <= total+1e-9: pts.append({'P_lb':float(a['P_lb']),'x_ft':max(0.0,min(total,x))})
            if not pts: continue
            case=_solve_case(i,total,supports,pts,[],[])
            if case['max_positive_moment_kip_ft']>best['max_positive_moment_kip_ft']:
                best['max_positive_moment_kip_ft']=case['max_positive_moment_kip_ft']; best['governing_positions']['max_positive_moment']={'pattern':pat.get('name','moving load'),'lead_x_ft':round(xlead,10),'demand_x_ft':case.get('max_positive_moment_location_ft')}
            if case['min_negative_moment_kip_ft']<best['min_negative_moment_kip_ft']:
                best['min_negative_moment_kip_ft']=case['min_negative_moment_kip_ft']; best['governing_positions']['min_negative_moment']={'pattern':pat.get('name','moving load'),'lead_x_ft':round(xlead,10),'demand_x_ft':case.get('min_negative_moment_location_ft')}
            if case['max_abs_shear_kips']>best['max_abs_shear_kips']:
                best['max_abs_shear_kips']=case['max_abs_shear_kips']; best['governing_positions']['max_abs_shear']={'pattern':pat.get('name','moving load'),'lead_x_ft':round(xlead,10),'demand_x_ft':case.get('max_abs_shear_location_ft')}
            if case['max_downward_deflection_in']>best['max_downward_deflection_in']:
                best['max_downward_deflection_in']=case['max_downward_deflection_in']; best['governing_positions']['max_downward_deflection']={'pattern':pat.get('name','moving load'),'lead_x_ft':round(xlead,10),'demand_x_ft':case.get('max_downward_deflection_location_ft')}
    if best['max_positive_moment_kip_ft']<-1e90: return None
    return best


def _torsion_analysis(i,total):
    t=i.get('torsion') or {}
    if not t.get('enabled'): return None
    dtor=t.get('distributed_torques',[]) or []
    key={0.0,total}; key.update(float(x) for x in t.get('restraints',[])); key.update(float(p['x_ft']) for p in t.get('point_torques',[]) or [])
    for s in t.get('segments',[]) or []: key.update([float(s['x_start_ft']),float(s['x_end_ft'])])
    for u in dtor: key.update([float(u['x_start_ft']),float(u['x_end_ft'])])
    xs=np.array(sorted(key))*12.0; n=len(xs); K=np.zeros((n,n)); F=np.zeros(n); elem=[]
    def GJ(mid_ft):
        for s in t.get('segments',[]) or []:
            if float(s['x_start_ft'])-1e-9<=mid_ft<=float(s['x_end_ft'])+1e-9: return float(s['G_ksi'])*1000*float(s['J_in4'])
        return float(t['G_ksi'])*1000*float(t['J_in4'])
    def tq(x_ft):
        q=0.0
        for u in dtor:
            a=float(u['x_start_ft']); b=float(u['x_end_ft'])
            if a-1e-9<=x_ft<=b+1e-9:
                r=(x_ft-a)/(b-a)
                q += (float(u['t_start_lb_in_per_ft'])+(float(u['t_end_lb_in_per_ft'])-float(u['t_start_lb_in_per_ft']))*r)/12.0
        return q
    for e in range(n-1):
        L=xs[e+1]-xs[e]; gj=GJ((xs[e]+xs[e+1])/24); k=gj/L*np.array([[1,-1],[-1,1]],float); K[e:e+2,e:e+2]+=k
        q0=tq(xs[e]/12); q1=tq(xs[e+1]/12); fe=np.array([L*(2*q0+q1)/6, L*(q0+2*q1)/6],float); F[e:e+2]+=fe; elem.append((e,L,gj,fe,q0,q1))
    for p in t.get('point_torques',[]) or []:
        idx=int(np.argmin(abs(xs-float(p['x_ft'])*12))); F[idx]+=float(p['T_lb_in'])
    restrained=sorted(set(int(np.argmin(abs(xs-float(x)*12))) for x in t.get('restraints',[]))); free=[j for j in range(n) if j not in restrained]; theta=np.zeros(n)
    if free:
        try: theta[free]=np.linalg.solve(K[np.ix_(free,free)],F[free])
        except np.linalg.LinAlgError as exc: raise ValueError('Torsional stiffness matrix is singular; add adequate torsional restraint.') from exc
    R=K@theta-F
    reactions=[{'x_ft':float(xs[j]/12),'torque_lb_in':float(R[j])} for j in restrained]
    torques=[]; maxT=0.0
    for e,L,gj,fe,q0,q1 in elem:
        ke=gj/L*np.array([[1,-1],[-1,1]],float); ef=ke@theta[e:e+2]-fe; T0=float(-ef[0])
        vals=[]
        for xx in np.linspace(0,L,9):
            T=T0-(q0*xx+(q1-q0)*xx*xx/(2*L)); vals.append(float(T)); maxT=max(maxT,abs(T))
        torques.append({'x_start_ft':float(xs[e]/12),'x_end_ft':float(xs[e+1]/12),'torque_lb_in_start':vals[0],'torque_lb_in_end':vals[-1]})
    return {'status':'complete_saint_venant_torsion','max_abs_rotation_rad':float(np.max(np.abs(theta))),'max_abs_torque_lb_in':float(maxT),'restraint_reactions':reactions,'segment_torques':torques,'assumptions':['Saint-Venant torsion only.','Warping torsion, warping normal stress, and bimoment are not included.']}

def _envelope(results,moving=None,torsion=None):
    named=list(results.items())
    pos_name,pos=max(named,key=lambda kv:kv[1]['max_positive_moment_kip_ft'])
    neg_name,neg=min(named,key=lambda kv:kv[1]['min_negative_moment_kip_ft'])
    shear_name,shear=max(named,key=lambda kv:kv[1]['max_abs_shear_kips'])
    defl_name,defl=max(named,key=lambda kv:kv[1]['max_downward_deflection_in'])
    env={
        'max_positive_moment_kip_ft':pos['max_positive_moment_kip_ft'],
        'max_positive_moment_location_ft':pos.get('max_positive_moment_location_ft'),
        'max_positive_moment_case':pos_name,
        'min_negative_moment_kip_ft':neg['min_negative_moment_kip_ft'],
        'min_negative_moment_location_ft':neg.get('min_negative_moment_location_ft'),
        'min_negative_moment_case':neg_name,
        'max_abs_shear_kips':shear['max_abs_shear_kips'],
        'max_abs_shear_location_ft':shear.get('max_abs_shear_location_ft'),
        'max_abs_shear_case':shear_name,
        'max_downward_deflection_in':defl['max_downward_deflection_in'],
        'max_downward_deflection_location_ft':defl.get('max_downward_deflection_location_ft'),
        'max_downward_deflection_case':defl_name,
    }
    if moving:
        if moving['max_positive_moment_kip_ft']>env['max_positive_moment_kip_ft']:
            env['max_positive_moment_kip_ft']=moving['max_positive_moment_kip_ft']; env['max_positive_moment_case']='moving_load'; env['max_positive_moment_location_ft']=moving.get('governing_positions',{}).get('max_positive_moment',{}).get('demand_x_ft')
        if moving['min_negative_moment_kip_ft']<env['min_negative_moment_kip_ft']:
            env['min_negative_moment_kip_ft']=moving['min_negative_moment_kip_ft']; env['min_negative_moment_case']='moving_load'; env['min_negative_moment_location_ft']=moving.get('governing_positions',{}).get('min_negative_moment',{}).get('demand_x_ft')
        if moving['max_abs_shear_kips']>env['max_abs_shear_kips']:
            env['max_abs_shear_kips']=moving['max_abs_shear_kips']; env['max_abs_shear_case']='moving_load'; env['max_abs_shear_location_ft']=moving.get('governing_positions',{}).get('max_abs_shear',{}).get('demand_x_ft')
        if moving['max_downward_deflection_in']>env['max_downward_deflection_in']:
            env['max_downward_deflection_in']=moving['max_downward_deflection_in']; env['max_downward_deflection_case']='moving_load'; env['max_downward_deflection_location_ft']=moving.get('governing_positions',{}).get('max_downward_deflection',{}).get('demand_x_ft')
    env['max_abs_moment_kip_ft']=max(abs(env['max_positive_moment_kip_ft']),abs(env['min_negative_moment_kip_ft']))
    if torsion:
        env['max_abs_torsional_rotation_rad']=torsion['max_abs_rotation_rad']
        env['max_abs_torque_lb_in']=torsion.get('max_abs_torque_lb_in',0.0)
    return env


def calculate(i:Dict[str,Any])->Dict[str,Any]:
    v=validate(i)
    if v['status']!='ready': return {'status':'blocked','validation':v}
    total,supports=_geometry(i)
    results={}
    for cat in ('dead','live'):
        p,d,m=_category_loads(i,total,cat); results[f'{cat}_load']=_solve_case(i,total,supports,p,d,m)
    pd,dd,md=_category_loads(i,total,'dead'); pl,dl,ml=_category_loads(i,total,'live'); results['dead_plus_live']=_solve_case(i,total,supports,pd+pl,dd+dl,md+ml)
    moving=_moving_envelope(i,total,supports); torsion=_torsion_analysis(i,total)
    Lin=total*12; live_delta=results['live_load']['max_downward_deflection_in']; total_delta=results['dead_plus_live']['max_downward_deflection_in']
    has_settlement=any(abs(float(s.get('settlement_in',0.0) or 0.0))>1e-12 for s in supports)
    if has_settlement:
        service={'status':'engineer_review_due_to_support_settlement','live_load_limit_in':Lin/240,'dead_plus_live_limit_in':Lin/360,'note':'Imposed support settlement is present; ordinary span deflection limits may need to be applied relative to the displaced support chord rather than absolute displacement.'}
    else:
        service={'status':'checked' if v['deflection_ready'] and str(i.get('load_level','')).lower()=='service' else 'not_checked','live_load_limit_in':Lin/240,'dead_plus_live_limit_in':Lin/360}
        if service['status']=='checked': service.update({'live_load_deflection_in':live_delta,'dead_plus_live_deflection_in':total_delta,'live_load_ratio_to_L_over_240':live_delta/(Lin/240),'dead_plus_live_ratio_to_L_over_360':total_delta/(Lin/360),'live_load_passes_L_over_240':live_delta<=Lin/240,'dead_plus_live_passes_L_over_360':total_delta<=Lin/360})
    env=_envelope(results,moving,torsion)
    method='Euler-Bernoulli beam stiffness method'
    if (i.get('shear_deformation') or {}).get('enabled'): method='Timoshenko beam stiffness method with effective shear area'
    if (i.get('second_order') or {}).get('enabled'): method += ' + elastic geometric stiffness (bounded second-order mode)'
    return {'status':'complete_general_beam_analysis','validation':v,'analysis_method':method,'analysis_results':results,'moving_load_envelope':moving,'torsion_analysis':torsion,'demand_envelope':env,'serviceability':service,'qaqc':['Explicit supports, settlements, stiffness segments, and load locations are validated.','Point, moment, uniform, triangular, and trapezoidal loads retain actual locations.','Moving-load effects are enveloped by direct stepping of axle patterns.','Second-order mode is not a substitute for the complete AISC 360-16 Direct Analysis Method.','Torsion is Saint-Venant only; warping torsion is excluded.','Serviceability remains LL L/240 and D+L L/360 per juniorSE project standard.'],'engineer_review_required':True}
