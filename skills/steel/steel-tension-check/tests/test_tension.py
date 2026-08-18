import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

validator = load('tension_validator', 'validator.py')
calculator = load('tension_calculator', 'calculator.py')


def base():
    return {
        'design_method': 'LRFD',
        'Fy_ksi': 50.0,
        'Fu_ksi': 65.0,
        'Ag_in2': 10.0,
        'An_in2': 8.5,
        'U': 0.90,
        'required_tension_kip': 300.0,
    }


def test_lrfd_gross_yielding_and_net_rupture():
    r = calculator.calculate(base())
    assert r['status'] == 'complete'
    assert abs(r['nominal_strengths_kip']['gross_section_yielding'] - 500.0) < 1e-9
    assert abs(r['effective_net_area_in2'] - 7.65) < 1e-9
    assert abs(r['nominal_strengths_kip']['net_section_rupture'] - 497.25) < 1e-9
    assert abs(r['available_strengths_kip']['gross_section_yielding'] - 450.0) < 1e-9
    assert abs(r['available_strengths_kip']['net_section_rupture'] - 372.9375) < 1e-9
    assert r['governing_limit_state'] == 'net_section_rupture'
    assert r['passes'] is True


def test_asd_available_strengths():
    i = base(); i['design_method'] = 'ASD'
    r = calculator.calculate(i)
    assert abs(r['available_strengths_kip']['gross_section_yielding'] - 500.0/1.67) < 1e-9
    assert abs(r['available_strengths_kip']['net_section_rupture'] - 497.25/2.0) < 1e-9


def test_accepts_direct_effective_net_area():
    i = base(); i.pop('An_in2'); i.pop('U'); i['Ae_in2'] = 7.65
    v = validator.validate(i)
    assert v['status'] == 'ready'
    r = calculator.calculate(i)
    assert abs(r['effective_net_area_in2'] - 7.65) < 1e-9


def test_blocks_complete_check_without_effective_net_area_path():
    i = base(); i.pop('An_in2'); i.pop('U')
    v = validator.validate(i)
    assert v['status'] == 'blocked'
    assert any('Ae_in2' in e or 'An_in2' in e for e in v['errors'])


def test_does_not_invent_shear_lag_factor():
    i = base(); i.pop('U')
    v = validator.validate(i)
    assert v['status'] == 'blocked'
    assert any('U' in e for e in v['errors'])


def test_slenderness_is_advisory_not_strength_block():
    i = base(); i['member_length_in'] = 240.0; i['r_min_in'] = 0.70
    r = calculator.calculate(i)
    assert r['slenderness']['L_over_r'] > 300
    assert r['slenderness']['advisory_exceeded'] is True
    assert r['status'] == 'complete'


def test_rejects_effective_net_area_greater_than_gross_area():
    i = base(); i['Ae_in2'] = 11.0; i.pop('An_in2'); i.pop('U')
    v = validator.validate(i)
    assert v['status'] == 'blocked'


def test_standardized_axial_result_contract():
    r = calculator.calculate(base())
    axial = r['axial_strength_result']
    assert axial['force_type'] == 'tension'
    assert axial['chapter'] == 'D'
    assert axial['required_strength_kip'] == 300.0
    assert axial['available_strength_kip'] == r['available_strength_kip']
    assert axial['dcr'] == r['dcr']
