import importlib.util,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));s=importlib.util.spec_from_file_location("c",ROOT/"calculator.py");c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
def b():return {"design_method":"LRFD","E_ksi":29000,"Fy_ksi":50,"Sx_in3":80,"Zx_in3":90,"ry_in":2,"rts_in":2.3,"J_in4":0.45,"ho_in":11,"Lb_ft":5,"Cb":1,"flange_classification":"compact","web_classification":"compact","flange_lambda":6.0,"flange_lambda_p":9.15,"flange_lambda_r":24.08,"h_in":11,"tw_in":0.4,"required_moment_kip_ft":200}
def test_f2_compact():
 r=c.calculate(b());assert r["chapter_f_route"]=="F2";assert r["status"]=="complete"
def test_f3_noncompact_flange():
 x=b();x.update({"flange_classification":"noncompact","flange_lambda":15});r=c.calculate(x);assert r["chapter_f_route"]=="F3";assert "compression_flange_local_buckling" in r["limit_state_nominal_strengths_kip_ft"]
def test_f3_slender_flange():
 x=b();x.update({"flange_classification":"slender","flange_lambda":30});r=c.calculate(x);assert r["chapter_f_route"]=="F3";assert r["nominal_strength_Mn_kip_ft"]<50*90/12
def test_noncompact_web_requires_f4_inputs_when_not_provided():
 x=b();x["web_classification"]="noncompact";r=c.calculate(x);assert r["status"]=="blocked";assert "bf_in" in r["validation"]["missing_inputs"]
