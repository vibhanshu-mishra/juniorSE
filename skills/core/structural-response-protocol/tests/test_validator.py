from pathlib import Path
import importlib.util
import json

MODULE_PATH = Path(__file__).resolve().parents[1] / "validator.py"
spec = importlib.util.spec_from_file_location("structural_response_validator", MODULE_PATH)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def load_example(name):
    return json.loads((Path(__file__).resolve().parents[1] / "examples" / name).read_text())


def test_passing_response_is_ready():
    result = validator.validate(load_example("passing-response.json"))
    assert result["status"] == "ready"
    assert result["errors"] == []


def test_forbidden_final_design_language_blocks():
    result = validator.validate(load_example("blocked-final-language.json"))
    assert result["status"] == "blocked"
    assert any("Forbidden" in err for err in result["errors"])
