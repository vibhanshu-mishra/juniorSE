from __future__ import annotations
import importlib.util
import math
from pathlib import Path
from typing import Any, Dict

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('steel_compression_validator_local', HERE / 'validator.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

PHI_C = 0.90
OMEGA_C = 1.67


def _fcr_e3(Fy: float, Fe: float) -> float:
    ratio = Fy / Fe
    if ratio <= 2.25:
        return (0.658 ** ratio) * Fy
    return 0.877 * Fe


def _axis(E: float, L: float, K: float, r: float) -> Dict[str, float]:
    klr = K * L / r
    Fe = math.pi ** 2 * E / (klr ** 2)
    return {'KL_over_r': klr, 'Fe_ksi': Fe}


def _compression_classification(i: Dict[str, Any], E: float, Fy: float) -> Dict[str, Any]:
    bf, tf, h, tw = map(float, (i['bf_in'], i['tf_in'], i['h_in'], i['tw_in']))
    root = math.sqrt(E / Fy)
    flange_lambda = bf / (2.0 * tf)
    web_lambda = h / tw

    if i['section_type'] == 'rolled_I':
        kc = None
        flange_lambda_r = 0.56 * root
        flange_case = 'B4.1a Case 1'
    else:
        kc = 4.0 / math.sqrt(web_lambda)
        kc = max(0.35, min(0.76, kc))
        flange_lambda_r = 0.64 * math.sqrt(kc * E / Fy)
        flange_case = 'B4.1a Case 2'

    web_lambda_r = 1.49 * root
    return {
        'flange': {
            'lambda': flange_lambda,
            'lambda_r': flange_lambda_r,
            'slender': flange_lambda > flange_lambda_r,
            'table_case': flange_case,
            'kc': kc,
        },
        'web': {
            'lambda': web_lambda,
            'lambda_r': web_lambda_r,
            'slender': web_lambda > web_lambda_r,
            'table_case': 'B4.1a Case 5',
        },
    }


def _effective_width(b: float, t: float, lam: float, lam_r: float, Fcr: float, Fy: float, c1: float, c2: float) -> Dict[str, float]:
    threshold = lam_r * math.sqrt(Fy / Fcr)
    if lam <= threshold:
        return {'b_effective_in': b, 'Fel_ksi': None, 'full_effective': True, 'threshold_lambda': threshold}
    Fel = (c2 * lam_r / lam) ** 2 * Fy
    ratio = math.sqrt(Fel / Fcr)
    be = b * (1.0 - c1 * ratio) * ratio
    be = max(0.0, min(b, be))
    return {'b_effective_in': be, 'Fel_ksi': Fel, 'full_effective': False, 'threshold_lambda': threshold}


def calculate(i: Dict[str, Any]) -> Dict[str, Any]:
    check = validator.validate(i)
    if check['status'] != 'ready':
        return {'status': 'blocked', 'validation': check, 'engineer_review_required': True}

    method = str(i['design_method']).upper()
    E = float(i['E_ksi']); Fy = float(i['Fy_ksi']); Ag = float(i['Ag_in2'])
    Pr = float(i['required_compression_kip'])

    axes = {
        'x': _axis(E, float(i['Lx_in']), float(i['Kx']), float(i['rx_in'])),
        'y': _axis(E, float(i['Ly_in']), float(i['Ky']), float(i['ry_in'])),
    }
    for a in axes.values():
        a['Fcr_ksi'] = _fcr_e3(Fy, a['Fe_ksi'])

    governing_axis = min(axes, key=lambda k: axes[k]['Fcr_ksi'])
    Fcr = axes[governing_axis]['Fcr_ksi']
    classification = _compression_classification(i, E, Fy)
    slender = classification['flange']['slender'] or classification['web']['slender']

    effective = {'flange': None, 'web': None}
    Ae = Ag
    route = 'E3'
    if slender:
        route = 'E7'
        bf = float(i['bf_in']); tf = float(i['tf_in']); h = float(i['h_in']); tw = float(i['tw_in'])
        if classification['flange']['slender']:
            b = bf / 2.0
            ef = _effective_width(
                b, tf, classification['flange']['lambda'], classification['flange']['lambda_r'],
                Fcr, Fy, 0.22, 1.49
            )
            effective['flange'] = ef
            Ae -= 4.0 * (b - ef['b_effective_in']) * tf
        if classification['web']['slender']:
            ef = _effective_width(
                h, tw, classification['web']['lambda'], classification['web']['lambda_r'],
                Fcr, Fy, 0.18, 1.31
            )
            effective['web'] = ef
            Ae -= (h - ef['b_effective_in']) * tw
        if Ae <= 0 or Ae > Ag + 1e-9:
            return {
                'status': 'blocked',
                'validation': {'status': 'blocked', 'errors': ['Calculated effective area is nonphysical; engineer review required.']},
                'engineer_review_required': True,
            }

    Pn = Fcr * Ae
    available = PHI_C * Pn if method == 'LRFD' else Pn / OMEGA_C
    dcr = Pr / available if available > 0 else float('inf')

    axial = {
        'force_type': 'compression',
        'chapter': 'E',
        'required_strength_kip': Pr,
        'available_strength_kip': available,
        'dcr': dcr,
        'governing_limit_state': 'flexural_buckling_with_slender_elements' if route == 'E7' else f'flexural_buckling_{governing_axis}',
        'passes': dcr <= 1.0,
    }

    return {
        'status': 'complete',
        'code_basis': 'AISC 360-16 Chapter E; flexural-buckling path E3 with E7 effective-area treatment for slender I-shape elements.',
        'design_method': method,
        'chapter_route': route,
        'classification': classification,
        'axes': axes,
        'governing_axis': governing_axis,
        'Fcr_ksi': Fcr,
        'effective_widths': effective,
        'gross_area_in2': Ag,
        'effective_area_in2': Ae,
        'nominal_strength_kip': Pn,
        'available_strength_kip': available,
        'required_compression_kip': Pr,
        'dcr': dcr,
        'passes': dcr <= 1.0,
        'design_factor': {'phi_c': PHI_C} if method == 'LRFD' else {'omega_c': OMEGA_C},
        'e4_review_status': i['e4_review_status'],
        'axial_strength_result': axial,
        'qaqc': {
            'both_flexural_axes_checked': True,
            'chapter_b_compression_slenderness_checked': True,
            'e7_effective_area_checked_when_required': slender,
            'effective_length_factors_explicit': True,
            'chapter_e4_not_silently_ignored': True,
        },
        'limitations': [
            'Phase 3B supports rolled or built-up doubly symmetric I-shaped members only.',
            'Chapter E4 torsional/flexural-torsional buckling is not calculated in this skill and must be explicitly reviewed as non-governing/not required.',
            'Chapter C global stability compliance is outside this skill.',
        ],
        'engineer_review_required': True,
    }
