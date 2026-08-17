import importlib.util, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
spec=importlib.util.spec_from_file_location("calc",ROOT/"calculator.py"); calc=importlib.util.module_from_spec(spec); spec.loader.exec_module(calc)

def base(): return {"E_ksi":29000,"Fy_ksi":50,"bf_in":8,"tf_in":0.6,"h_in":14,"tw_in":0.4}

def test_compact_routes_to_f2():
    r=calc.calculate(base()); assert r["flange"]["classification"]=="compact"; assert r["web"]["classification"]=="compact"; assert r["recommended_chapter_f_route"]=="F2"

def test_noncompact_flange_routes_to_f3():
    x=base(); x.update({"bf_in":14,"tf_in":0.4}); r=calc.calculate(x); assert r["flange"]["classification"]=="noncompact"; assert r["recommended_chapter_f_route"]=="F3"

def test_slender_flange_routes_to_f3():
    x=base(); x.update({"bf_in":20,"tf_in":0.3}); r=calc.calculate(x); assert r["flange"]["classification"]=="slender"; assert r["recommended_chapter_f_route"]=="F3"
