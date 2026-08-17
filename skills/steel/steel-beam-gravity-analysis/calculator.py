"""Calculator for juniorSE steel-beam-gravity-analysis.

Current executable scope:
- simply supported beam
- uniform dead and live gravity loads
- reactions, maximum shear, maximum moment
- service deflection checks when E_ksi and Ix_in4 are provided

This does not perform AISC strength/capacity checks.
"""
from __future__ import annotations

from typing import Any, Dict

from validator import validate


def _uniform_simple_results(w_plf: float, span_ft: float) -> Dict[str, float]:
    reaction_lb = w_plf * span_ft / 2.0
    max_moment_kip_ft = (w_plf * span_ft**2 / 8.0) / 1000.0
    return {
        "uniform_load_plf": w_plf,
        "reaction_each_end_lb": reaction_lb,
        "max_shear_lb": reaction_lb,
        "max_moment_kip_ft": max_moment_kip_ft,
    }


def _deflection_in(w_plf: float, span_ft: float, E_ksi: float, Ix_in4: float) -> float:
    E_psi = E_ksi * 1000.0
    L_in = span_ft * 12.0
    w_lb_per_in = w_plf / 12.0
    return 5 * w_lb_per_in * L_in**4 / (384 * E_psi * Ix_in4)


def calculate(inputs: Dict[str, Any]) -> Dict[str, Any]:
    validation = validate(inputs)
    if validation["status"] != "ready":
        return {"status": "blocked", "validation": validation}

    span_ft = float(inputs["span_ft"])
    dead = float(inputs.get("dead_load_plf", 0.0))
    live = float(inputs.get("live_load_plf", 0.0))
    total = dead + live

    L_in = span_ft * 12.0
    live_limit_in = L_in / 240.0
    total_limit_in = L_in / 360.0

    result: Dict[str, Any] = {
        "status": "complete_analysis_only",
        "validation": validation,
        "scope_note": "Analysis and serviceability only. AISC member-capacity checks are not performed by this skill.",
        "inputs_used": {
            "span_ft": span_ft,
            "dead_load_plf": dead,
            "live_load_plf": live,
            "total_service_load_plf": total,
            "load_level": str(inputs["load_level"]).lower(),
            "serviceability_criteria": {
                "live_load": "L/240",
                "dead_plus_live": "L/360",
            },
        },
        "analysis_results": {
            "dead_load": _uniform_simple_results(dead, span_ft),
            "live_load": _uniform_simple_results(live, span_ft),
            "dead_plus_live": _uniform_simple_results(total, span_ft),
        },
        "serviceability": {
            "live_load_limit_in": live_limit_in,
            "dead_plus_live_limit_in": total_limit_in,
            "status": "incomplete_without_E_ksi_and_Ix_in4",
        },
        "qaqc": [
            "Validation completed before calculation.",
            "Current load model checked: simply supported uniform gravity load only.",
            "Deflection criteria set to LL L/240 and D+L L/360 per project direction.",
            "AISC capacity, LTB, compactness, and local checks are not performed by this analysis skill.",
        ],
        "engineer_review_required": True,
    }

    if validation["deflection_ready"]:
        E_ksi = float(inputs["E_ksi"])
        Ix_in4 = float(inputs["Ix_in4"])
        dead_delta = _deflection_in(dead, span_ft, E_ksi, Ix_in4)
        live_delta = _deflection_in(live, span_ft, E_ksi, Ix_in4)
        total_delta = _deflection_in(total, span_ft, E_ksi, Ix_in4)
        result["inputs_used"].update({"E_ksi": E_ksi, "Ix_in4": Ix_in4})
        result["serviceability"].update(
            {
                "status": "checked",
                "dead_load_deflection_in": dead_delta,
                "live_load_deflection_in": live_delta,
                "dead_plus_live_deflection_in": total_delta,
                "live_load_limit_in": live_limit_in,
                "dead_plus_live_limit_in": total_limit_in,
                "live_load_ratio_to_L_over_240": live_delta / live_limit_in if live_limit_in else None,
                "dead_plus_live_ratio_to_L_over_360": total_delta / total_limit_in if total_limit_in else None,
                "live_load_passes_L_over_240": live_delta <= live_limit_in,
                "dead_plus_live_passes_L_over_360": total_delta <= total_limit_in,
            }
        )

    return result
