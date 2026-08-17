"""Current calculator for juniorSE steel-beam-gravity-check.

Current executable scope:
- simply supported uniform gravity load
- analysis demand
- serviceability checks: LL <= L/240 and D+L <= L/360
- strength readiness warning only

This does not perform AISC member-capacity checks yet.
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
    E_ksi = float(inputs["E_ksi"])
    Ix_in4 = float(inputs["Ix_in4"])

    L_in = span_ft * 12.0
    live_limit_in = L_in / 240.0
    total_limit_in = L_in / 360.0
    live_delta = _deflection_in(live, span_ft, E_ksi, Ix_in4)
    total_delta = _deflection_in(total, span_ft, E_ksi, Ix_in4)

    live_ratio = live_delta / live_limit_in
    total_ratio = total_delta / total_limit_in
    serviceability_passes = live_delta <= live_limit_in and total_delta <= total_limit_in

    return {
        "status": "complete_serviceability_only",
        "validation": validation,
        "scope_note": "Current executable scope checks analysis demand and serviceability only. AISC strength capacity checks are not implemented.",
        "inputs_used": {
            "span_ft": span_ft,
            "dead_load_plf": dead,
            "live_load_plf": live,
            "total_service_load_plf": total,
            "E_ksi": E_ksi,
            "Ix_in4": Ix_in4,
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
            "live_load_deflection_in": live_delta,
            "live_load_limit_in": live_limit_in,
            "live_load_ratio_to_L_over_240": live_ratio,
            "live_load_passes_L_over_240": live_delta <= live_limit_in,
            "dead_plus_live_deflection_in": total_delta,
            "dead_plus_live_limit_in": total_limit_in,
            "dead_plus_live_ratio_to_L_over_360": total_ratio,
            "dead_plus_live_passes_L_over_360": total_delta <= total_limit_in,
            "serviceability_passes_current_scope": serviceability_passes,
        },
        "strength_checks": {
            "status": "not_implemented_current_version",
            "message": "Do not report this beam as passing AISC strength checks from this result alone.",
            "not_checked": [
                "AISC flexural capacity",
                "AISC shear capacity",
                "lateral-torsional buckling strength",
                "compactness/local buckling",
                "web yielding/web crippling",
                "connection/support bearing",
            ],
        },
        "qaqc": [
            "Validation completed before calculation.",
            "Current load model checked: simply supported uniform gravity load only.",
            "Live-load deflection compared to L/240.",
            "Dead + live load deflection compared to L/360.",
            "AISC capacity, LTB, compactness, and local checks not performed by this version.",
        ],
        "engineer_review_required": True,
    }
