---
name: steel-beam-gravity-check
category: structural-steel
level: executable
description: Perform a bounded steel gravity beam check under engineer supervision by combining beam analysis, serviceability checks, and explicit placeholders for AISC strength checks not yet implemented.
---

# steel-beam-gravity-check

Use this skill to check or preliminarily size a structural steel beam under gravity loading.

This skill is intentionally split from `steel-beam-gravity-analysis`:

- `steel-beam-gravity-analysis` computes simple-span uniform-load reactions, shear, moment, and deflections.
- `steel-beam-gravity-check` performs the review/check wrapper around those results, including serviceability pass/fail and strength-check readiness.

Current executable scope performs analysis-demand and serviceability checks only. It does not yet perform full AISC flexural strength, shear strength, compactness, lateral-torsional buckling strength, or web-local strength checks.

## Trigger

Use this skill when the user asks:

- “Does this steel beam work?”
- “Check this W-shape for gravity load.”
- “Prepare a preliminary gravity beam calculation.”
- “Check beam deflection for live load and total load.”
- “What is still missing before this beam can be approved?”

## Do not use when

Do not use this skill for:

- concrete, wood, masonry, aluminum, or cold-formed steel members
- lateral frame design
- seismic/wind force-resisting system design
- connection design
- composite beam design unless a separate composite-beam skill is available
- final construction approval

## Ground rules

- Use `structural-response-protocol` first.
- Use `assumption-guardrails` before calculating.
- Use `steel-beam-gravity-analysis` for simple-span uniform-load mechanics.
- Use `select-load-combinations` when service-level loads must be converted to ASD/LRFD design demand.
- Use `calculation-qaqc-review` before final output.
- Do not assume continuous lateral bracing unless stated.
- Do not ignore lateral-torsional buckling applicability.
- Do not mix LRFD demand with ASD capacity.
- Do not produce a clean AISC pass/fail until AISC capacity checks are actually performed.

## Required inputs

- design objective: check existing beam or size new beam
- code/design basis, such as AISC 360 edition, if known
- design method: ASD or LRFD
- steel grade/specification
- beam section or candidate sections, unless sizing
- span_ft
- support condition
- dead_load_plf
- live_load_plf
- load_level: service or factored
- load distribution: uniform for current executable scope
- unbraced length or lateral bracing condition
- E_ksi and Ix_in4 for deflection/serviceability
- whether beam is composite/non-composite
- whether concentrated loads, bearing, web crippling, or web yielding may apply

## Default serviceability criteria

Per current juniorSE project direction, use these defaults unless the user gives project-specific criteria:

- Live Load deflection: **L/240**
- Dead + Live Load deflection: **L/360**

These are intentionally written into the skill. Do not silently reverse them or replace them with common office defaults.

## Stop conditions

Stop before a full beam check if:

- design method is unknown
- steel grade is unknown
- span/support condition is unknown
- loads or load status are unknown
- unbraced length/bracing condition is unknown for flexural stability
- E and Ix are missing for serviceability
- the section properties needed for strength checks are not available
- the beam may be composite but composite assumptions are not defined

If enough data exists for analysis but not strength design, return an analysis/serviceability-only result and clearly state that AISC strength checks are incomplete.

## Process

1. **Classify the task.** Check existing section, preliminary sizing, compare options, or diagnose failure.
2. **Summarize inputs.** List provided, derived, assumed, and missing values.
3. **Confirm design basis.** State code/design basis and ASD/LRFD method.
4. **Confirm load basis.** Determine whether loads are service-level or factored.
5. **Run analysis.** Use `steel-beam-gravity-analysis` for simple-span uniform-load reactions, shear, moment, and deflections.
6. **Check serviceability.** Compare LL deflection to L/240 and D+L deflection to L/360.
7. **Check strength readiness.** Determine whether enough inputs exist for AISC flexure, shear, LTB, compactness, and local checks.
8. **Do not fake strength.** If AISC checks are not implemented or inputs are missing, mark them as incomplete.
9. **Identify governing result.** For current executable scope, governing result may be serviceability or incomplete strength readiness.
10. **Run QA/QC.** Use `calculation-qaqc-review`.
11. **Hand off.** State engineer-review items.

## Current executable output

The current calculator may produce:

- analysis results for D, L, and D+L
- LL deflection ratio against L/240
- D+L deflection ratio against L/360
- serviceability pass/fail status
- strength-check readiness status
- missing strength inputs
- QA/QC notes

## Strength checks not yet implemented

The skill must explicitly state that the following are not yet executable in this version:

- AISC flexural capacity
- AISC shear capacity
- lateral-torsional buckling strength
- section compactness/local buckling classification
- web yielding/web crippling
- concentrated-load checks
- connection/support bearing checks

## Output format

```text
Task: [check / sizing / comparison / diagnosis]
Status: [complete_serviceability_only / preliminary / incomplete]

Known inputs:
- ...

Missing inputs / assumptions:
- ...

Design basis:
- Material/design standard: ...
- Method: ASD/LRFD
- Load basis: service-level/factored

Analysis demand:
- Reactions: ...
- Moment: ...
- Shear: ...

Serviceability:
- LL deflection vs L/240: ...
- D+L deflection vs L/360: ...

Strength checks:
- Flexure: incomplete/not implemented or checked by external/validated module
- Shear: incomplete/not implemented or checked by external/validated module
- LTB/bracing: ...
- Local/concentrated load effects: ...

Governing result:
- ...

QA/QC review:
- ...

Engineer review notes:
- ...
```

## Guardrails

- If the beam is not laterally braced, do not use fully braced flexural capacity.
- If bracing is unknown, do not silently assume it.
- If loads are service-level, select the proper strength or ASD combination before strength checks.
- If loads are factored, do not factor them again.
- If checking deflection, use service-level load cases and compare LL to L/240 and D+L to L/360 unless project criteria override.
- If connection/support details could affect the beam model, flag them.

## Definition of done

The skill is complete only when:

- inputs and assumptions are visible
- design method is consistent
- load-combination basis is clear
- analysis demand is shown or the analysis skill has been referenced
- LL deflection is compared to L/240 when stiffness is available
- D+L deflection is compared to L/360 when stiffness is available
- AISC strength checks are either performed by a future validated module or explicitly marked incomplete
- governing current-scope result is identified
- QA/QC review is included
- engineer-review items are listed

## Implementation files

This juniorSE skill includes machine-checkable support files:

- `rules.yaml` for required inputs, stop conditions, guardrails, and definition of done.
- `validator.py` for input validation and stop-condition checks.
- `calculator.py` for current bounded serviceability-check execution.
- `examples/` for passing and blocked scenarios.
- `tests/` for automated behavior.
