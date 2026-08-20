"""Static/runtime smoke test for juniorSE's agent packaging layer."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    manifest = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
    assert manifest["name"] == "juniorse"

    router = (ROOT / "plugin-skills" / "juniorse" / "SKILL.md").read_text()
    assert "steel-flexure-check" in router
    assert "assumption-guardrails" in router
    assert "calculation-qaqc-review" in router

    assumptions = load_module(
        ROOT / "skills" / "core" / "assumption-guardrails" / "validator.py",
        "juniorse_smoke_assumptions",
    )
    blocked = assumptions.validate(
        {
            "required_for_scope": ["design_method", "bracing_condition"],
            "assumptions": {
                "design_method": {"value": "LRFD", "status": "user_provided"}
            },
        }
    )
    assert blocked["status"] == "blocked"
    assert "bracing_condition" in blocked["missing_required"]

    qaqc = load_module(
        ROOT / "skills" / "core" / "calculation-qaqc-review" / "validator.py",
        "juniorse_smoke_qaqc",
    )
    incomplete = qaqc.validate(
        {
            "task_classification": "steel beam check",
            "input_summary": {"member": "example"},
            "assumptions": {},
            "engineer_review_required": True,
        }
    )
    assert incomplete["status"] == "blocked"

    print("juniorSE plugin smoke test: PASS")
    print("- plugin manifest readable")
    print("- router references core/design skills")
    print("- missing bracing is blocked")
    print("- incomplete QA/QC output is blocked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
