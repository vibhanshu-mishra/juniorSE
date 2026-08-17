import importlib.util
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "validator.py"
spec = importlib.util.spec_from_file_location("select_load_combinations_validator", MODULE)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def test_ready_for_complete_lrfd_service_inputs():
    result = validator.validate({
        "code_family": "ASCE 7",
        "code_edition": "ASCE 7-22",
        "design_method": "LRFD",
        "load_cases": ["D", "L"],
        "load_level": "service",
    })
    assert result["status"] == "ready"
    assert result["missing_inputs"] == []


def test_blocks_missing_design_method():
    result = validator.validate({
        "code_family": "ASCE 7",
        "code_edition": "ASCE 7-22",
        "load_cases": ["D", "L"],
        "load_level": "service",
    })
    assert result["status"] == "blocked"
    assert "design_method" in result["missing_inputs"]


def test_warns_for_factored_loads():
    result = validator.validate({
        "code_family": "ASCE 7",
        "code_edition": "ASCE 7-22",
        "design_method": "LRFD",
        "load_cases": ["D", "L"],
        "load_level": "factored",
    })
    assert result["status"] == "ready"
    assert result["warnings"]
