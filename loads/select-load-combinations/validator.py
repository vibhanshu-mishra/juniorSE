"""Validation for juniorSE ASCE 7 Chapter 2 load-combination selector."""
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
import yaml

HERE = Path(__file__).resolve().parent

BASE_REQUIRED = ("code_family", "code_edition", "design_method", "load_level", "loads", "objective")
SUPPORTED_EDITIONS = {"ASCE 7-16", "ASCE 7-22"}
SUPPORTED_METHODS = {"ASD", "LRFD"}
RECOGNIZED = {"D","L","Lr","S","R","W","E","F","H","WT","Ev","Eh","Emh","Hw","Fa","Di","Wi","T","N","Ak","Ni"}
SPECIAL_FAMILIES = {"flood","ice","self_straining","nonspecified","extraordinary","structural_integrity","water_in_soil"}


def _ruleset(edition: str) -> Dict[str, Any]:
    name = "asce7_16.yaml" if edition == "ASCE 7-16" else "asce7_22.yaml"
    with open(HERE / "rules" / name, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate(inputs: Dict[str, Any]) -> Dict[str, Any]:
    missing = [k for k in BASE_REQUIRED if inputs.get(k) in (None, "")]
    errors = []
    warnings = []
    loads = inputs.get("loads") if isinstance(inputs.get("loads"), dict) else {}
    edition = str(inputs.get("code_edition", ""))
    method = str(inputs.get("design_method", "")).upper()
    objective = str(inputs.get("objective", "")).lower()
    family = str(inputs.get("chapter2_family", "basic")).lower()

    if inputs.get("code_family") not in (None, "ASCE 7"):
        errors.append("Only ASCE 7 is supported by this skill.")
    if edition and edition not in SUPPORTED_EDITIONS:
        errors.append("Unsupported ASCE 7 edition.")
    if method and method not in SUPPORTED_METHODS:
        errors.append("design_method must be ASD or LRFD.")
    if inputs.get("load_level") not in (None, "service", "factored"):
        errors.append("load_level must be service or factored.")
    if inputs.get("load_level") == "factored":
        warnings.append("Loads are already factored. Do not apply Chapter 2 factors again without explicit justification.")

    nonnumeric = []
    unsupported = []
    for k, v in loads.items():
        if k not in RECOGNIZED:
            unsupported.append(k)
        try:
            float(v)
        except (TypeError, ValueError):
            nonnumeric.append(k)
    if unsupported:
        errors.append("Unrecognized load cases are present.")
    if nonnumeric:
        errors.append("All load effects must be numeric scalar effects for this evaluator.")

    edition_incompatible_load_cases = []
    edition_incompatible_families = []
    if edition == "ASCE 7-16":
        for k in ("WT", "Hw"):
            if k in loads:
                edition_incompatible_load_cases.append(k)
        if family == "water_in_soil":
            edition_incompatible_families.append("water_in_soil")
    if edition_incompatible_load_cases:
        errors.append("One or more load cases are not supported in the selected ASCE 7 edition.")
    if edition_incompatible_families:
        errors.append("The selected Chapter 2 family is not available in this edition.")

    if "H" in loads and inputs.get("h_effect") not in {"adds", "resists"}:
        missing.append("h_effect")
    if "H" in loads and inputs.get("h_effect") == "resists" and "h_is_permanent" not in inputs:
        missing.append("h_is_permanent")

    # 7-22 explicitly separates resolved vertical/horizontal seismic effects.
    if edition == "ASCE 7-22" and "E" in loads and not ({"Ev","Eh","Emh"} & set(loads)):
        if inputs.get("seismic_effect_definition") != "resolved_legacy_E":
            missing.append("seismic_effect_definition")

    if family in SPECIAL_FAMILIES and not inputs.get("resolved_special_combinations"):
        missing.append("resolved_special_combinations")

    # serviceability is valid input, but it routes elsewhere rather than erroring.
    if objective == "serviceability":
        warnings.append("Serviceability should use service-load/serviceability criteria, not Chapter 2 strength/ASD combinations.")

    missing = list(dict.fromkeys(missing))
    status = "ready" if not missing and not errors else "blocked"
    rs = _ruleset(edition) if edition in SUPPORTED_EDITIONS else None
    return {
        "status": status,
        "missing_inputs": missing,
        "errors": errors,
        "warnings": warnings,
        "unsupported_load_cases": unsupported,
        "nonnumeric_load_cases": nonnumeric,
        "edition_incompatible_load_cases": edition_incompatible_load_cases,
        "edition_incompatible_families": edition_incompatible_families,
        "chapter2_family": family,
        "ruleset": rs,
        "engineer_review_required": True,
    }
