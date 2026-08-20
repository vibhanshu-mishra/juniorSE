from pathlib import Path
import importlib.util
import json

MODULE_PATH = Path(__file__).resolve().parents[1] / "validator.py"
spec = importlib.util.spec_from_file_location("assumption_guardrails_validator", MODULE_PATH)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def load_example(name):
    return json.loads((Path(__file__).resolve().parents[1] / "examples" / name).read_text())


def test_explicit_assumptions_are_ready_with_warning():
    result = validator.validate(load_example("passing-explicit-assumptions.json"))
    assert result["status"] == "ready"
    assert any("bracing_condition" in warning for warning in result["warnings"])


def test_missing_critical_assumption_blocks():
    result = validator.validate(load_example("blocked-missing-critical.json"))
    assert result["status"] == "blocked"
    assert "bracing_condition" in result["missing_required"]
