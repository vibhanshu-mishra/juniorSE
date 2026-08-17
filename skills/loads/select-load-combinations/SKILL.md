---
name: select-load-combinations
category: structural-loads
description: Select and explain structural load combinations for ASD or LRFD workflows. Use when the task requires factored demand, allowable stress demand, or comparison of governing load cases.
---

# select-load-combinations

Use this skill to select load combinations in a controlled, code-aware way before member/system design.

This skill does not replace the governing code. It forces the AI to identify the design method, load standard, load types, and load status before selecting combinations.

## Trigger

Use this skill when the user asks:

- which load factor to use
- whether ASD or LRFD applies
- what load combination governs
- how to combine dead, live, roof live, snow, wind, seismic, rain, or other loads
- to check a member where loads are service-level and design demand must be generated

## Ground rules

- Do not select combinations until the design method is known: ASD or LRFD.
- Do not mix ASD and LRFD.
- Do not factor loads that are already factored without confirmation.
- Do not treat service-level reactions from software as factored unless stated.
- Do not ignore companion loads without explaining why they are excluded.
- State the load standard and edition if known.
- If the exact edition is unknown, label the result as preliminary and request confirmation.

## Required inputs

- design method: ASD or LRFD
- applicable load standard/code edition
- load types present: D, L, Lr, S, R, W, E, H, F, etc.
- load magnitudes
- whether loads are service-level or already factored
- member/system being checked
- whether uplift, overturning, drift, or stability is involved
- strength vs serviceability objective

## Stop conditions

Stop and ask if:

- ASD/LRFD method is unknown
- load status is unknown: service-level vs factored
- load types are unclear
- wind/seismic directionality or sign matters and is not defined
- the user asks for governing combination but gives only final software envelope with no combination basis
- code edition/local amendments materially affect the answer

## Process

1. Identify design objective: strength, allowable stress, serviceability, drift, overturning, uplift, or stability.
2. Confirm design method: ASD or LRFD.
3. Confirm load standard/code edition.
4. List all load types present.
5. Confirm load magnitudes and whether they are service-level or factored.
6. Generate only the relevant candidate combinations.
7. Calculate combined demand for each candidate combination.
8. Identify the governing combination for the requested effect.
9. State excluded combinations and why they were not considered.
10. Flag any missing data that could change the governing result.

## Output format

```text
Design method: [ASD/LRFD]
Load standard: [standard/edition or preliminary basis]
Load status: [service-level/factored/unknown]
Load types considered: [list]
Objective: [strength/serviceability/etc.]

Candidate combinations:
1. [combo] = [calculation]
2. [combo] = [calculation]

Governing combination:
[combo] controls for [effect] with demand = [value]

Not checked / requires confirmation:
- [item]
```

## Guardrails

- If loads are already factored, do not apply factors again.
- If checking serviceability, use service-level combinations/criteria rather than strength factors unless the task explicitly requires otherwise.
- If wind or seismic creates positive and negative effects, evaluate sign/direction where relevant.
- If both ASD and LRFD results are requested, keep them in separate sections.

## Definition of done

The skill is complete when:

- the method is clear
- load status is clear
- candidate combinations are shown
- governing combination is identified for the requested effect
- exclusions and missing inputs are disclosed
- downstream design skill can use the selected demand without ambiguity

## Handoffs

- Use `assumption-guardrails` before selecting combinations if inputs are incomplete.
- Use material/member design skills after determining demand.
- Use `calculation-qaqc-review` before final output if numerical demand is calculated.
