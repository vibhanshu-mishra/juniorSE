import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

spec_v = importlib.util.spec_from_file_location("beam_analysis_validator", ROOT / "validator.py")
validator = importlib.util.module_from_spec(spec_v)
spec_v.loader.exec_module(validator)

spec_c = importlib.util.spec_from_file_location("beam_analysis_calculator", ROOT / "calculator.py")
calculator = importlib.util.module_from_spec(spec_c)
spec_c.loader.exec_module(calculator)

BASE_INPUTS = {
    "span_ft": 20,
    "dead_load_plf": 1000,
    "live_load_plf": 2000,
    "load_level": "service",
    "support_condition": "simply_supported",
    "E_ksi": 29000,
    "Ix_in4": 1000,
}


def test_analysis_validator_ready_for_simple_uniform_beam():
    result = validator.validate(BASE_INPUTS)
    assert result["status"] == "ready"
    assert result["deflection_ready"] is True


def test_analysis_accepts_categorized_point_loads():
    inputs = dict(BASE_INPUTS)
    inputs["point_loads"] = [{"P_lb": 5000, "x_ft": 10, "category": "live"}]
    result = validator.validate(inputs)
    assert result["status"] == "ready"


def test_analysis_demands_for_simple_uniform_loads():
    result = calculator.calculate(BASE_INPUTS)
    total = result["analysis_results"]["dead_plus_live"]
    assert result["status"] == "complete_general_beam_analysis"
    assert abs(total["support_reactions"][0]["vertical_lb"] - 30000) < 1
    assert abs(total["max_abs_shear_kips"] - 30) < 0.05
    assert abs(total["max_positive_moment_kip_ft"] - 150) < 0.05


def test_analysis_serviceability_uses_live_L_over_240_and_total_L_over_360():
    result = calculator.calculate(BASE_INPUTS)
    service = result["serviceability"]
    assert service["status"] == "checked"
    assert service["live_load_limit_in"] == 1.0  # 20 ft = 240 in; 240/240 = 1.0 in
    assert round(service["dead_plus_live_limit_in"], 6) == round(240 / 360, 6)
    assert "live_load_ratio_to_L_over_240" in service
    assert "dead_plus_live_ratio_to_L_over_360" in service
