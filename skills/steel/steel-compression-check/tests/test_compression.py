import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('compression_calc', ROOT / 'calculator.py')
calc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(calc)


def e1d_lrfd():
    return {
        'design_method': 'LRFD',
        'section_type': 'rolled_I',
        'Fy_ksi': 50.0,
        'E_ksi': 29000.0,
        'Ag_in2': 26.5,
        'required_compression_kip': 840.0,
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


def test_blocks_without_effective_length_factor():
    i = e1d_lrfd()
    i.pop('Kx')
    r = calc.calculate(i)
    assert r['status'] == 'blocked'


def test_blocks_without_e4_review():
    i = e1d_lrfd()
    i.pop('e4_review_status')
    r = calc.calculate(i)
    assert r['status'] == 'blocked'


def test_aisc_companion_e1d_lrfd_flexural_buckling():
    r = calc.calculate(e1d_lrfd())
    assert r['status'] == 'complete'
    assert r['chapter_route'] == 'E3'
    assert r['governing_axis'] == 'x'
    assert abs(r['axes']['x']['KL_over_r'] - 58.6) < 0.1
    assert abs(r['axes']['x']['Fe_ksi'] - 83.3) < 0.2
    assert abs(r['Fcr_ksi'] - 38.9) < 0.2
    assert abs(r['available_strength_kip'] - 927.0) < 2.0
    assert r['passes'] is True


def test_aisc_companion_e1d_asd_flexural_buckling():
    i = e1d_lrfd()
    i['design_method'] = 'ASD'
    i['required_compression_kip'] = 560.0
    r = calc.calculate(i)
    assert abs(r['available_strength_kip'] - 617.0) < 2.0
    assert r['passes'] is True


def test_aisc_companion_e2_slender_web_routes_to_e7():
    i = {
        'design_method': 'LRFD',
        'section_type': 'built_up_I',
        'Fy_ksi': 50.0,
        'E_ksi': 29000.0,
        'Ag_in2': 19.8,
        'required_compression_kip': 420.0,
        'Lx_in': 180.0,
        'Ly_in': 180.0,
        'Kx': 1.0,
        'Ky': 1.0,
        'rx_in': 6.0,
        'ry_in': 2.08,
        'bf_in': 8.0,
        'tf_in': 1.0,
        'h_in': 15.0,
        'tw_in': 0.25,
        'e4_review_status': 'checked_separately_non_governing',
    }
    r = calc.calculate(i)
    assert r['status'] == 'complete'
    assert r['chapter_route'] == 'E7'
    assert r['classification']['web']['slender'] is True
    assert abs(r['Fcr_ksi'] - 28.9) < 0.2
    assert abs(r['effective_area_in2'] - 19.2) < 0.15
    assert abs(r['available_strength_kip'] - 500.0) < 3.0
    assert r['passes'] is True


def test_invalid_section_family_blocks():
    i = e1d_lrfd()
    i['section_type'] = 'HSS_rectangular'
    r = calc.calculate(i)
    assert r['status'] == 'blocked'
