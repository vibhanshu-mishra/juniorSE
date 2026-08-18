import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('h_calc', HERE/'calculator.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)


def _axial_result(force_type, req, avail):
    return {'status':'complete','force_type':force_type,'chapter':'D' if force_type=='tension' else 'E','required_strength_kip':req,'available_strength_kip':avail,'dcr':req/avail,'governing_limit_state':'benchmark','passes':req/avail<=1.0}

def _flex_result(req, avail):
    return {'status':'complete','required_strength_kip_ft':req,'available_strength_kip_ft':avail,'dcr':req/avail,'passes':req/avail<=1.0}


def test_h1_1a_compression_branch():
    r=mod.calculate({
      'design_method':'LRFD','analysis_basis':'second_order_or_chapter_c_compatible',
      'axial_strength_result':_axial_result('compression',60,200),
      'major_axis_flexure_result':_flex_result(40,100),
      'minor_axis_flexure_result':_flex_result(10,50),
    })
    expected=0.30 + (8/9)*(0.40+0.20)
    assert r['status']=='complete'
    assert r['chapter_h_route']=='H1'
    assert r['interaction_equation']=='H1-1a'
    assert abs(r['interaction_ratio']-expected)<1e-12


def test_h1_1b_low_axial_branch():
    r=mod.calculate({
      'design_method':'ASD','analysis_basis':'second_order_or_chapter_c_compatible',
      'axial_strength_result':_axial_result('compression',20,200),
      'major_axis_flexure_result':_flex_result(40,100),
      'minor_axis_flexure_result':_flex_result(5,50),
    })
    expected=0.10/2 + 0.40 + 0.10
    assert r['interaction_equation']=='H1-1b'
    assert abs(r['interaction_ratio']-expected)<1e-12


def test_h1_tension_uses_available_tensile_strength():
    r=mod.calculate({
      'design_method':'LRFD','analysis_basis':'second_order_or_chapter_c_compatible',
      'axial_strength_result':_axial_result('tension',40,100),
      'major_axis_flexure_result':_flex_result(15,100),
      'minor_axis_flexure_result':_flex_result(5,50),
    })
    expected=0.40+(8/9)*(0.15+0.10)
    assert r['force_type']=='tension'
    assert r['interaction_equation']=='H1-1a'
    assert abs(r['interaction_ratio']-expected)<1e-12


def test_h1_blocks_without_analysis_basis_acknowledgement():
    r=mod.calculate({
      'design_method':'LRFD',
      'axial_strength_result':_axial_result('compression',60,200),
      'major_axis_flexure_result':_flex_result(40,100),
      'minor_axis_flexure_result':_flex_result(10,50),
    })
    assert r['status']=='blocked'
    assert 'analysis_basis' in r['validation']['missing_inputs']

def test_h1_executes_child_skills_without_duplicate_capacities():
    r=mod.calculate({
      'design_method':'LRFD','analysis_basis':'second_order_or_chapter_c_compatible',
      'axial_inputs':{
        'sign_convention':'tension_positive','required_axial_kip':40,
        'member_inputs':{'design_method':'LRFD','Fy_ksi':50,'Fu_ksi':65,'Ag_in2':10,'Ae_in2':8}
      },
      'major_axis_flexure_inputs':{
        'design_method':'LRFD','section_symmetry':'doubly_symmetric','E_ksi':29000,'Fy_ksi':50,
        'Sx_in3':100,'Zx_in3':110,'J_in4':1.0,'ho_in':12,'Lb_ft':5,'Cb':1.0,
        'flange_classification':'compact','web_classification':'compact','flange_lambda':6,
        'flange_lambda_p':9,'flange_lambda_r':24,'h_in':10,'tw_in':0.5,'ry_in':2.0,'rts_in':2.5,
        'required_moment_kip_ft':50
      },
      'minor_axis_flexure_inputs':{
        'design_method':'LRFD','E_ksi':29000,'Fy_ksi':50,'Sy_in3':20,'Zy_in3':30,
        'bf_in':8,'tf_in':0.75,'required_moment_kip_ft':10
      }
    })
    assert r['status']=='complete'
    assert r['mode']=='nested_skill_execution'
    assert r['strength_results']['axial']['chapter']=='D'
    assert r['strength_results']['major_axis_flexure']['chapter_f_route']=='F2'
    assert r['strength_results']['minor_axis_flexure']['chapter_f_route']=='F6'
