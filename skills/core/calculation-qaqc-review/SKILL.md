---
name: calculation-qaqc-review
category: structural-core
description: Self-review structural calculations before handing them to a supervising engineer. Use after any numerical structural calculation or code-based design check.
---

# calculation-qaqc-review

Use this skill as the final internal review before presenting a structural calculation.

The goal is to catch missing assumptions, unit errors, method mismatches, skipped limit states, and overconfident conclusions.

## Trigger

Use this skill after:

- member design/check calculations
- load combination calculations
- wind or seismic calculations
- deflection or drift checks
- footing or foundation checks
- calculation package preparation
- review of another calculation

## Ground rules

- Do not finalize a numerical answer until QA/QC is complete.
- The QA/QC section must be visible in the response.
- If a critical issue is found, revise the answer or downgrade the conclusion before presenting it.
- Do not bury failed checks.
- Do not present a pass/fail if inputs remain preliminary or incomplete.

## QA/QC checklist

### 1. Input check

Verify:

- all critical inputs are provided or clearly assumed
- assumptions are labeled preliminary when applicable
- geometry, material, and loads match the task
- service-level vs factored load status is clear

### 2. Code/design basis check

Verify:

- code family and edition are stated or marked preliminary
- ASD/LRFD method is consistent
- load standard and material design standard are not mixed incorrectly
- local amendments or project criteria are not silently ignored when relevant

### 3. Unit check

Verify:

- length units are consistent
- force units are consistent
- stress units are consistent
- section properties use compatible units
- conversions are shown where they affect the result

### 4. Demand check

Verify:

- load combination is appropriate
- demand equations match support/loading assumptions
- signs/directions are handled where relevant
- tributary area/width is clear if used

### 5. Capacity/limit-state check

Verify:

- all relevant limit states are checked or explicitly excluded
- strength reduction or safety factors match the design method
- stability effects are considered where relevant
- governing limit state is identified

### 6. Serviceability check

Verify:

- deflection, drift, vibration, or crack control is checked when relevant
- criteria are stated
- service load basis is not confused with strength load basis

### 7. Reasonableness check

Verify:

- result magnitude is plausible
- demand/capacity ratio is interpreted correctly
- conclusion follows from the numbers
- no intermediate rounding changes the conclusion

### 8. Handoff check

Verify:

- engineer-review notes are included
- unresolved assumptions are listed
- final design/construction approval is not implied

## Output format

```text
QA/QC review:
- Inputs: [pass / issue]
- Code/design basis: [pass / issue]
- Units: [pass / issue]
- Demand: [pass / issue]
- Capacity/limit states: [pass / issue]
- Serviceability: [pass / issue / not applicable]
- Reasonableness: [pass / issue]
- Engineer review items: [list]
```

## Failure handling

If QA/QC finds a problem:

1. State the issue.
2. Correct the calculation if possible.
3. If not possible, stop and request missing information.
4. Downgrade the conclusion to preliminary/incomplete.

## Definition of done

The calculation is ready for handoff only when:

- QA/QC has been performed
- issues are corrected or disclosed
- conclusion is bounded
- engineer-review items are visible
