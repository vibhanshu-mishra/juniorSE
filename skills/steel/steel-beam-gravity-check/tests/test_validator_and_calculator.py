import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

spec_v = importlib.util.spec_from_file_location("steel_beam_check_validator", ROOT / "validator.py")
validator = importlib.util.module_from_spec(spec_v)
spec_v.loader.exec_module(validator)

spec_c = importlib.util.spec_from_file_location("steel_beam_check_calculator", ROOT / "calculator.py")
calculator = importlib.util.module_from_spec(spec_c)
spec_c.loader.exec_module(calculator)

BASE_INPUTS = {
    "code_family": "ASCE 7 / AISC",
    "code_edition": "ASCE 7-22 / AISC 360-22",
    "design_method": "LRFD",
    "span_ft": 20,
    "dead_load_plf": 1000,
    "live_load_plf": 2000,
    "load_level": "service",
    "support_condition": "simply_supported",
    "bracing_condition": "continuous top flange bracing stated by user",
    "steel_grade": "A992 Fy=50 ksi",
    "member_section": "W-shape with Ix provided",
    "composite_status": "non-composite",
    "E_ksi": 29000,
    "Ix_in4": 1000,
}


def test_validator_ready_for_serviceability_check_inputs():
    result = validator.validate(BASE_INPUTS)
    assert result["status"] == "ready"
    assert result["missing_inputs"] == []
    assert result["serviceability_missing_inputs"] == []


def test_validator_blocks_missing_stiffness_for_current_check_scope():
    inputs = dict(BASE_INPUTS)
    inputs.pop("Ix_in4")
    result = validator.validate(inputs)
    assert result["status"] == "blocked"
    assert "Ix_in4" in result["serviceability_missing_inputs"]


def test_calculator_reports_analysis_demands():
    result = calculator.calculate(BASE_INPUTS)
    total = result["analysis_results"]["dead_plus_live"]
    assert result["status"] == "complete_serviceability_only"
    assert total["reaction_each_end_lb"] == 30000
    assert total["max_shear_lb"] == 30000
    assert total["max_moment_kip_ft"] == 150


def test_calculator_compares_live_to_L_over_240_and_total_to_L_over_360():
    result = calculator.calculate(BASE_INPUTS)
    service = result["serviceability"]
    assert service["live_load_limit_in"] == 1.0
    assert round(service["dead_plus_live_limit_in"], 6) == round(240 / 360, 6)
    assert "live_load_passes_L_over_240" in service
    assert "dead_plus_live_passes_L_over_360" in service


def test_calculator_does_not_claim_strength_check():
    result = calculator.calculate(BASE_INPUTS)
    assert result["strength_checks"]["status"] == "not_implemented_current_version"
    assert "AISC flexural capacity" in result["strength_checks"]["not_checked"]
