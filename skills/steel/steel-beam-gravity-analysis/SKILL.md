---
name: steel-beam-gravity-analysis
category: structural-steel
level: executable
description: Calculate simple-span steel beam gravity analysis demands and service deflections for uniform dead and live loads under engineer supervision.
---

# steel-beam-gravity-analysis

Use this skill to calculate bounded beam-level analysis results for a simply supported beam with uniform gravity loads.

This skill computes demand and serviceability quantities only. It does not determine AISC member capacity, select a steel shape, verify lateral-torsional buckling capacity, classify compactness, or approve a final design.

## Trigger

Use this skill when the user asks for:

- reactions for a simple steel beam
- maximum shear or moment for a uniform gravity load
- live-load, dead-load, or total-load deflection for a simple span
- the analysis-demand portion of a steel gravity beam check

## Do not use when

Do not use this skill for:

- continuous beams
- cantilevers
- point loads or partial-length loads
- composite beam action
- lateral-system member design
- steel capacity/pass-fail checks without the companion check skill
- final stamped design

## Required inputs

- span_ft
- dead_load_plf
- live_load_plf
- load_level: service or factored
- support_condition: simply supported

## Required for deflection

- E_ksi
- Ix_in4

If `E_ksi` and `Ix_in4` are not provided, the skill may calculate reactions, shear, and moment, but it must report deflection as incomplete.

## Default serviceability criteria

When checking service deflection for this skill, use the following project standard unless the user provides different criteria:

- Live Load deflection limit: **L/240**
- Dead + Live Load deflection limit: **L/360**

Do not silently swap these limits. If a different project criterion is given, report both the provided criterion and this default so the reviewer can see the change.

## Process

1. Confirm the beam model is within scope: simply supported, uniform gravity loads.
2. Confirm loads are service-level or factored.
3. Calculate reactions, maximum shear, and maximum moment using the provided load cases.
4. If section stiffness is provided, calculate elastic deflections separately for dead load, live load, and total dead + live load.
5. Compare live-load deflection to L/240.
6. Compare total dead + live deflection to L/360.
7. Report whether each serviceability check passes, fails, or is incomplete.
8. State that AISC strength/capacity checks are not performed by this analysis skill.
9. Include QA/QC notes and engineer-review items.

## Equations for current scope

For a simply supported beam with uniform load:

```text
R = wL / 2
Vmax = wL / 2
Mmax = wL^2 / 8
Delta_max = 5wL^4 / 384EI
```

Use consistent units. For deflection, convert span to inches, load to lb/in, E to psi, and Ix to in^4.

## Guardrails

- Do not use factored loads for serviceability deflection checks unless the user explicitly asks for factored-load deflection and it is labeled accordingly.
- Do not claim member adequacy from analysis demand alone.
- Do not proceed for non-simple-span or non-uniform load patterns.
- Do not invent E or Ix. If stiffness data is missing, mark deflection incomplete.

## Definition of done

This skill is complete only when the output includes:

- input summary
- scope confirmation
- reactions
- maximum shear
- maximum moment
- deflection results or a clear deflection-incomplete note
- LL deflection compared to L/240 when stiffness is available
- D+L deflection compared to L/360 when stiffness is available
- QA/QC notes
- engineer-review notes

## Implementation files

This juniorSE skill includes:

- `rules.yaml`
- `validator.py`
- `calculator.py`
- `examples/`
- `tests/`
