---
name: steel-beam-gravity-check
category: structural-steel
description: Check or preliminarily size a structural steel beam under gravity loading. Use for bounded steel beam flexure, shear, deflection, and lateral-bracing review under engineer supervision.
---

# steel-beam-gravity-check

Use this skill to check or preliminarily size a structural steel beam under gravity loading.

This skill is for bounded beam-level work. It is not a complete building design, lateral-system design, connection design, or final stamped calculation.

## Trigger

Use this skill when the user asks:

- “Does this steel beam work?”
- “What size steel beam do I need?”
- “Check this W-shape for gravity load.”
- “Why is this beam failing?”
- “Prepare a preliminary beam calculation.”

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
- Use `select-load-combinations` when service-level loads must be factored or ASD demand must be developed.
- Use `calculation-qaqc-review` before final output.
- Do not assume continuous lateral bracing unless stated.
- Do not ignore lateral-torsional buckling applicability.
- Do not mix LRFD demand with ASD capacity.
- Do not produce a clean pass/fail if critical inputs are missing.

## Required inputs

- design objective: check existing beam or size new beam
- code/design basis, such as AISC 360 edition, if known
- design method: ASD or LRFD
- steel grade/specification
- beam section or candidate sections, unless sizing
- span
- support condition
- load types and magnitudes
- load status: service-level or factored
- load distribution: uniform, point load, partial uniform, etc.
- unbraced length or lateral bracing condition
- deflection criteria
- whether beam is composite/non-composite
- whether concentrated loads, bearing, web crippling, or web yielding may apply

## Optional inputs

- camber requirements
- vibration sensitivity
- construction-stage loading
- live-load reduction basis
- fireproofing or architectural depth limits
- connection eccentricity or end reaction requirements

## Stop conditions

Stop before final calculation if:

- design method is unknown
- steel grade is unknown
- span/support condition is unknown
- loads or load status are unknown
- unbraced length/bracing condition is unknown for flexural stability
- deflection criteria are required but missing
- the section properties are not available
- the beam may be composite but composite assumptions are not defined

If the user wants a quick preliminary check, proceed only with clearly labeled preliminary assumptions.

## Process

1. **Classify the task.** Check existing section, preliminary sizing, compare options, or diagnose failure.
2. **Summarize inputs.** List provided, derived, assumed, and missing values.
3. **Confirm design basis.** State code/design basis and ASD/LRFD method.
4. **Confirm load basis.** Determine whether loads are service-level or factored.
5. **Select/load combinations.** Use `select-load-combinations` if required.
6. **Analyze demand.** Determine maximum moment, shear, and reactions using the appropriate beam model.
7. **Check flexure.** Evaluate available flexural strength using the correct design method and bracing condition. Consider yielding and lateral-torsional buckling applicability.
8. **Check shear.** Evaluate shear demand versus available shear strength.
9. **Check serviceability.** Evaluate deflection against stated criteria using service-level loads.
10. **Check concentrated-load effects if applicable.** Flag web yielding, web crippling, bearing, stiffener, or local effects when concentrated loads/reactions are present.
11. **Identify governing result.** State which check controls.
12. **Run QA/QC.** Use `calculation-qaqc-review`.
13. **Hand off.** State engineer-review items.

## Minimum checks

For a normal non-composite gravity beam, check or explicitly exclude:

- flexure
- shear
- lateral-torsional buckling applicability
- deflection/serviceability
- reactions
- concentrated-load/web-local effects, when applicable
- bearing/support assumptions

## Output format

```text
Task: [check / sizing / comparison / diagnosis]
Status: [complete / preliminary / incomplete]

Known inputs:
- ...

Missing inputs / assumptions:
- ...

Design basis:
- Material/design standard: ...
- Method: ASD/LRFD
- Load basis: service-level/factored

Demand:
- Moment: ...
- Shear: ...
- Reactions: ...

Checks:
- Flexure: ...
- Shear: ...
- LTB/bracing: ...
- Deflection: ...
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
- If checking deflection, use service-level load cases and stated criteria.
- If connection/support details could affect the beam model, flag them.

## Definition of done

The skill is complete only when:

- inputs and assumptions are visible
- design method is consistent
- load combination basis is clear
- moment, shear, and deflection paths are shown
- flexure, shear, LTB applicability, and serviceability are checked or explicitly excluded
- governing result is identified
- QA/QC review is included
- engineer-review items are listed


## Implementation files

This juniorSE skill includes machine-checkable support files:

- `rules.yaml` for required inputs, stop conditions, guardrails, and definition of done.
- `validator.py` for input validation and stop-condition checks.
- `examples/` for passing and blocked scenarios.
- `tests/` for automated validation behavior.
- `calculator.py` for the current bounded executable starter calculation scope.
