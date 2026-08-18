from __future__ import annotations
import copy
import importlib.util
from pathlib import Path
from typing import Any, Dict

HERE = Path(__file__).resolve().parent
STEEL = HERE.parent


def _load_calc(folder_name: str, module_name: str):
    path = STEEL / folder_name / 'calculator.py'
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_validator():
    spec = importlib.util.spec_from_file_location('steel_axial_strength_validator_local', HERE / 'validator.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = _load_validator()
tension_calc = _load_calc('steel-tension-check', 'steel_tension_calc_for_axial_router')
compression_calc = _load_calc('steel-compression-check', 'steel_compression_calc_for_axial_router')


def calculate(i: Dict[str, Any]) -> Dict[str, Any]:
    check = validator.validate(i)
    if check['status'] != 'ready':
        return {
            'status': 'blocked',
            'validation': check,
            'source_skill': None,
            'engineer_review_required': True,
        }

    force = float(i['required_axial_kip'])
    member_inputs = copy.deepcopy(i['member_inputs'])

    if force == 0.0:
        axial = {
            'force_type': 'none',
            'chapter': None,
            'required_strength_kip': 0.0,
            'available_strength_kip': None,
            'dcr': 0.0,
            'governing_limit_state': 'no_axial_demand',
            'passes': True,
        }
        return {
            'status': 'complete',
            'code_basis': 'No axial design chapter invoked because required axial force is zero.',
            'sign_convention': 'tension_positive',
            'source_skill': None,
            'source_chapter': None,
            'child_result': None,
            'axial_strength_result': axial,
            'engineer_review_required': True,
        }

    if force > 0:
        source_skill = 'steel-tension-check'
        source_chapter = 'D'
        member_inputs['required_tension_kip'] = force
        child = tension_calc.calculate(member_inputs)
    else:
        source_skill = 'steel-compression-check'
        source_chapter = 'E'
        member_inputs['required_compression_kip'] = abs(force)
        child = compression_calc.calculate(member_inputs)

    if child.get('status') != 'complete':
        return {
            'status': 'blocked',
            'sign_convention': 'tension_positive',
            'source_skill': source_skill,
            'source_chapter': source_chapter,
            'child_result': child,
            'engineer_review_required': True,
        }

    axial = copy.deepcopy(child['axial_strength_result'])
    return {
        'status': 'complete',
        'code_basis': child.get('code_basis'),
        'sign_convention': 'tension_positive',
        'signed_required_axial_kip': force,
        'source_skill': source_skill,
        'source_chapter': source_chapter,
        'child_result': child,
        'axial_strength_result': axial,
        'qaqc': {
            'child_skill_reused_without_equation_duplication': True,
            'signed_force_routed_explicitly': True,
            'child_guardrails_preserved': True,
        },
        'engineer_review_required': True,
    }
