from __future__ import annotations
import importlib.util
from pathlib import Path
from typing import Any, Dict

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('steel_tension_validator_local', HERE / 'validator.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

PHI_YIELD = 0.90
OMEGA_YIELD = 1.67
PHI_RUPTURE = 0.75
OMEGA_RUPTURE = 2.00


def calculate(i: Dict[str, Any]) -> Dict[str, Any]:
    check = validator.validate(i)
    if check['status'] != 'ready':
        return {
            'status': 'blocked',
            'validation': check,
            'engineer_review_required': True,
        }

    method = str(i['design_method']).upper()
    Fy = float(i['Fy_ksi'])
    Fu = float(i['Fu_ksi'])
    Ag = float(i['Ag_in2'])
    Pr = float(i['required_tension_kip'])

    if i.get('Ae_in2') not in (None, ''):
        Ae = float(i['Ae_in2'])
        ae_basis = 'provided_effective_net_area'
        An = float(i['An_in2']) if i.get('An_in2') not in (None, '') else None
        U = float(i['U']) if i.get('U') not in (None, '') else None
    else:
        An = float(i['An_in2'])
        U = float(i['U'])
        Ae = An * U
        ae_basis = 'An_times_U'

    Pn_y = Fy * Ag
    Pn_u = Fu * Ae

    if method == 'LRFD':
        Pa_y = PHI_YIELD * Pn_y
        Pa_u = PHI_RUPTURE * Pn_u
        factors = {
            'gross_section_yielding': {'phi': PHI_YIELD},
            'net_section_rupture': {'phi': PHI_RUPTURE},
        }
    else:
        Pa_y = Pn_y / OMEGA_YIELD
        Pa_u = Pn_u / OMEGA_RUPTURE
        factors = {
            'gross_section_yielding': {'omega': OMEGA_YIELD},
            'net_section_rupture': {'omega': OMEGA_RUPTURE},
        }

    capacities = {
        'gross_section_yielding': Pa_y,
        'net_section_rupture': Pa_u,
    }
    governing = min(capacities, key=capacities.get)
    available = capacities[governing]
    dcr = Pr / available if available > 0 else float('inf')

    slenderness = {
        'checked': False,
        'L_over_r': None,
        'advisory_limit': 300.0,
        'advisory_exceeded': False,
        'note': 'AISC Chapter D tension-member slenderness is treated here as an advisory, not a tensile-strength reduction.',
    }
    if i.get('member_length_in') not in (None, ''):
        lor = float(i['member_length_in']) / float(i['r_min_in'])
        slenderness.update({
            'checked': True,
            'L_over_r': lor,
            'advisory_exceeded': lor > 300.0,
        })

    axial = {
        'force_type': 'tension',
        'chapter': 'D',
        'required_strength_kip': Pr,
        'available_strength_kip': available,
        'dcr': dcr,
        'governing_limit_state': governing,
        'passes': dcr <= 1.0,
    }

    return {
        'status': 'complete',
        'code_basis': 'AISC 360-16 Chapter D',
        'design_method': method,
        'effective_net_area_in2': Ae,
        'effective_net_area_basis': ae_basis,
        'net_area_in2': An,
        'shear_lag_factor_U': U,
        'nominal_strengths_kip': {
            'gross_section_yielding': Pn_y,
            'net_section_rupture': Pn_u,
        },
        'design_factors': factors,
        'available_strengths_kip': capacities,
        'governing_limit_state': governing,
        'available_strength_kip': available,
        'required_tension_kip': Pr,
        'dcr': dcr,
        'passes': dcr <= 1.0,
        'slenderness': slenderness,
        'axial_strength_result': axial,
        'qaqc': {
            'gross_yielding_checked': True,
            'net_section_rupture_checked': True,
            'effective_net_area_source_explicit': True,
            'no_silent_hole_or_shear_lag_assumptions': True,
        },
        'engineer_review_required': True,
    }
