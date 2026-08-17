---
name: steel-beam-gravity-analysis
description: Analyze single- and multi-span beams under point, uniform, triangular, trapezoidal, moment, settlement, moving, second-order, shear-deformation, and bounded Saint-Venant torsion effects. Use this skill to obtain demand envelopes before material-specific strength checks.
---

# steel-beam-gravity-analysis

## Trigger
Use when a beam needs structural demand analysis before a material-specific capacity check.

## Required behavior
1. Establish the beam geometry and every support restraint.
2. Preserve actual load locations and load shapes.
3. Separate dead and live loads when serviceability is requested.
4. Require real stiffness/properties for any analysis that depends on them.
5. Block unsupported or unstable models instead of inventing properties.
6. Return a unified demand envelope suitable for downstream design skills.

## Supported bending actions
- full-span and partial uniform loads
- point loads
- triangular and trapezoidal line loads
- applied concentrated moments
- mixed load cases
- simple, cantilever, fixed, propped, and continuous multi-span beams
- piecewise-variable EI
- imposed vertical support settlements
- moving axle patterns and directly stepped response envelopes

## Optional analysis modes
### Shear deformation
Use a Timoshenko beam stiffness formulation only when `G_ksi` and effective `Av_in2` are explicitly supplied. Do not invent a shear area or correction factor.

### Second-order effects
A bounded elastic geometric-stiffness mode may be used when an explicit axial force is supplied. Positive axial force means compression. This is an analysis aid for P-delta/P-delta-like amplification; it is **not** a complete implementation of the AISC 360-16 Direct Analysis Method. Near-instability cases must stop and require rigorous stability analysis.

### Torsion
Torsion is solved in a separate Saint-Venant channel. Explicit torsional restraints and `GJ` are required. Point and distributed torque may be analyzed. Warping torsion, bimoment, and warping normal stresses remain outside this phase.

## AISC/Manual alignment
AISC 360-16 is the steel-design context. The 15th Edition Manual beam tables are used as reference/benchmark families rather than transcribed lookup tables. juniorSE analyzes the actual system directly.

## Serviceability
For service-level beam bending loads, compare:
- live-load deflection to `L/240`
- dead + live deflection to `L/360`

When imposed support settlement makes a normal span-deflection comparison ambiguous, flag the serviceability interpretation for engineer review rather than silently treating settlement as ordinary beam deflection.

## Guardrails
- Never infer fixity, settlement, stiffness, shear area, torsional restraint, or axial force.
- Do not use factored loads for serviceability checks.
- Do not infer torsional restraint from pinned/roller/fixed bending labels.
- Do not call second-order elastic geometric stiffness a complete AISC Direct Analysis Method analysis.
- Do not use Saint-Venant-only torsion when restrained warping is material to the problem.
- This skill produces demand. AISC Chapters F/G/J10 strength checks happen in downstream skills.

## Definition of done
A complete analysis returns support reactions, bending moment extremes, maximum shear, deflection, requested moving-load/torsion results, a unified demand envelope, QA/QC notes, and an explicit engineer-review requirement.
