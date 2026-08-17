import importlib.util,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R));s=importlib.util.spec_from_file_location("c",R/"calculator.py");c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
def test_stocky_web_cv_one():
 r=c.calculate({"design_method":"LRFD","E_ksi":29000,"Fy_ksi":50,"h_in":12,"tw_in":0.4,"required_shear_kips":40});assert r["Cv1"]==1.0
def test_slenderer_web_calculates_cv_below_one():
 r=c.calculate({"design_method":"LRFD","E_ksi":29000,"Fy_ksi":50,"h_in":40,"tw_in":0.2,"required_shear_kips":40});assert 0<r["Cv1"]<1
