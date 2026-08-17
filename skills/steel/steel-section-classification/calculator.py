from __future__ import annotations
import math
from typing import Any, Dict
import importlib.util
from pathlib import Path

def _load_local_validator():
    p = Path(__file__).with_name("validator.py")
    spec = importlib.util.spec_from_file_location(f"juniorse_{p.parent.name}_validator", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.validate

validate = _load_local_validator()

def _classify(lam: float, lp: float, lr: float) -> str:
    if lam <= lp:
        return "compact"
    if lam <= lr:
        return "noncompact"
    return "slender"

def calculate(inputs: Dict[str, Any]) -> Dict[str, Any]:
    v = validate(inputs)
    if v["status"] != "ready":
        return {"status": "blocked", "validation": v}
    E, Fy = float(inputs["E_ksi"]), float(inputs["Fy_ksi"])
    bf, tf, h, tw = map(float, (inputs["bf_in"], inputs["tf_in"], inputs["h_in"], inputs["tw_in"]))
    root = math.sqrt(E/Fy)
    fl, wl = bf/(2*tf), h/tw
    flp, flr = 0.38*root, 1.00*root
    wlp, wlr = 3.76*root, 5.70*root
    fc, wc = _classify(fl, flp, flr), _classify(wl, wlp, wlr)
    if wc == "compact":
        route = "F2" if fc == "compact" else "F3"
    elif wc == "noncompact":
        route = "F4"
    else:
        route = "F5"
    return {
        "status": "complete",
        "basis": "AISC 360-16 Chapter B flexural element classification for doubly symmetric I/W shapes.",
        "flange": {"lambda": fl, "lambda_p": flp, "lambda_r": flr, "classification": fc},
        "web": {"lambda": wl, "lambda_p": wlp, "lambda_r": wlr, "classification": wc},
        "recommended_chapter_f_route": route,
        "engineer_review_required": True,
    }
