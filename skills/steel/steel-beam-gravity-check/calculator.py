"""Starter calculator for juniorSE steel-beam-gravity-check.

Current scope is intentionally limited:
- simply supported beam
- uniform gravity load using D + L service load, or provided factored D/L when load_level=factored
- reactions, maximum shear, maximum moment
- optional elastic deflection if E_ksi and Ix_in4 are provided

This does not perform AISC member-capacity checks yet.
"""
from __future__ import annotations

from typing import Any, Dict

from validator import validate


def calculate(inputs: Dict[str, Any]) -> Dict[str, Any]:
    validation = validate(inputs)
    if validation["status"] != "ready":
        return {"status": "blocked", "validation": validation}

    span_ft = float(inputs["span_ft"])
    dead = float(inputs.get("dead_load_plf", 0.0))
    live = float(inputs.get("live_load_plf", 0.0))
    w_plf = dead + live

    # Simple beam with uniform load:
    # R = wL/2, Vmax = wL/2, Mmax = wL^2/8.
    reaction_lb = w_plf * span_ft / 2.0
    max_shear_lb = reaction_lb
    max_moment_ft_lb = w_plf * span_ft ** 2 / 8.0
    max_moment_kip_ft = max_moment_ft_lb / 1000.0

    result: Dict[str, Any] = {
        "status": "complete_analysis_only",
        "validation": validation,
        "scope_note": "Analysis demand only. AISC capacity checks are not implemented in this starter calculator.",
        "inputs_used": {
            "span_ft": span_ft,
            "dead_load_plf": dead,
            "live_load_plf": live,
            "total_uniform_load_plf": w_plf,
        },
        "results": {
            "reaction_each_end_lb": reaction_lb,
            "max_shear_lb": max_shear_lb,
            "max_moment_kip_ft": max_moment_kip_ft,
        },
        "qaqc": [
            "Validation completed before calculation.",
            "Current load model checked: simply supported uniform gravity load only.",
            "Capacity, LTB, compactness, and local checks not performed by this starter calculator.",
        ],
        "engineer_review_required": True,
    }

    if inputs.get("E_ksi") and inputs.get("Ix_in4"):
        # Delta_max = 5wL^4 / 384EI. Use lb/in, inches, psi, in^4.
        E_psi = float(inputs["E_ksi"]) * 1000.0
        Ix = float(inputs["Ix_in4"])
        L_in = span_ft * 12.0
        w_lb_per_in = w_plf / 12.0
        delta_in = 5 * w_lb_per_in * L_in ** 4 / (384 * E_psi * Ix)
        result["results"]["max_elastic_deflection_in"] = delta_in

    return result
