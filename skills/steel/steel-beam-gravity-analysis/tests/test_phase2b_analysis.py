import importlib.util
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('phase2b_calc', ROOT/'calculator.py')
calc = importlib.util.module_from_spec(spec); spec.loader.exec_module(calc)


def base_simple(**extra):
    d = {
        'span_ft': 20,
        'support_condition': 'simple',
        'load_level': 'service',
        'dead_load_plf': 0,
        'live_load_plf': 0,
        'E_ksi': 29000,
        'Ix_in4': 1000,
    }
    d.update(extra)
    return d


def test_triangular_load_reactions_match_statics():
    # 0 -> 1200 plf over 20 ft: W=12 kip at x=2L/3.
    r = calc.calculate(base_simple(linear_loads=[{
        'w_start_plf': 0, 'w_end_plf': 1200,
        'x_start_ft': 0, 'x_end_ft': 20, 'category': 'dead'
    }]))
    rx = r['analysis_results']['dead_load']['support_reactions']
    assert abs(rx[0]['vertical_lb'] - 4000) < 2
    assert abs(rx[1]['vertical_lb'] - 8000) < 2


def test_trapezoidal_load_reactions_match_resultant_centroid():
    # 600 -> 1200 plf over 20 ft: W=18 kip, xbar=11.111 ft.
    r = calc.calculate(base_simple(linear_loads=[{
        'w_start_plf': 600, 'w_end_plf': 1200,
        'x_start_ft': 0, 'x_end_ft': 20, 'category': 'dead'
    }]))
    rx = r['analysis_results']['dead_load']['support_reactions']
    assert abs(rx[0]['vertical_lb'] - 8000) < 2
    assert abs(rx[1]['vertical_lb'] - 10000) < 2


def test_concentrated_moment_produces_equal_opposite_simple_span_reactions():
    r = calc.calculate(base_simple(concentrated_moments=[{
        'M_lb_ft': 12000, 'x_ft': 10, 'category': 'dead'
    }]))
    rx = r['analysis_results']['dead_load']['support_reactions']
    assert abs(abs(rx[0]['vertical_lb']) - 600) < 1
    assert abs(abs(rx[1]['vertical_lb']) - 600) < 1
    assert rx[0]['vertical_lb'] * rx[1]['vertical_lb'] < 0


def test_variable_ei_center_point_deflection_matches_castigliano():
    P = 10000.0; L = 240.0; E = 29000.0*1000
    I1, I2 = 1000.0, 500.0
    expected = P*L**3/(96*E)*(1/I1 + 1/I2)
    r = calc.calculate(base_simple(
        E_ksi=None, Ix_in4=None,
        stiffness_segments=[
            {'x_start_ft':0,'x_end_ft':10,'E_ksi':29000,'Ix_in4':I1},
            {'x_start_ft':10,'x_end_ft':20,'E_ksi':29000,'Ix_in4':I2},
        ],
        point_loads=[{'P_lb':P,'x_ft':10,'category':'live'}]
    ))
    delta = r['analysis_results']['live_load']['max_downward_deflection_in']
    assert abs(delta - expected) < 0.003


def test_support_settlement_causes_compatible_rigid_body_rotation_for_simple_beam():
    r = calc.calculate({
        'span_ft':20,
        'supports':[{'x_ft':0,'type':'pinned','settlement_in':0.0},
                    {'x_ft':20,'type':'roller','settlement_in':-0.5}],
        'load_level':'service','dead_load_plf':0,'live_load_plf':0,
        'E_ksi':29000,'Ix_in4':1000,
    })
    case = r['analysis_results']['dead_plus_live']
    assert max(abs(x['vertical_lb']) for x in case['support_reactions']) < 1e-3
    assert abs(case['max_downward_deflection_in'] - 0.5) < 0.005


def test_single_moving_point_load_moment_envelope_hits_midspan_PL_over_4():
    r = calc.calculate(base_simple(moving_loads=[{
        'name':'single axle','category':'live','step_ft':0.25,
        'axles':[{'P_lb':10000,'offset_ft':0.0}]
    }]))
    env = r['moving_load_envelope']
    assert abs(env['max_positive_moment_kip_ft'] - 50.0) < 0.15
    assert env['governing_positions']['max_positive_moment']['lead_x_ft'] == 10.0


