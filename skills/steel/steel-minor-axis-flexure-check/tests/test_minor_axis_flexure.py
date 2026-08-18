import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('minor_calc', HERE/'calculator.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)


def test_f6_compact_flange_lrfd_yielding():
    r=mod.calculate({
        'design_method':'LRFD','E_ksi':29000,'Fy_ksi':50,
        'Sy_in3':15.0,'Zy_in3':20.0,'bf_in':8.0,'tf_in':0.75,
        'required_moment_kip_ft':30.0
    })
    assert r['status']=='complete'
    assert r['chapter_f_route']=='F6'
    assert r['flange_classification']=='compact'
    assert abs(r['nominal_strength_Mn_kip_ft'] - 83.3333333333) < 1e-6
    assert abs(r['available_strength_kip_ft'] - 75.0) < 1e-6
    assert abs(r['dcr'] - 0.4) < 1e-9


def test_f6_noncompact_flange_reduces_strength():
    r=mod.calculate({
        'design_method':'LRFD','E_ksi':29000,'Fy_ksi':50,
        'Sy_in3':15.0,'Zy_in3':20.0,'bf_in':14.0,'tf_in':0.5,
        'required_moment_kip_ft':30.0
    })
    assert r['status']=='complete'
    assert r['flange_classification']=='noncompact'
    assert r['nominal_strength_Mn_kip_ft'] < 83.3333333334
    assert r['governing_limit_state']=='flange_local_buckling'


def test_f6_blocks_missing_section_property():
    r=mod.calculate({'design_method':'LRFD','E_ksi':29000,'Fy_ksi':50,'Sy_in3':15.0,'bf_in':8.0,'tf_in':0.75,'required_moment_kip_ft':30.0})
    assert r['status']=='blocked'
    assert 'Zy_in3' in r['validation']['missing_inputs']
