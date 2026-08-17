"""Load-combination selector/evaluator for juniorSE.

This module evaluates a bounded set of common ASCE 7-16/7-22 style ASD and
LRFD load combinations for scalar effects. It is intended for preliminary,
engineer-supervised workflows and does not replace the governing code.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

_VALIDATOR_PATH = Path(__file__).with_name("validator.py")
_spec = importlib.util.spec_from_file_location("select_load_combinations_validator", _VALIDATOR_PATH)
validator = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(validator)

LOADS = ("D", "L", "Lr", "S", "R", "W", "E")
ROOF_ENV = ("Lr", "S", "R")


def _loads(inputs: Dict[str, Any]) -> Dict[str, float]:
    raw = inputs.get("loads", {})
    return {case: float(raw.get(case, 0.0) or 0.0) for case in LOADS}


def _combo_value(loads: Dict[str, float], factors: Dict[str, float]) -> float:
    return sum(loads.get(case, 0.0) * factor for case, factor in factors.items())


def _append_combo(combos: List[Dict[str, Any]], name: str, expression: str, loads: Dict[str, float], factors: Dict[str, float], notes: List[str] | None = None) -> None:
    used = {case: factor for case, factor in factors.items() if factor and (loads.get(case, 0.0) != 0.0 or case == "D")}
    combos.append({
        "name": name,
        "expression": expression,
        "factors": used,
        "value": _combo_value(loads, factors),
        "notes": notes or [],
    })


def _present(loads: Dict[str, float], case: str) -> bool:
    return abs(loads.get(case, 0.0)) > 0.0


def _dominant_roof_env_cases(loads: Dict[str, float]) -> List[str]:
    return [case for case in ROOF_ENV if _present(loads, case)]


def _lrfd_combinations(loads: Dict[str, float], inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
    combos: List[Dict[str, Any]] = []
    companion_l_factor = float(inputs.get("companion_live_load_factor", 1.0))
    if companion_l_factor not in (0.5, 1.0):
        companion_l_factor = 1.0

    _append_combo(combos, "LRFD-1", "1.4D", loads, {"D": 1.4})

    roof_cases = _dominant_roof_env_cases(loads)

    if _present(loads, "L") or roof_cases:
        factors = {"D": 1.2, "L": 1.6}
        expression = "1.2D + 1.6L"
        for case in roof_cases:
            factors[case] = 0.5
        if roof_cases:
            expression += " + 0.5(Lr/S/R present)"
        _append_combo(combos, "LRFD-2", expression, loads, factors)

    for case in roof_cases:
        factors = {"D": 1.2, case: 1.6}
        expression = f"1.2D + 1.6{case}"
        if _present(loads, "L"):
            factors["L"] = companion_l_factor
            expression += f" + {companion_l_factor:g}L"
        if _present(loads, "W"):
            # W can reverse. Generate both signs for scalar target effects.
            for sign, label in ((1.0, "W+"), (-1.0, "W-")):
                wfactors = dict(factors)
                wfactors["W"] = 0.5 * sign
                _append_combo(combos, f"LRFD-3-{case}-{label}", expression + f" + 0.5{label}", loads, wfactors)
        else:
            _append_combo(combos, f"LRFD-3-{case}", expression, loads, factors)

    if _present(loads, "W"):
        base_factors = {"D": 1.2}
        expression = "1.2D + 1.0W"
        if _present(loads, "L"):
            base_factors["L"] = companion_l_factor
            expression += f" + {companion_l_factor:g}L"
        for case in roof_cases:
            base_factors[case] = 0.5
        if roof_cases:
            expression += " + 0.5(Lr/S/R present)"
        for sign, label in ((1.0, "W+"), (-1.0, "W-")):
            factors = dict(base_factors)
            factors["W"] = sign
            _append_combo(combos, f"LRFD-4-{label}", expression.replace("W", label), loads, factors)

        for sign, label in ((1.0, "W+"), (-1.0, "W-")):
            _append_combo(combos, f"LRFD-6-{label}", f"0.9D + 1.0{label}", loads, {"D": 0.9, "W": sign})

    if _present(loads, "E"):
        base_factors = {"D": 1.2}
        expression = "1.2D + 1.0E"
        if _present(loads, "L"):
            base_factors["L"] = companion_l_factor
            expression += f" + {companion_l_factor:g}L"
        if _present(loads, "S"):
            base_factors["S"] = 0.2
            expression += " + 0.2S"
        for sign, label in ((1.0, "E+"), (-1.0, "E-")):
            factors = dict(base_factors)
            factors["E"] = sign
            _append_combo(combos, f"LRFD-5-{label}", expression.replace("E", label), loads, factors)
        for sign, label in ((1.0, "E+"), (-1.0, "E-")):
            _append_combo(combos, f"LRFD-7-{label}", f"0.9D + 1.0{label}", loads, {"D": 0.9, "E": sign})

    return combos


def _asd_combinations(loads: Dict[str, float], inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
    combos: List[Dict[str, Any]] = []
    _append_combo(combos, "ASD-1", "D", loads, {"D": 1.0})

    if _present(loads, "L"):
        _append_combo(combos, "ASD-2", "D + L", loads, {"D": 1.0, "L": 1.0})

    roof_cases = _dominant_roof_env_cases(loads)
    for case in roof_cases:
        _append_combo(combos, f"ASD-3-{case}", f"D + {case}", loads, {"D": 1.0, case: 1.0})

    if _present(loads, "L") and roof_cases:
        factors = {"D": 1.0, "L": 0.75}
        for case in roof_cases:
            factors[case] = 0.75
        _append_combo(combos, "ASD-4", "D + 0.75L + 0.75(Lr/S/R present)", loads, factors)

    if _present(loads, "W"):
        for sign, label in ((1.0, "W+"), (-1.0, "W-")):
            _append_combo(combos, f"ASD-5-{label}", f"D + 0.6{label}", loads, {"D": 1.0, "W": 0.6 * sign})

        base_factors = {"D": 1.0}
        if _present(loads, "L"):
            base_factors["L"] = 0.75
        for case in roof_cases:
            base_factors[case] = 0.75
        if len(base_factors) > 1:
            for sign, label in ((1.0, "W+"), (-1.0, "W-")):
                factors = dict(base_factors)
                factors["W"] = 0.75 * 0.6 * sign
                _append_combo(combos, f"ASD-6-{label}", f"D + 0.75L/roof + 0.75(0.6{label})", loads, factors)

        for sign, label in ((1.0, "W+"), (-1.0, "W-")):
            _append_combo(combos, f"ASD-7-{label}", f"0.6D + 0.6{label}", loads, {"D": 0.6, "W": 0.6 * sign})

    if _present(loads, "E"):
        for sign, label in ((1.0, "E+"), (-1.0, "E-")):
            _append_combo(combos, f"ASD-8-{label}", f"D + 0.7{label}", loads, {"D": 1.0, "E": 0.7 * sign})

        base_factors = {"D": 1.0}
        if _present(loads, "L"):
            base_factors["L"] = 0.75
        if _present(loads, "S"):
            base_factors["S"] = 0.75
        if len(base_factors) > 1:
            for sign, label in ((1.0, "E+"), (-1.0, "E-")):
                factors = dict(base_factors)
                factors["E"] = 0.75 * 0.7 * sign
                _append_combo(combos, f"ASD-9-{label}", f"D + 0.75L/S + 0.75(0.7{label})", loads, factors)

        for sign, label in ((1.0, "E+"), (-1.0, "E-")):
            _append_combo(combos, f"ASD-10-{label}", f"0.6D + 0.7{label}", loads, {"D": 0.6, "E": 0.7 * sign})

    return combos


def _governing(combos: Iterable[Dict[str, Any]]) -> Tuple[Dict[str, Any] | None, Dict[str, Any] | None, Dict[str, Any] | None]:
    combo_list = list(combos)
    if not combo_list:
        return None, None, None
    positive = max(combo_list, key=lambda c: c["value"])
    negative = min(combo_list, key=lambda c: c["value"])
    absolute = max(combo_list, key=lambda c: abs(c["value"]))
    return positive, negative, absolute


def select_combinations(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Validate inputs and evaluate candidate load combinations.

    Returns scalar candidate combination values for the provided target effect.
    Sign-sensitive wind/seismic combinations are returned in positive and
    negative directions.
    """
    validation = validator.validate(inputs)
    warnings = list(validation.get("warnings", []))

    if str(inputs.get("load_level", "")).lower() == "factored":
        return {
            "status": "blocked",
            "validation": validation,
            "candidate_combinations": [],
            "warnings": warnings or ["Loads are already factored. Do not re-factor unless explicitly justified."],
            "engineer_review_required": True,
        }

    if validation["status"] != "ready":
        return {
            "status": "blocked",
            "validation": validation,
            "candidate_combinations": [],
            "warnings": warnings,
            "engineer_review_required": True,
        }

    loads = _loads(inputs)
    method = str(inputs["design_method"]).strip().upper()
    if method == "LRFD":
        combos = _lrfd_combinations(loads, inputs)
    else:
        combos = _asd_combinations(loads, inputs)

    positive, negative, absolute = _governing(combos)
    if method == "LRFD" and inputs.get("companion_live_load_factor") is None and _present(loads, "L") and (_present(loads, "W") or _present(loads, "E")):
        warnings.append("Companion live-load factor defaults to 1.0. Confirm whether project-specific code conditions permit 0.5L.")

    return {
        "status": "complete_preliminary",
        "code_family": inputs.get("code_family"),
        "code_edition": inputs.get("code_edition"),
        "design_method": method,
        "load_level": inputs.get("load_level"),
        "objective": inputs.get("objective"),
        "loads": {case: value for case, value in loads.items() if abs(value) > 0.0},
        "candidate_combinations": combos,
        "governing_positive": positive,
        "governing_negative": negative,
        "governing_absolute": absolute,
        "warnings": warnings,
        "limitations": [
            "This selector evaluates scalar target effects only; member/system sign conventions must be confirmed.",
            "This version supports common D, L, Lr, S, R, W, and E combinations only.",
            "Flood, soil, self-straining, crane, construction, ponding, ice, and special load-combination provisions are not implemented.",
            "Final code interpretation and project-specific amendments require engineer review.",
        ],
        "engineer_review_required": True,
    }
