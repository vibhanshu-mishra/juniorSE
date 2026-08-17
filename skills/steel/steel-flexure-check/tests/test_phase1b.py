import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('flexcalc_phase1b', ROOT/'calculator.py')
calc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(calc)


def companion_f15():
    return {
        'design_method':'LRFD','section_symmetry':'doubly_symmetric',
        'E_ksi':29000,'Fy_ksi':50,'Sx_in3':2040,'Sxt_in3':2040,'Zx_in3':2270,
        'J_in4':77.3,'ho_in':64.0,'Lb_ft':12.5,'Cb':1.25,
        'bf_in':14.0,'tf_in':2.0,'h_in':62.0,'hc_in':62.0,'tw_in':0.5,
        'flange_classification':'compact','web_classification':'noncompact',
        'flange_lambda':3.5,'flange_lambda_p':9.15,'flange_lambda_r':24.1,
        'web_lambda':124.0,'web_lambda_p':90.6,'web_lambda_r':137.0,
        'required_moment_kip_ft':6910.0,
    }


def slender_web_base():
    return {
        'design_method':'LRFD','section_symmetry':'doubly_symmetric',
        'E_ksi':29000,'Fy_ksi':50,'Sx_in3':500,'Sxt_in3':500,'Zx_in3':560,
        'J_in4':20,'ho_in':40,'Lb_ft':8,'Cb':1.0,
        'bf_in':12,'tf_in':1.0,'h_in':50,'hc_in':50,'tw_in':0.30,
        'flange_classification':'compact','web_classification':'slender',
        'flange_lambda':6.0,'flange_lambda_p':9.15,'flange_lambda_r':24.1,
        'web_lambda':50/0.30,'web_lambda_p':90.6,'web_lambda_r':137.0,
        'required_moment_kip_ft':1000,
    }


def test_f4_matches_companion_example_f15_nominal_strength():
    r = calc.calculate(companion_f15())
    assert r['status'] == 'complete'
    assert r['chapter_f_route'] == 'F4'
    assert abs(r['Rpc'] - 1.03) < 0.01
    assert abs(r['Lp_ft']*12 - 98.3) < 1.0
    assert abs(r['Lr_ft']*12 - 369.0) < 4.0
    assert abs(r['nominal_strength_Mn_kip_ft'] - 8760.0) < 60.0
    assert r['governing_limit_state'] in {'compression_flange_yielding','lateral_torsional_buckling'}


def test_f5_slender_web_returns_rpg_and_four_limit_state_framework():
    r = calc.calculate(slender_web_base())
    assert r['status'] == 'complete'
    assert r['chapter_f_route'] == 'F5'
    assert 0 < r['Rpg'] <= 1.0
    assert 'compression_flange_yielding' in r['limit_state_nominal_strengths_kip_ft']
    assert 'lateral_torsional_buckling' in r['limit_state_nominal_strengths_kip_ft']
    assert r['f5_ltb_region'] in {'Lb <= Lp','Lp < Lb <= Lr','Lb > Lr'}


def test_f5_noncompact_flange_includes_local_buckling():
    x = slender_web_base()
    x.update({'flange_classification':'noncompact','flange_lambda':15.0})
    r = calc.calculate(x)
    assert r['chapter_f_route'] == 'F5'
    assert 'compression_flange_local_buckling' in r['limit_state_nominal_strengths_kip_ft']


def test_f5_slender_flange_includes_local_buckling():
    x = slender_web_base()
    x.update({'flange_classification':'slender','flange_lambda':30.0})
    r = calc.calculate(x)
    assert r['chapter_f_route'] == 'F5'
    assert 'compression_flange_local_buckling' in r['limit_state_nominal_strengths_kip_ft']
