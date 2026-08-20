import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = load_module("validator")
calculator = load_module("calculator")


def base(edition="ASCE 7-22", method="LRFD", loads=None, objective="strength", **extra):
    data = {
        "code_family": "ASCE 7",
        "code_edition": edition,
        "design_method": method,
        "load_level": "service",
        "loads": loads or {"D": 1.0},
        "objective": objective,
    }
    data.update(extra)
    return data


def combo_by_section(result, section_id):
    return [c for c in result["candidate_combinations"] if c.get("section_id") == section_id]


def test_716_lrfd_basic_keeps_legacy_snow_factor_in_combo_2():
    result = calculator.select_combinations(base("ASCE 7-16", "LRFD", {"D": 1.0, "L": 2.0, "S": 3.0}))
    c2 = combo_by_section(result, "2.3.1-2")
    assert c2
    assert any(abs(c["factors"].get("S", 0) - 0.5) < 1e-12 for c in c2)


def test_722_lrfd_basic_uses_03_snow_companion_in_combo_2():
    result = calculator.select_combinations(base("ASCE 7-22", "LRFD", {"D": 1.0, "L": 2.0, "S": 3.0}))
    c2 = combo_by_section(result, "2.3.1-2a")
    assert c2
    assert any(abs(c["factors"].get("S", 0) - 0.3) < 1e-12 for c in c2)


def test_722_lrfd_basic_uses_10_snow_as_principal_roof_load():
    result = calculator.select_combinations(base("ASCE 7-22", "LRFD", {"D": 1.0, "S": 3.0}))
    c3 = combo_by_section(result, "2.3.1-3a")
    assert c3
    assert any(abs(c["factors"].get("S", 0) - 1.0) < 1e-12 for c in c3)


def test_fluid_load_follows_dead_load_factor_in_722_basic_strength_combos():
    result = calculator.select_combinations(base("ASCE 7-22", "LRFD", {"D": 1.0, "F": 2.0, "L": 1.0}))
    c1 = combo_by_section(result, "2.3.1-1a")[0]
    c2 = combo_by_section(result, "2.3.1-2a")[0]
    assert c1["factors"]["F"] == c1["factors"]["D"] == 1.4
    assert c2["factors"]["F"] == c2["factors"]["D"] == 1.2


def test_h_requires_directionality_classification():
    result = validator.validate(base("ASCE 7-22", "LRFD", {"D": 1.0, "H": 2.0}))
    assert result["status"] == "blocked"
    assert "h_effect" in result["missing_inputs"]


def test_722_strength_h_adds_with_16_and_permanent_resisting_uses_09():
    adding = calculator.select_combinations(base("ASCE 7-22", "LRFD", {"D": 1.0, "H": 2.0}, h_effect="adds"))
    assert any(abs(c["factors"].get("H", 0) - 1.6) < 1e-12 for c in adding["candidate_combinations"])
    resisting = calculator.select_combinations(base("ASCE 7-22", "LRFD", {"D": 1.0, "H": 2.0}, h_effect="resists", h_is_permanent=True))
    assert any(abs(c["factors"].get("H", 0) - 0.9) < 1e-12 for c in resisting["candidate_combinations"])


def test_722_asd_h_adds_with_10_and_permanent_resisting_uses_06():
    adding = calculator.select_combinations(base("ASCE 7-22", "ASD", {"D": 1.0, "H": 2.0}, objective="allowable_stress", h_effect="adds"))
    assert any(abs(c["factors"].get("H", 0) - 1.0) < 1e-12 for c in adding["candidate_combinations"])
    resisting = calculator.select_combinations(base("ASCE 7-22", "ASD", {"D": 1.0, "H": 2.0}, objective="allowable_stress", h_effect="resists", h_is_permanent=True))
    assert any(abs(c["factors"].get("H", 0) - 0.6) < 1e-12 for c in resisting["candidate_combinations"])


def test_722_tornado_wt_is_supported_as_wind_family_and_directional():
    result = calculator.select_combinations(base("ASCE 7-22", "LRFD", {"D": 1.0, "WT": 5.0}))
    names = {c["name"] for c in result["candidate_combinations"]}
    assert any("WT+" in name for name in names)
    assert any("WT-" in name for name in names)


def test_716_rejects_wt_as_edition_incompatible():
    result = validator.validate(base("ASCE 7-16", "LRFD", {"D": 1.0, "WT": 5.0}))
    assert result["status"] == "blocked"
    assert "WT" in result["edition_incompatible_load_cases"]


def test_722_seismic_accepts_resolved_ev_eh_and_generates_section_236_combos():
    result = calculator.select_combinations(base("ASCE 7-22", "LRFD", {"D": 10.0, "L": 3.0, "S": 2.0, "Ev": 1.0, "Eh": 4.0}))
    assert result["status"] == "complete_preliminary"
    assert combo_by_section(result, "2.3.6")


def test_722_seismic_blocks_legacy_scalar_e_unless_marked_resolved_legacy():
    result = validator.validate(base("ASCE 7-22", "LRFD", {"D": 10.0, "E": 4.0}))
    assert result["status"] == "blocked"
    assert "seismic_effect_definition" in result["missing_inputs"]


def test_serviceability_objective_routes_outside_chapter2_strength_selector():
    result = calculator.select_combinations(base("ASCE 7-22", "LRFD", {"D": 1.0, "L": 1.0}, objective="serviceability"))
    assert result["status"] == "routed"
    assert result["route"] == "serviceability"


def test_special_chapter2_families_are_recognized_not_called_unsupported():
    result = validator.validate(base("ASCE 7-22", "LRFD", {"D": 1.0, "Fa": 2.0}, chapter2_family="flood"))
    assert "Fa" not in result.get("unsupported_load_cases", [])
    assert result["status"] == "blocked"
    assert "resolved_special_combinations" in result["missing_inputs"]


def test_water_in_soil_family_is_722_only():
    result16 = validator.validate(base("ASCE 7-16", "LRFD", {"D": 1.0, "Hw": 2.0}, chapter2_family="water_in_soil"))
    assert result16["status"] == "blocked"
    assert "water_in_soil" in result16["edition_incompatible_families"]
    result22 = validator.validate(base("ASCE 7-22", "LRFD", {"D": 1.0, "Hw": 2.0}, chapter2_family="water_in_soil"))
    assert "water_in_soil" not in result22["edition_incompatible_families"]


def test_rules_metadata_is_exposed_in_result():
    result = calculator.select_combinations(base("ASCE 7-22", "LRFD", {"D": 1.0, "L": 1.0}))
    assert result["ruleset"]["edition"] == "ASCE 7-22"
    assert "2.3.1" in result["ruleset"]["implemented_sections"]
