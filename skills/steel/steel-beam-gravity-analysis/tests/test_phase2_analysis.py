import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

spec = importlib.util.spec_from_file_location('phase2_calc', ROOT/'calculator.py')
calc = importlib.util.module_from_spec(spec); spec.loader.exec_module(calc)


def test_simple_center_point_load():
    r = calc.calculate({
        'span_ft':20,'support_condition':'simple','load_level':'service',
        'dead_load_plf':0,'live_load_plf':0,
        'point_loads':[{'P_lb':10000,'x_ft':10,'category':'live'}],
        'E_ksi':29000,'Ix_in4':1000,
    })
    case=r['analysis_results']['live_load']
    assert abs(case['support_reactions'][0]['vertical_lb']-5000)<1
    assert abs(case['support_reactions'][-1]['vertical_lb']-5000)<1
    assert abs(case['max_positive_moment_kip_ft']-50)<0.05
    assert abs(case['max_downward_deflection_in']-0.09931)<0.002


def test_cantilever_uniform_load():
    r=calc.calculate({
        'span_ft':10,'support_condition':'cantilever','load_level':'service',
        'dead_load_plf':1000,'live_load_plf':0,'E_ksi':29000,'Ix_in4':1000,
    })
    case=r['analysis_results']['dead_load']
    assert abs(case['support_reactions'][0]['vertical_lb']-10000)<1
    assert abs(abs(case['support_reactions'][0]['moment_kip_ft'])-50)<0.05
    assert abs(case['min_negative_moment_kip_ft']+50)<0.1


def test_two_span_continuous_uniform_load():
    r=calc.calculate({
        'spans_ft':[10,10],
        'supports':[{'x_ft':0,'type':'pinned'},{'x_ft':10,'type':'roller'},{'x_ft':20,'type':'roller'}],
        'load_level':'service','dead_load_plf':1000,'live_load_plf':0,
        'E_ksi':29000,'Ix_in4':1000,
    })
    case=r['analysis_results']['dead_load']
    reactions=[x['vertical_lb'] for x in case['support_reactions']]
    assert abs(reactions[0]-3750)<5
    assert abs(reactions[1]-12500)<10
    assert abs(reactions[2]-3750)<5
    assert abs(case['min_negative_moment_kip_ft']+12.5)<0.1


def test_partial_uniform_and_point_load_can_coexist():
    r=calc.calculate({
        'span_ft':20,'support_condition':'simple','load_level':'service',
        'dead_load_plf':0,'live_load_plf':0,'E_ksi':29000,'Ix_in4':1000,
        'uniform_loads':[{'w_plf':500,'x_start_ft':0,'x_end_ft':10,'category':'dead'}],
        'point_loads':[{'P_lb':4000,'x_ft':15,'category':'live'}],
    })
    assert r['status']=='complete_general_beam_analysis'
    assert r['analysis_results']['dead_plus_live']['max_positive_moment_kip_ft']>0

def test_unstable_support_model_blocks_instead_of_crashing():
    r=calc.calculate({
        'span_ft':20,
        'supports':[{'x_ft':0,'type':'roller'}],
        'load_level':'service','dead_load_plf':1000,'live_load_plf':0,
        'E_ksi':29000,'Ix_in4':1000,
    })
    assert r['status']=='blocked'
