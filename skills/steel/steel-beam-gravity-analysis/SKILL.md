---
name: steel-beam-gravity-analysis
description: Analyze common single- and multi-span beams under point and uniform gravity loads. Use this skill to obtain reactions, shear, moment, and deflection demands before material-specific strength checks.
---

# steel-beam-gravity-analysis

## Trigger
Use when a beam needs structural analysis for gravity loading before a material-specific capacity check.

## Process
1. Identify beam length or individual spans.
2. Identify every support and support restraint.
3. Preserve each load at its actual position; do not replace point loads with uniform loads unless an engineer explicitly requests an equivalent-load approximation.
4. Separate dead and live service loads so service deflections can be checked independently.
5. Require `E` and `I` for deflection and for indeterminate support systems.
6. Solve the beam using a linear-elastic Euler-Bernoulli stiffness formulation.
7. Report support reactions, positive and negative moment extremes, maximum absolute shear, and deflection.
8. For service loads, compare live-load deflection with L/240 and dead-plus-live deflection with L/360.
9. Hand calculated demands to the relevant material design skill; this skill does not determine AISC strength.

## AISC Manual alignment
The 15th Edition Manual groups useful beam aids in Tables 3-22a through 3-22c and Table 3-23. juniorSE uses those table families as behavioral/reference categories rather than embedding a copyrighted lookup table:

- **Table 3-22a:** concentrated-load equivalents. juniorSE analyzes concentrated loads directly, so an equivalent uniform-load approximation is normally unnecessary.
- **Table 3-22b:** cantilever beams. Cantilever restraint and gravity loads are solved directly.
- **Table 3-22c:** continuous beams. Multi-span continuous systems are solved directly from support conditions and stiffness.
- **Table 3-23:** shears, moments, and deflections. juniorSE directly returns these quantities and tests common closed-form cases that correspond to this family of beam diagrams.

## Guardrails
- Do not invent support fixity.
- Do not invent `E` or `I` for an indeterminate beam.
- Do not use factored loads for LL or D+L serviceability checks.
- Do not infer load location from a sketch unless the location can be established reliably.
- Stop if support configuration leaves the model unstable.
- Current release assumes constant EI along the modeled beam.

## Definition of done
A completed analysis identifies the support model and loads, provides reactions/shear/moment demand, reports deflection when stiffness is available, applies the juniorSE serviceability criteria to service loads, and explicitly states that member strength is checked elsewhere.
