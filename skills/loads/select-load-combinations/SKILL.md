---
name: select-load-combinations
category: structural-loads
level: executable
description: Edition-aware ASCE 7 Chapter 2 load-combination routing and scalar evaluation for engineer-supervised structural design.
---

# select-load-combinations

Use this skill to select and evaluate ASCE 7 Chapter 2 load combinations in a controlled, edition-aware way.

## Trigger

Use when the user asks which load combination governs, which factors apply, whether ASD/LRFD is being used correctly, or how D/L/Lr/S/R/W/E/F/H and supported special Chapter 2 effects should be combined.

## Required inputs

- `code_family`: `ASCE 7`
- `code_edition`: `ASCE 7-16` or `ASCE 7-22`
- `design_method`: `ASD` or `LRFD`
- `load_level`: `service` or `factored`
- `loads`: scalar target effects
- `objective`: strength / allowable stress / uplift / overturning / serviceability context

Additional inputs are required when applicable:

- `h_effect`: `adds` or `resists`
- `h_is_permanent`: required when H resists
- `seismic_effect_definition`: required for legacy scalar `E` under ASCE 7-22
- `chapter2_family`: basic, flood, ice, self_straining, nonspecified, seismic, extraordinary, structural_integrity, or water_in_soil
- `resolved_special_combinations`: required for special families not yet separately benchmarked numerically

## Edition behavior

### ASCE 7-16

- Executes basic LRFD/ASD combinations using the ASCE 7-16 Chapter 2 basis.
- Supports the legacy resolved scalar seismic effect `E` in the ASCE 7-16 combination path.
- Does not permit ASCE 7-22-only `WT` or water-in-soil family routing.

### ASCE 7-22

- Executes the revised basic strength/ASD combinations.
- Supports wind or tornado effect `WT` as an edition-specific wind family.
- Handles `F` with the same factor as `D` in applicable basic combinations.
- Requires explicit H directionality and permanence where relevant.
- Routes resolved seismic effects through Sections 2.3.6 / 2.4.5 using `Ev` plus `Eh` or `Emh`.
- Recognizes the Section 2.3.7 water-in-soil family.

## Process

1. Identify code edition and ASD/LRFD basis.
2. Confirm loads are service-level before applying factors.
3. Identify the Chapter 2 family.
4. Validate edition-specific load symbols and required applicability inputs.
5. If H is present, determine whether it adds to or resists the principal effect and whether it is permanent.
6. If seismic is present, confirm whether the input is a resolved legacy `E` or resolved `Ev`/`Eh`/`Emh` effects.
7. Generate only applicable candidate combinations.
8. Evaluate directional variants for wind/tornado/seismic scalar effects.
9. Report governing positive, negative, and absolute scalar effects.
10. Route serviceability to service-load criteria rather than applying strength factors.
11. For flood, ice, self-straining, nonspecified, extraordinary, structural-integrity, and water-in-soil families, block unless the needed code-defined combination data are explicitly resolved and supplied.

## Guardrails

- Never refactor already factored loads silently.
- Never assume H directionality or permanence.
- Never treat ASCE 7-16 and ASCE 7-22 factors as interchangeable.
- Never silently collapse ASCE 7-22 `Ev` and `Eh` into a vague scalar seismic effect.
- Never invent flood, ice, self-straining, extraordinary-event, structural-integrity, or water-in-soil factors.
- Serviceability is not a strength-combination problem.
- Wind/tornado and seismic effects are not assumed to act simultaneously unless the governing provision explicitly requires it.

## Machine-readable rules

Edition-specific metadata is stored in:

```text
rules/asce7_16.yaml
rules/asce7_22.yaml
```

The Python evaluator reads the selected ruleset and exposes it in the output for QA/QC.

## Definition of done

The result is complete when the edition, method, load level, Chapter 2 family, applicable candidate combinations, governing scalar effects, exclusions, and engineer-review notes are explicit.
