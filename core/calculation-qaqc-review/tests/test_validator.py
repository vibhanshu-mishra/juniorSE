from pathlib import Path
import importlib.util
import json

MODULE_PATH = Path(__file__).resolve().parents[1] / "validator.py"
spec = importlib.util.spec_from_file_location("qaqc_validator", MODULE_PATH)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def load_example(name):
    return json.loads((Path(__file__).resolve().parents[1] / "examples" / name).read_text())


def test_complete_qaqc_output_ready():
    result = validator.validate(load_example("passing-qaqc-output.json"))
    assert result["status"] == "ready"
    assert result["missing_qaqc_checks"] == []


def test_missing_qaqc_checks_block():
    result = validator.validate(load_example("blocked-missing-qaqc.json"))
    assert result["status"] == "blocked"
    assert result["missing_qaqc_checks"]
