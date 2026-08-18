import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('axial_calc', ROOT / 'calculator.py')
calc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(calc)


def tension_member_inputs():
    return {
        'design_method': 'LRFD',
        'Fy_ksi': 50.0,
        'Fu_ksi': 65.0,
        'Ag_in2': 10.0,
        'An_in2': 8.5,
        'U': 0.90,
    }


def compression_member_inputs():
    return {
        'design_method': 'LRFD',
        'section_type': 'rolled_I',
        'Fy_ksi': 50.0,
        'E_ksi': 29000.0,
        'Ag_in2': 26.5,
        'Lx_in': 360.0,
        'Ly_in': 180.0,
        'Kx': 1.0,
        'Ky': 1.0,
        'rx_in': 6.14,
        'ry_in': 3.70,
        'bf_in': 14.52,
        'tf_in': 14.52 / (2 * 10.2),
        'h_in': 12.95,
        'tw_in': 12.95 / 25.9,
        'e4_review_status': 'checked_separately_non_governing',
    }


def test_routes_positive_axial_force_to_tension_chapter_d():
    r = calc.calculate({
        'sign_convention': 'tension_positive',
        'required_axial_kip': 300.0,
        'member_inputs': tension_member_inputs(),
    })
    assert r['status'] == 'complete'
    assert r['source_skill'] == 'steel-tension-check'
    assert r['axial_strength_result']['force_type'] == 'tension'
    assert r['axial_strength_result']['chapter'] == 'D'
    assert r['axial_strength_result']['required_strength_kip'] == 300.0
    assert abs(r['axial_strength_result']['available_strength_kip'] - 372.9375) < 1e-9


def test_routes_negative_axial_force_to_compression_chapter_e():
    r = calc.calculate({
        'sign_convention': 'tension_positive',
        'required_axial_kip': -840.0,
        'member_inputs': compression_member_inputs(),
    })
    assert r['status'] == 'complete'
    assert r['source_skill'] == 'steel-compression-check'
    assert r['axial_strength_result']['force_type'] == 'compression'
    assert r['axial_strength_result']['chapter'] == 'E'
    assert r['axial_strength_result']['required_strength_kip'] == 840.0
    assert abs(r['axial_strength_result']['available_strength_kip'] - 927.0) < 2.0


def test_zero_axial_force_returns_zero_demand_result_without_child_check():
    r = calc.calculate({
        'sign_convention': 'tension_positive',
        'required_axial_kip': 0.0,
        'member_inputs': {},
    })
    assert r['status'] == 'complete'
    assert r['source_skill'] is None
    assert r['axial_strength_result']['force_type'] == 'none'
    assert r['axial_strength_result']['required_strength_kip'] == 0.0
    assert r['axial_strength_result']['dcr'] == 0.0
    assert r['axial_strength_result']['passes'] is True


def test_blocks_unknown_sign_convention():
    r = calc.calculate({
        'sign_convention': 'compression_positive',
        'required_axial_kip': 100.0,
        'member_inputs': tension_member_inputs(),
    })
    assert r['status'] == 'blocked'
    assert any('tension_positive' in e for e in r['validation']['errors'])


def test_propagates_tension_child_block_when_shear_lag_missing():
    inputs = tension_member_inputs()
    inputs.pop('U')
    r = calc.calculate({
        'sign_convention': 'tension_positive',
        'required_axial_kip': 100.0,
        'member_inputs': inputs,
    })
    assert r['status'] == 'blocked'
    assert r['source_skill'] == 'steel-tension-check'
    assert r['child_result']['status'] == 'blocked'
    assert any('U' in e for e in r['child_result']['validation']['errors'])


def test_propagates_compression_child_block_when_e4_review_missing():
    inputs = compression_member_inputs()
    inputs.pop('e4_review_status')
    r = calc.calculate({
        'sign_convention': 'tension_positive',
        'required_axial_kip': -100.0,
        'member_inputs': inputs,
    })
    assert r['status'] == 'blocked'
    assert r['source_skill'] == 'steel-compression-check'
    assert r['child_result']['status'] == 'blocked'


def test_does_not_overwrite_conflicting_child_required_strength_field():
    inputs = tension_member_inputs()
    inputs['required_tension_kip'] = 999.0
    r = calc.calculate({
        'sign_convention': 'tension_positive',
        'required_axial_kip': 100.0,
        'member_inputs': inputs,
    })
    assert r['status'] == 'blocked'
    assert any('required_tension_kip' in e for e in r['validation']['errors'])
