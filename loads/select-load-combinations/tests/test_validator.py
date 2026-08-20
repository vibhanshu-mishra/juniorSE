import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

validator = load_module("validator")
calculator = load_module("calculator")


def test_ready_for_complete_lrfd_service_loads_with_numeric_values():
    result = validator.validate({
        "code_family": "ASCE 7",
        "code_edition": "ASCE 7-22",
        "design_method": "LRFD",
        "load_level": "service",
        "loads": {"D": 1.0, "L": 2.0},
        "objective": "strength",
    })
    assert result["status"] == "ready"
    assert result["missing_inputs"] == []


def test_blocks_missing_design_method():
    result = validator.validate({
        "code_family": "ASCE 7",
        "code_edition": "ASCE 7-22",
        "load_level": "service",
        "loads": {"D": 1.0, "L": 2.0},
        "objective": "strength",
    })
    assert result["status"] == "blocked"
    assert "design_method" in result["missing_inputs"]


def test_blocks_factored_loads_for_combination_generation():
    result = calculator.select_combinations({
        "code_family": "ASCE 7",
        "code_edition": "ASCE 7-22",
        "design_method": "LRFD",
        "load_level": "factored",
        "loads": {"D": 1.0, "L": 2.0},
        "objective": "strength",
    })
    assert result["status"] == "blocked"
    assert any("already factored" in warning.lower() for warning in result["warnings"])


def test_lrfd_gravity_combinations_return_governing_value():
    result = calculator.select_combinations({
        "code_family": "ASCE 7",
        "code_edition": "ASCE 7-22",
        "design_method": "LRFD",
        "load_level": "service",
        "loads": {"D": 1.0, "L": 2.0},
        "objective": "strength",
    })
    assert result["status"] == "complete_preliminary"
    assert result["governing_positive"]["name"] == "LRFD-722-2a-none"
    assert abs(result["governing_positive"]["value"] - 4.4) < 1e-9
    assert len(result["candidate_combinations"]) >= 2


def test_asd_gravity_combinations_return_service_level_governing_value():
    result = calculator.select_combinations({
        "code_family": "ASCE 7",
        "code_edition": "ASCE 7-22",
        "design_method": "ASD",
        "load_level": "service",
        "loads": {"D": 1.0, "L": 2.0},
        "objective": "allowable_stress",
    })
    assert result["status"] == "complete_preliminary"
    assert result["governing_positive"]["name"] == "ASD-722-2a"
    assert abs(result["governing_positive"]["value"] - 3.0) < 1e-9


def test_wind_combinations_evaluate_positive_and_negative_lateral_direction():
    result = calculator.select_combinations({
        "code_family": "ASCE 7",
        "code_edition": "ASCE 7-22",
        "design_method": "LRFD",
        "load_level": "service",
        "loads": {"D": 1.0, "W": 5.0},
        "objective": "uplift_or_overturning",
    })
    names = {combo["name"] for combo in result["candidate_combinations"]}
    assert "LRFD-722-5a-W+" in names
    assert "LRFD-722-5a-W-" in names
    assert result["governing_positive"]["value"] == 6.2
    assert result["governing_negative"]["value"] == -4.1


def test_h_load_is_recognized_but_blocks_until_directionality_is_given():
    result = validator.validate({
        "code_family": "ASCE 7",
        "code_edition": "ASCE 7-22",
        "design_method": "LRFD",
        "load_level": "service",
        "loads": {"D": 1.0, "H": 0.4},
        "objective": "strength",
    })
    assert result["status"] == "blocked"
    assert "H" not in result["unsupported_load_cases"]
    assert "h_effect" in result["missing_inputs"]
