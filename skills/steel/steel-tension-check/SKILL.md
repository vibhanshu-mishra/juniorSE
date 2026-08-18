---
name: steel-tension-check
description: Perform a bounded AISC 360-16 Chapter D axial tension strength check using gross-section yielding and net-section rupture, with explicit effective-net-area guardrails.
---
# Steel Tension Check

## Trigger
Use when an engineer asks juniorSE to check a structural steel member carrying axial tension under AISC 360-16.

## Scope
This skill implements the Chapter D tensile member strength path for:
- gross-section yielding
- net-section rupture
- explicit effective net area `Ae`
- `Ae = An × U` when both `An` and shear-lag factor `U` are supplied
- ASD or LRFD available strength
- optional tension-member slenderness advisory

## Required inputs
- design method: ASD or LRFD
- `Fy`
- `Fu`
- gross area `Ag`
- required tensile strength
- either `Ae` directly, or both `An` and `U`

## Process
1. Confirm the problem is axial tension and AISC 360-16 Chapter D applies.
2. Validate material strengths, gross area, required tensile force, and design method.
3. Establish effective net area without inventing connection geometry:
   - use `Ae` if explicitly provided; otherwise
   - calculate `Ae = An × U` only when both values are provided.
4. Calculate nominal gross-section yielding strength.
5. Calculate nominal net-section rupture strength.
6. Convert both nominal strengths to ASD or LRFD available strengths.
7. Select the smaller available strength as governing.
8. Calculate DCR and pass/fail.
9. If member length and minimum radius of gyration are provided, report `L/r` as an advisory check.
10. Run QA/QC and return a standardized `axial_strength_result` for later orchestration by Chapter H.

## Guardrails
- Never invent bolt-hole deductions, net area, or shear-lag factor.
- A complete tension check is blocked when no effective-net-area path is available.
- Do not treat gross yielding alone as a complete member tensile-strength check.
- Do not perform connection block shear, bolt strength, weld strength, gusset strength, or connection design in this skill.
- If connection geometry is needed to establish `An` or `U`, ask for it or require those values from an upstream connection/net-area skill.
- Engineer review is always required.

## Definition of done
The output must report:
- code basis and design method
- effective net area and how it was obtained
- nominal strength for gross yielding
- nominal strength for net-section rupture
- available strength for both limit states
- governing limit state
- required tensile strength
- DCR and pass/fail
- optional slenderness advisory
- QA/QC flags
- standardized axial-strength result for future Chapter H use

## Current boundary
This skill checks the tension member itself. Connection strength and block shear are intentionally outside the Phase 3A boundary.
