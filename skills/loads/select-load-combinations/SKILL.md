---
name: select-load-combinations
category: structural-loads
level: executable
description: Select and evaluate bounded ASCE 7 style ASD/LRFD load combinations for scalar structural effects under engineer supervision.
---

# select-load-combinations

Use this skill to select and evaluate common structural load combinations in a controlled, code-aware way before member or system design.

This skill does not replace the governing code. It forces the AI to identify the design method, load standard, load types, load status, and objective before selecting combinations. In v0.3, this skill includes a bounded `calculator.py` that evaluates common ASCE 7-16/ASCE 7-22 style ASD and LRFD scalar combinations for D, L, Lr, S, R, W, and E.

## Trigger

Use this skill when the user asks:

- which load factor to use
- whether ASD or LRFD applies
- what load combination governs
- how to combine dead, live, roof live, snow, rain, wind, or seismic effects
- to convert service-level loads into candidate ASD/LRFD design demands
- to evaluate positive/negative wind or seismic scalar effects

## Do not use this skill for

- final sealed design
- special seismic load effects or overstrength combinations
- flood, soil, self-straining, crane, construction, ponding, ice, or local amendment provisions
- automatic load path determination
- automatic live-load companion reduction eligibility
- multi-axis envelope generation
- serviceability limit checks beyond identifying that service-level combinations/criteria are needed

If any of those are needed, stop and say this skill version does not support that scope yet.

## Ground rules

- Do not select combinations until the design method is known: ASD or LRFD.
- Do not mix ASD and LRFD.
- Do not factor loads that are already factored unless the user explicitly asks for a documented special case.
- Do not treat service-level reactions from software as factored unless stated.
- Do not ignore companion loads without explaining why they are excluded.
- Do not invent wind/seismic direction or sign convention.
- State the load standard and edition if known.
- If the exact edition is unknown, label the result as blocked or preliminary and request confirmation.
- Always disclose unsupported load types.

## Required inputs

- `code_family`: currently only `ASCE 7` is supported
- `code_edition`: currently `ASCE 7-16` and `ASCE 7-22` are explicitly supported as preliminary basis
- `design_method`: `ASD` or `LRFD`
- `load_level`: `service` or `factored`
- `loads`: numeric scalar load effects using supported keys: `D`, `L`, `Lr`, `S`, `R`, `W`, `E`
- `objective`: strength, allowable stress, uplift, overturning, drift/serviceability context, etc.

## Stop conditions

Stop and ask if:

- ASD/LRFD method is unknown
- load status is unknown: service-level vs factored
- load magnitudes are missing or nonnumeric
- load types are unclear
- unsupported load cases are present
- wind/seismic directionality or sign matters and is not defined
- the user asks for governing combination but gives only a final software envelope with no combination basis
- code edition/local amendments materially affect the answer

## Process

1. Identify the design objective: strength, allowable stress, serviceability, drift, overturning, uplift, or stability.
2. Confirm design method: ASD or LRFD.
3. Confirm load standard and code edition.
4. List all load types present.
5. Confirm all load magnitudes and whether they are service-level or factored.
6. Run `validator.py`.
7. If validation is blocked, return the missing/unsupported items and do not calculate.
8. If loads are already factored, block automatic refactoring.
9. Run `calculator.py` only for supported service-level D, L, Lr, S, R, W, and E scalar effects.
10. Generate relevant candidate combinations.
11. Evaluate positive and negative wind/seismic direction variants where applicable.
12. Identify governing positive, governing negative, and governing absolute scalar effect.
13. State exclusions, limitations, and engineer review notes.

## Output format

```text
Design method: [ASD/LRFD]
Load standard: [ASCE 7 edition or preliminary basis]
Load status: [service/factored/unknown]
Load types considered: [list]
Objective: [strength/serviceability/uplift/etc.]

Validation:
[ready/blocked with missing inputs, unsupported loads, warnings]

Candidate combinations:
1. [name]: [expression] = [value]
2. [name]: [expression] = [value]

Governing scalar effects:
- Governing positive: [combo] = [value]
- Governing negative: [combo] = [value]
- Governing absolute: [combo] = [value]

Not checked / requires confirmation:
- [item]

Engineer review note:
This is a preliminary juniorSE output and must be reviewed against the governing code, project criteria, sign conventions, and local amendments.
```

## Guardrails

- If loads are already factored, do not apply factors again.
- If checking serviceability, use service-level combinations/criteria rather than strength factors unless the task explicitly requires otherwise.
- If wind or seismic creates positive and negative effects, evaluate both signs for scalar effects and ask the engineer to confirm sign convention.
- If both ASD and LRFD results are requested, keep them in separate sections.
- Do not claim that this skill handles special seismic combinations, overstrength, local amendments, or unsupported load cases.
- Do not claim a final governing result if unsupported loads are present.

## Definition of done

The skill is complete when:

- inputs are summarized
- method is clear
- load status is clear
- unsupported loads are disclosed
- candidate combinations are shown or blocked with reasons
- governing positive/negative/absolute scalar effects are identified when applicable
- excluded provisions are stated
- downstream design skill can use the selected demand without ambiguity
- engineer review is explicitly required

## Handoffs

- Use `assumption-guardrails` before selecting combinations if inputs are incomplete.
- Use material/member design skills after determining demand.
- Use `calculation-qaqc-review` before final output if numerical demand is calculated.

## Implementation files

This juniorSE skill includes machine-checkable support files:

- `rules.yaml` for required inputs, supported load cases, stop conditions, guardrails, calculator scope, and definition of done.
- `validator.py` for input validation and stop-condition checks.
- `calculator.py` for bounded scalar ASD/LRFD candidate combination evaluation.
- `examples/` for passing and blocked scenarios.
- `tests/` for automated validation and calculator behavior.
