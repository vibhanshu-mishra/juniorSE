from __future__ import annotations
import importlib.util, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STEEL = HERE.parents[1]

def load_calc(skill):
    p = STEEL / skill / 'calculator.py'
    spec = importlib.util.spec_from_file_location(f'test_{skill}', p)
    mod = importlib.util.module_from_spec(spec)
    old=list(sys.path); sys.path.insert(0,str(p.parent))
    try: spec.loader.exec_module(mod)
    finally: sys.path[:]=old
    return mod

AN = load_calc('steel-beam-gravity-analysis')
CHECK = load_calc('steel-beam-gravity-check')

SECTION = {
    'code_family':'AISC','code_edition':'AISC 360-16','design_method':'LRFD',
    'bracing_condition':'Lb provided','steel_grade':'A992','member_section':'test W/I shape',
    'composite_status':'noncomposite','E_ksi':29000,'Fy_ksi':50,'Ix_in4':1000,
    'Sx_in3':80,'Zx_in3':90,'d_in':12,'h_in':10.8,'tw_in':0.40,'bf_in':6.5,'tf_in':0.40,
    'ry_in':2.0,'rts_in':2.3,'J_in4':0.45,'ho_in':11.0,'Lb_ft':5.0,'Cb':1.0,
}

def analyze(payload):
    result = AN.calculate(payload)
    assert result['status'] == 'complete_general_beam_analysis'
    return result

def run_check(analysis, **extra):
    inp = dict(SECTION)
    inp['analysis_result'] = analysis
    inp.update(extra)
    return CHECK.calculate(inp)

def test_simple_udl_envelope_drives_flexure_and_shear():
    a = analyze({'span_ft':20,'support_condition':'simple','dead_load_plf':1000,'live_load_plf':2000,'load_level':'service','E_ksi':29000,'Ix_in4':1000})
    r = run_check(a)
    assert r['status'] == 'complete_envelope_strength_check'
    assert r['demand_source'] == 'analysis_result.demand_envelope'
    assert r['strength_checks']['chapter_f_flexure']['positive']['required_strength_kip_ft'] > 0
    assert r['strength_checks']['chapter_g_shear']['required_strength_kips'] > 0


def test_center_point_load_routes_actual_envelope_not_uniform_recalculation():
    a = analyze({'span_ft':20,'support_condition':'simple','point_loads':[{'P_lb':10000,'x_ft':10,'category':'dead'}],'load_level':'factored','E_ksi':29000,'Ix_in4':1000})
    assert abs(a['demand_envelope']['max_positive_moment_kip_ft'] - 50.0) < 0.2
    r = run_check(a)
    assert abs(r['strength_checks']['chapter_f_flexure']['positive']['required_strength_kip_ft'] - 50.0) < 0.2


def test_continuous_beam_preserves_positive_and_negative_flexure_checks():
    a = analyze({'spans_ft':[10,10],'supports':[{'x_ft':0,'type':'pinned'},{'x_ft':10,'type':'roller'},{'x_ft':20,'type':'roller'}],
                 'dead_load_plf':1000,'load_level':'factored','E_ksi':29000,'Ix_in4':1000})
    r = run_check(a)
    flex = r['strength_checks']['chapter_f_flexure']
    assert flex['positive']['required_strength_kip_ft'] > 0
    assert flex['negative']['required_strength_kip_ft'] > 0
    assert flex['negative']['demand_sign'] == 'negative'


def test_moving_load_envelope_can_govern_strength():
    a = analyze({'span_ft':20,'support_condition':'simple','load_level':'factored','E_ksi':29000,'Ix_in4':1000,
                 'moving_loads':[{'name':'single axle','category':'dead','step_ft':1.0,'axles':[{'P_lb':20000,'offset_ft':0}]}]})
    r = run_check(a)
    assert r['analysis_metadata']['moving_load_envelope_used'] is True
    assert r['strength_checks']['chapter_f_flexure']['positive']['required_strength_kip_ft'] >= 99.0


def test_j10_support_reaction_case_uses_analysis_reaction():
    a = analyze({'span_ft':20,'support_condition':'simple','dead_load_plf':1000,'load_level':'factored','E_ksi':29000,'Ix_in4':1000})
    r = run_check(a, web_local_cases=[{
        'name':'left support','source':'support_reaction','x_ft':0.0,
        'bearing_length_N_in':6.0,'distance_from_end_in':0.0,'k_in':1.0
    }])
    case = r['strength_checks']['chapter_j10_web_local']['cases'][0]
    assert abs(case['resolved_force_kips'] - 10.0) < 0.2
    assert case['source'] == 'support_reaction'
    assert case['result']['status'] == 'complete'
