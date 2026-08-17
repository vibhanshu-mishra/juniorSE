import importlib.util,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R));s=importlib.util.spec_from_file_location("c",R/"calculator.py");c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
def b():return {"design_method":"LRFD","E_ksi":29000,"Fy_ksi":50,"d_in":18,"tw_in":0.4,"tf_in":0.6,"k_in":1.0,"bearing_length_N_in":4,"concentrated_force_kips":40,"distance_from_end_in":30}
def test_interior_cases():
 r=c.calculate(b());assert "interior" in r["web_local_yielding"]["case"];assert "interior" in r["web_local_crippling"]["case"]
def test_end_cases_have_lower_local_yielding_strength():
 a=c.calculate(b());x=b();x["distance_from_end_in"]=2;r=c.calculate(x);assert r["web_local_yielding"]["available_strength_kips"]<a["web_local_yielding"]["available_strength_kips"]
