import importlib.util,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sv=importlib.util.spec_from_file_location("v",ROOT/"validator.py");v=importlib.util.module_from_spec(sv);sv.loader.exec_module(v);sc=importlib.util.spec_from_file_location("c",ROOT/"calculator.py");c=importlib.util.module_from_spec(sc);sc.loader.exec_module(c)
BASE={"code_family":"AISC","code_edition":"AISC 360-16","design_method":"LRFD","span_ft":20,"dead_load_plf":1000,"live_load_plf":2000,"strength_uniform_load_plf":4400,"load_level":"service","support_condition":"simply_supported","bracing_condition":"Lb provided","steel_grade":"A992","member_section":"example W/I","composite_status":"non-composite","E_ksi":29000,"Fy_ksi":50,"Ix_in4":1000,"Sx_in3":80,"Zx_in3":90,"d_in":12,"h_in":11,"tw_in":0.4,"bf_in":6.5,"tf_in":0.4,"ry_in":2,"rts_in":2.3,"J_in4":0.45,"ho_in":11,"Lb_ft":5,"Cb":1}
def test_ready():assert v.validate(BASE)["status"]=="ready"
def test_orchestrates_phase1():
 r=c.calculate(BASE);assert r["status"]=="complete_phase_1_bounded_check";assert r["strength_checks"]["chapter_f_flexure"]["status"]=="complete";assert r["strength_checks"]["chapter_g_shear"]["status"]=="complete"
def test_serviceability_limits():
 r=c.calculate(BASE)["serviceability"];assert r["live_load_limit_in"]==1.0;assert round(r["dead_plus_live_limit_in"],6)==round(240/360,6)
def test_noncompact_flange_is_not_blocked():
 x=dict(BASE);x.update({"bf_in":14,"tf_in":0.4});r=c.calculate(x);assert r["strength_checks"]["chapter_f_flexure"]["chapter_f_route"]=="F3"
def test_slender_web_routes_to_f5():
 x=dict(BASE);x.update({"h_in":100,"tw_in":0.4});r=c.calculate(x);assert r["strength_checks"]["chapter_f_flexure"]["chapter_f_route"]=="F5";assert r["strength_checks"]["chapter_f_flexure"]["status"]=="complete"
def test_optional_web_local_checks_run():
 x=dict(BASE);x.update({"concentrated_force_kips":40,"bearing_length_N_in":4,"distance_from_end_in":30,"k_in":1.0});r=c.calculate(x);assert r["strength_checks"]["chapter_j10_web_local"]["status"]=="complete"