def test_timoshenko_center_point_deflection_includes_shear_component():
    P=10000.0; L=240.0; E=29000.0*1000; I=1000.0; G=11200.0*1000; Av=20.0
    eb = P*L**3/(48*E*I)
    shear = P*L/(4*G*Av)
    r = calc.calculate(base_simple(
        point_loads=[{'P_lb':P,'x_ft':10,'category':'live'}],
        shear_deformation={'enabled':True,'G_ksi':11200,'Av_in2':Av}
    ))
    delta=r['analysis_results']['live_load']['max_downward_deflection_in']
    assert abs(delta-(eb+shear)) < 0.003
    assert delta > eb


def test_second_order_zero_axial_matches_first_order_and_compression_amplifies():
    inp=base_simple(point_loads=[{'P_lb':10000,'x_ft':10,'category':'live'}])
    first=calc.calculate(inp)['analysis_results']['live_load']['max_downward_deflection_in']
    zero=calc.calculate({**inp,'second_order':{'enabled':True,'axial_force_lb':0}})['analysis_results']['live_load']['max_downward_deflection_in']
    comp=calc.calculate({**inp,'second_order':{'enabled':True,'axial_force_lb':500000}})['analysis_results']['live_load']['max_downward_deflection_in']
    assert abs(zero-first) < 1e-6
    assert comp > first


def test_second_order_blocks_near_euler_instability_for_simple_span():
    E=29000*1000; I=1000; L=240
    pcr=math.pi**2*E*I/L**2
    r=calc.calculate(base_simple(second_order={'enabled':True,'axial_force_lb':0.99*pcr}))
    assert r['status']=='blocked'
    assert any('critical' in e.lower() or 'buckling' in e.lower() for e in r['validation']['errors'])


def test_saint_venant_torsion_cantilever_matches_TL_over_GJ():
    T=12000.0; L=120.0; G=11200*1000; J=10.0
    expected=T*L/(G*J)
    r=calc.calculate({
        'span_ft':10,'support_condition':'cantilever','load_level':'service',
        'dead_load_plf':0,'live_load_plf':0,'E_ksi':29000,'Ix_in4':1000,
        'torsion':{
            'enabled':True,'G_ksi':11200,'J_in4':J,
            'restraints':[0.0],
            'point_torques':[{'T_lb_in':T,'x_ft':10.0}]
        }
    })
    tor=r['torsion_analysis']
    assert tor['status']=='complete_saint_venant_torsion'
    assert abs(tor['max_abs_rotation_rad']-expected) < 1e-7
    assert abs(abs(tor['restraint_reactions'][0]['torque_lb_in'])-T) < 1e-3


def test_unified_demand_envelope_is_present():
    r=calc.calculate(base_simple(
        point_loads=[{'P_lb':5000,'x_ft':10,'category':'live'}],
        linear_loads=[{'w_start_plf':0,'w_end_plf':500,'x_start_ft':0,'x_end_ft':20,'category':'dead'}]
    ))
    env=r['demand_envelope']
    assert set(['max_positive_moment_kip_ft','min_negative_moment_kip_ft','max_abs_shear_kips','max_downward_deflection_in']).issubset(env)

def test_uniform_distributed_saint_venant_torque_cantilever():
    # Uniform torsional load t over fixed-free bar: theta(L)=t L^2/(2GJ), reaction=tL.
    t_per_ft=1200.0; L=120.0; G=11200*1000; J=10.0
    t_per_in=t_per_ft/12.0
    expected=t_per_in*L**2/(2*G*J)
    r=calc.calculate({
        'span_ft':10,'support_condition':'cantilever','load_level':'service',
        'dead_load_plf':0,'live_load_plf':0,'E_ksi':29000,'Ix_in4':1000,
        'torsion':{
            'enabled':True,'G_ksi':11200,'J_in4':J,'restraints':[0.0],
            'distributed_torques':[{'t_start_lb_in_per_ft':t_per_ft,'t_end_lb_in_per_ft':t_per_ft,'x_start_ft':0,'x_end_ft':10}]
        }
    })
    tor=r['torsion_analysis']
    assert abs(tor['max_abs_rotation_rad']-expected) < 1e-7
    assert abs(abs(tor['restraint_reactions'][0]['torque_lb_in'])-t_per_ft*10) < 1e-3
    assert abs(tor['max_abs_torque_lb_in']-t_per_ft*10) < 5

def test_demand_envelope_reports_governing_locations():
    r=calc.calculate({'span_ft':20,'support_condition':'simple','dead_load_plf':1000,'load_level':'factored','E_ksi':29000,'Ix_in4':1000})
    env=r['demand_envelope']
    assert abs(env['max_positive_moment_location_ft']-10.0)<0.5
    assert env['max_abs_shear_location_ft'] is not None
    assert env['max_positive_moment_case'] in {'dead_load','dead_plus_live'}
