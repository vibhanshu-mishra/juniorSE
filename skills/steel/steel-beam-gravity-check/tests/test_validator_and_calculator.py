import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

spec_v = importlib.util.spec_from_file_location("steel_beam_validator", ROOT / "validator.py")
validator = importlib.util.module_from_spec(spec_v)
spec_v.loader.exec_module(validator)

spec_c = importlib.util.spec_from_file_location("steel_beam_calculator", ROOT / "calculator.py")
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
    "member_section": "W-shape provided separately",
}


def test_validator_ready_for_complete_simple_beam_inputs():
    result = validator.validate(BASE_INPUTS)
    assert result["status"] == "ready"
    assert result["missing_inputs"] == []


def test_validator_blocks_missing_bracing_condition():
    inputs = dict(BASE_INPUTS)
    inputs.pop("bracing_condition")
    result = validator.validate(inputs)
    assert result["status"] == "blocked"
    assert "bracing_condition" in result["missing_inputs"]


def test_calculator_simple_uniform_load_demands():
    result = calculator.calculate(BASE_INPUTS)
    assert result["status"] == "complete_analysis_only"
    assert result["results"]["reaction_each_end_lb"] == 30000
    assert result["results"]["max_shear_lb"] == 30000
    assert result["results"]["max_moment_kip_ft"] == 150


def test_calculator_blocks_when_validator_blocks():
    inputs = dict(BASE_INPUTS)
    inputs.pop("design_method")
    result = calculator.calculate(inputs)
    assert result["status"] == "blocked"
