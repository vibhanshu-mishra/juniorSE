"""Edition-aware ASCE 7 Chapter 2 scalar load-combination evaluator for juniorSE.

Numerically executable scope:
- ASCE 7-16 basic LRFD/ASD combinations (including legacy scalar E)
- ASCE 7-22 basic LRFD/ASD combinations, W/WT directionality, F/H rules
- ASCE 7-22 resolved seismic effects Ev/Eh (and optional Emh) for Sections 2.3.6/2.4.5

Special Chapter 2 families are recognized and safely routed. They execute only
when the caller supplies explicitly resolved combinations, preserving the rule
that juniorSE must not invent code-defined hazard factors.
"""
from __future__ import annotations
import importlib.util
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple
import yaml

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("select_load_combinations_validator_v2", HERE / "validator.py")
validator = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(validator)

ALL_LOADS = ("D","L","Lr","S","R","W","E","F","H","WT","Ev","Eh","Emh","Hw","Fa","Di","Wi","T","N","Ak","Ni")


def _ruleset(edition: str) -> Dict[str, Any]:
    fn = "asce7_16.yaml" if edition == "ASCE 7-16" else "asce7_22.yaml"
    with open(HERE / "rules" / fn, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _loads(inputs: Dict[str, Any]) -> Dict[str, float]:
    raw = inputs.get("loads", {})
    return {k: float(raw.get(k, 0.0) or 0.0) for k in ALL_LOADS}


def _value(loads: Dict[str, float], factors: Dict[str, float]) -> float:
    return sum(float(loads.get(k, 0.0)) * float(v) for k, v in factors.items())


def _append(out: List[Dict[str, Any]], name: str, section_id: str, expression: str,
            loads: Dict[str, float], factors: Dict[str, float], notes: List[str] | None = None) -> None:
    out.append({
        "name": name,
        "section_id": section_id,
        "expression": expression,
        "factors": {k: v for k, v in factors.items() if v != 0 and (loads.get(k, 0.0) != 0 or k in {"D","F","H"})},
        "value": _value(loads, factors),
        "notes": notes or [],
    })


def _h_factor(inputs: Dict[str, Any], method: str) -> float | None:
    if "H" not in inputs.get("loads", {}):
        return None
    effect = inputs.get("h_effect")
    permanent = bool(inputs.get("h_is_permanent", False))
    if effect == "adds":
        return 1.6 if method == "LRFD" else 1.0
    if effect == "resists":
        if not permanent:
            return 0.0
        return 0.9 if method == "LRFD" else 0.6
    return None


def _with_fh(base: Dict[str, float], inputs: Dict[str, Any], method: str) -> Dict[str, float]:
    f = dict(base)
    loads = inputs.get("loads", {})
    if "F" in loads and "D" in f:
        f["F"] = f["D"]
    hf = _h_factor(inputs, method)
    if hf is not None:
        f["H"] = hf
    return f


def _wind_variants(loads, base, wind_case, factor, name, section_id, expression, inputs, method):
    out = []
    if abs(loads.get(wind_case, 0.0)) == 0:
        return out
    for sign, lab in ((1.0, "+"), (-1.0, "-")):
        f = dict(base)
        f[wind_case] = factor * sign
        f = _with_fh(f, inputs, method)
        _append(out, f"{name}-{wind_case}{lab}", section_id, expression.replace("{wind}", f"{wind_case}{lab}"), loads, f)
    return out


def _lrfd_716(loads, inputs):
    out = []
    def add(name, sec, expr, f): _append(out, name, sec, expr, loads, _with_fh(f, inputs, "LRFD"))
    add("LRFD-716-1", "2.3.1-1", "1.4D", {"D":1.4})
    # one candidate for each applicable roof environmental principal/companion case
    c2 = {"D":1.2,"L":1.6}
    for k in ("Lr","S","R"):
        if loads[k]: c2[k]=0.5
    if loads["L"] or any(loads[k] for k in ("Lr","S","R")): add("LRFD-716-2", "2.3.1-2", "1.2D+1.6L+0.5(Lr or S or R)", c2)
    for k in ("Lr","S","R"):
        if loads[k]:
            base={"D":1.2,k:1.6}
            if loads["L"]: base["L"]=float(inputs.get("companion_live_load_factor",1.0))
            add(f"LRFD-716-3-{k}", "2.3.1-3", f"1.2D+1.6{k}+(L or 0.5W)", base)
            out += _wind_variants(loads, base, "W", 0.5, f"LRFD-716-3-{k}", "2.3.1-3", f"1.2D+1.6{k}+L+0.5{{wind}}", inputs, "LRFD")
    if loads["W"]:
        base={"D":1.2}
        if loads["L"]: base["L"]=float(inputs.get("companion_live_load_factor",1.0))
        for k in ("Lr","S","R"):
            if loads[k]: base[k]=0.5
        out += _wind_variants(loads, base, "W", 1.0, "LRFD-716-4", "2.3.1-4", "1.2D+1.0{wind}+L+0.5(Lr/S/R)", inputs, "LRFD")
        out += _wind_variants(loads, {"D":0.9}, "W", 1.0, "LRFD-716-6", "2.3.1-6", "0.9D+1.0{wind}", inputs, "LRFD")
    if loads["E"]:
        for sign, lab in ((1.0,"+"),(-1.0,"-")):
            f={"D":1.2,"E":sign}
            if loads["L"]: f["L"]=1.0
            if loads["S"]: f["S"]=0.2
            add(f"LRFD-716-5-E{lab}", "2.3.1-5", "1.2D+1.0E+L+0.2S", f)
            add(f"LRFD-716-7-E{lab}", "2.3.1-7", "0.9D+1.0E", {"D":0.9,"E":sign})
    return out


def _asd_716(loads, inputs):
    out=[]
    def add(name, sec, expr, f): _append(out,name,sec,expr,loads,_with_fh(f,inputs,"ASD"))
    add("ASD-716-1","2.4.1-1","D",{"D":1.0})
    if loads["L"]: add("ASD-716-2","2.4.1-2","D+L",{"D":1,"L":1})
    for k in ("Lr","S","R"):
        if loads[k]: add(f"ASD-716-3-{k}","2.4.1-3",f"D+{k}",{"D":1,k:1})
    for k in ("Lr","S","R"):
        if loads[k] and loads["L"]: add(f"ASD-716-4-{k}","2.4.1-4",f"D+0.75L+0.75{k}",{"D":1,"L":0.75,k:0.75})
    if loads["W"]:
        out += _wind_variants(loads,{"D":1},"W",0.6,"ASD-716-5","2.4.1-5","D+0.6{wind}",inputs,"ASD")
        base={"D":1}
        if loads["L"]: base["L"]=0.75
        for k in ("Lr","S","R"):
            if loads[k]: base[k]=0.75
        out += _wind_variants(loads,base,"W",0.45,"ASD-716-6","2.4.1-6","D+0.75L+0.75(0.6{wind})+0.75(Lr/S/R)",inputs,"ASD")
        out += _wind_variants(loads,{"D":0.6},"W",0.6,"ASD-716-7","2.4.1-7","0.6D+0.6{wind}",inputs,"ASD")
    if loads["E"]:
        for sign,lab in ((1,"+"),(-1,"-")):
            add(f"ASD-716-8-E{lab}","2.4.5","D+0.7E",{"D":1,"E":0.7*sign})
            f={"D":1,"E":0.525*sign}
            if loads["L"]: f["L"]=0.75
            if loads["S"]: f["S"]=0.75
            add(f"ASD-716-9-E{lab}","2.4.5","D+0.75L+0.75(0.7E)+0.75S",f)
            add(f"ASD-716-10-E{lab}","2.4.5","0.6D+0.7E",{"D":0.6,"E":0.7*sign})
    return out


def _lrfd_722(loads, inputs):
    out=[]
    def add(name, sec, expr, f): _append(out,name,sec,expr,loads,_with_fh(f,inputs,"LRFD"))
    add("LRFD-722-1a","2.3.1-1a","1.4D",{"D":1.4})
    # Generate separate alternatives so 'or' logic is not accidentally summed.
    if loads["L"]:
        roof_alts=[(None,0.0),("Lr",0.5),("S",0.3),("R",0.5)]
        for k,fac in roof_alts:
            if k is None or loads[k]:
                f={"D":1.2,"L":1.6}
                if k: f[k]=fac
                add(f"LRFD-722-2a-{k or 'none'}","2.3.1-2a","1.2D+1.6L+(0.5Lr or 0.3S or 0.5R)",f)
    principal={"Lr":1.6,"S":1.0,"R":1.6}
    for k,pfac in principal.items():
        if loads[k]:
            base={"D":1.2,k:pfac}
            if loads["L"]: base["L"]=float(inputs.get("companion_live_load_factor",1.0))
            add(f"LRFD-722-3a-{k}-L","2.3.1-3a",f"1.2D+{pfac:g}{k}+(L or 0.5W)",base)
            out += _wind_variants(loads,base,"W",0.5,f"LRFD-722-3a-{k}","2.3.1-3a",f"1.2D+{pfac:g}{k}+0.5{{wind}}",inputs,"LRFD")
    windcase="WT" if loads["WT"] else "W"
    if loads[windcase]:
        roof_alts=[(None,0.0),("Lr",0.5),("S",0.3),("R",0.5)]
        for k,fac in roof_alts:
            if k is None or loads[k]:
                base={"D":1.2}
                if loads["L"]: base["L"]=1.0
                if k: base[k]=fac
                out += _wind_variants(loads,base,windcase,1.0,f"LRFD-722-4a-{k or 'none'}","2.3.1-4a","1.2D+1.0{wind}+L+(0.5Lr or 0.3S or 0.5R)",inputs,"LRFD")
        out += _wind_variants(loads,{"D":0.9},windcase,1.0,"LRFD-722-5a","2.3.1-5a","0.9D+1.0{wind}",inputs,"LRFD")
    # Resolved seismic effects. Signs apply to horizontal effect; Ev sign is prescribed by combo branch.
    if loads["Ev"] or loads["Eh"] or loads["Emh"]:
        hcase="Emh" if loads["Emh"] else "Eh"
        for sign,lab in ((1.0,"+"),(-1.0,"-")):
            f={"D":1.2,"Ev":1.0,hcase:sign}
            if loads["L"]: f["L"]=1.0
            if loads["S"]: f["S"]=0.2
            add(f"LRFD-722-2.3.6-A-{hcase}{lab}","2.3.6","1.2D+1.0Ev+1.0Eh+L+0.2S",f)
            add(f"LRFD-722-2.3.6-B-{hcase}{lab}","2.3.6","0.9D-1.0Ev+1.0Eh",{"D":0.9,"Ev":-1.0,hcase:sign})
    elif loads["E"] and inputs.get("seismic_effect_definition")=="resolved_legacy_E":
        for sign,lab in ((1,"+"),(-1,"-")):
            f={"D":1.2,"E":sign}
            if loads["L"]: f["L"]=1
            if loads["S"]: f["S"]=0.2
            add(f"LRFD-722-resolved-E-{lab}","2.3.6","resolved E used with 1.2D+E+L+0.2S",f)
            add(f"LRFD-722-resolved-E-uplift-{lab}","2.3.6","resolved E used with 0.9D+E",{"D":0.9,"E":sign})
    return out


def _asd_722(loads, inputs):
    out=[]
    def add(name, sec, expr, f): _append(out,name,sec,expr,loads,_with_fh(f,inputs,"ASD"))
    add("ASD-722-1a","2.4.1-1a","D",{"D":1})
    if loads["L"]: add("ASD-722-2a","2.4.1-2a","D+L",{"D":1,"L":1})
    for k,fac in (("Lr",1.0),("S",0.7),("R",1.0)):
        if loads[k]: add(f"ASD-722-3a-{k}","2.4.1-3a",f"D+{fac:g}{k}",{"D":1,k:fac})
        if loads[k] and loads["L"]: add(f"ASD-722-4a-{k}","2.4.1-4a",f"D+0.75L+0.75({k})",{"D":1,"L":0.75,k:0.75*fac})
    windcase="WT" if loads["WT"] else "W"
    if loads[windcase]:
        out += _wind_variants(loads,{"D":1},windcase,0.6,"ASD-722-5a","2.4.1-5a","D+0.6{wind}",inputs,"ASD")
        for k,fac in (("Lr",1.0),("S",0.7),("R",1.0)):
            if loads["L"] or loads[k]:
                base={"D":1}
                if loads["L"]: base["L"]=0.75
                if loads[k]: base[k]=0.75*fac
                out += _wind_variants(loads,base,windcase,0.45,f"ASD-722-6a-{k}","2.4.1-6a","D+0.75L+0.75(0.6{wind})+0.75(Lr/0.7S/R)",inputs,"ASD")
        out += _wind_variants(loads,{"D":0.6},windcase,0.6,"ASD-722-7a","2.4.1-7a","0.6D+0.6{wind}",inputs,"ASD")
    if loads["Ev"] or loads["Eh"] or loads["Emh"]:
        hcase="Emh" if loads["Emh"] else "Eh"
        for sign,lab in ((1.0,"+"),(-1.0,"-")):
            add(f"ASD-722-2.4.5-8-{hcase}{lab}","2.4.5","D+0.7Ev+0.7Eh",{"D":1,"Ev":0.7,hcase:0.7*sign})
            f={"D":1,"Ev":0.525,hcase:0.525*sign}
            if loads["L"]: f["L"]=0.75
            if loads["S"]: f["S"]=0.1
            add(f"ASD-722-2.4.5-9-{hcase}{lab}","2.4.5","D+0.525Ev+0.525Eh+0.75L+0.1S",f)
            add(f"ASD-722-2.4.5-10-{hcase}{lab}","2.4.5","0.6D-0.7Ev+0.7Eh",{"D":0.6,"Ev":-0.7,hcase:0.7*sign})
    elif loads["E"] and inputs.get("seismic_effect_definition")=="resolved_legacy_E":
        for sign,lab in ((1,"+"),(-1,"-")):
            add(f"ASD-722-resolved-E-{lab}","2.4.5","D+0.7E",{"D":1,"E":0.7*sign})
    return out


def _resolved_special(inputs, loads):
    combos=[]
    raw=inputs.get("resolved_special_combinations") or []
    for i,item in enumerate(raw,1):
        if not isinstance(item,dict) or "factors" not in item:
            continue
        factors={k:float(v) for k,v in item["factors"].items()}
        _append(combos,item.get("name",f"SPECIAL-{i}"),item.get("section_id","Chapter 2 special"),item.get("expression","resolved special combination"),loads,factors,["Factors supplied as resolved code-defined inputs; juniorSE did not infer them."])
    return combos


def _governing(combos: Iterable[Dict[str, Any]]) -> Tuple[Any,Any,Any]:
    c=list(combos)
    if not c: return None,None,None
    return max(c,key=lambda x:x["value"]), min(c,key=lambda x:x["value"]), max(c,key=lambda x:abs(x["value"]))


def select_combinations(inputs: Dict[str, Any]) -> Dict[str, Any]:
    validation=validator.validate(inputs)
    edition=str(inputs.get("code_edition",""))
    ruleset=_ruleset(edition) if edition in {"ASCE 7-16","ASCE 7-22"} else None
    objective=str(inputs.get("objective","")).lower()
    if objective=="serviceability":
        return {"status":"routed","route":"serviceability","message":"Use service-load combinations and project/code serviceability criteria rather than Chapter 2 strength/ASD combinations.","validation":validation,"ruleset":ruleset,"engineer_review_required":True}
    if str(inputs.get("load_level","")).lower()=="factored":
        return {"status":"blocked","validation":validation,"candidate_combinations":[],"warnings":validation.get("warnings",[]),"ruleset":ruleset,"engineer_review_required":True}
    if validation["status"]!="ready":
        return {"status":"blocked","validation":validation,"candidate_combinations":[],"warnings":validation.get("warnings",[]),"ruleset":ruleset,"engineer_review_required":True}
    loads=_loads(inputs)
    family=str(inputs.get("chapter2_family","basic")).lower()
    if family in {"flood","ice","self_straining","nonspecified","extraordinary","structural_integrity","water_in_soil"}:
        combos=_resolved_special(inputs,loads)
    else:
        method=str(inputs["design_method"]).upper()
        if edition=="ASCE 7-16": combos=_lrfd_716(loads,inputs) if method=="LRFD" else _asd_716(loads,inputs)
        else: combos=_lrfd_722(loads,inputs) if method=="LRFD" else _asd_722(loads,inputs)
    pos,neg,ab=_governing(combos)
    return {
        "status":"complete_preliminary",
        "code_family":"ASCE 7","code_edition":edition,"design_method":str(inputs["design_method"]).upper(),
        "chapter2_family":family,"load_level":inputs.get("load_level"),"objective":inputs.get("objective"),
        "loads":{k:v for k,v in loads.items() if abs(v)>0},"candidate_combinations":combos,
        "governing_positive":pos,"governing_negative":neg,"governing_absolute":ab,"ruleset":ruleset,
        "warnings":validation.get("warnings",[]),
        "limitations":[
            "Scalar target-effect evaluator; system/member sign conventions still require engineer confirmation.",
            "Special Chapter 2 families are routed and execute only from explicitly resolved code-defined combination inputs until their numerical rules are independently benchmarked.",
            "Project-specific amendments and hazard-definition chapters remain outside this selector.",
        ],
        "engineer_review_required":True,
    }
