---
name: steel-compression-check
description: Check the axial compressive strength of a supported doubly symmetric rolled or built-up I-shaped steel member using the implemented AISC 360-16 Chapter E3/E7 path. Use when axial compression strength, flexural buckling, or slender compression elements must be evaluated before Chapter H interaction.
---

# Steel Compression Check

## Trigger
Use this skill for a bounded axial-compression member check when the member is a doubly symmetric rolled I/W shape or built-up I-shape and the engineer has established the effective lengths about both principal axes.

Do not use this skill for HSS, pipe, angles, tees, singly symmetric members, or a case that still requires an unresolved Chapter E4 torsional/flexural-torsional buckling check.

## Ground rules
- Do not assume `Kx = Ky = 1.0`.
- Check flexural buckling about both principal axes.
- Use Chapter B compression-element slenderness limits, not the Chapter B flexural compact/noncompact limits.
- If a flange or web is slender in axial compression, use the implemented Chapter E7 effective-area path.
- Chapter E4 is not calculated here. The input must explicitly state that E4 has been reviewed as non-governing or not required for the case.
- Do not claim global Chapter C stability compliance from a member-strength check.

## Required inputs
- design method: ASD or LRFD
- section type: `rolled_I` or `built_up_I`
- `Fy`, `E`, gross area `Ag`
- required axial compression
- `Lx`, `Ly`
- `Kx`, `Ky`
- `rx`, `ry`
- flange width/thickness `bf`, `tf`
- clear web depth/thickness `h`, `tw`
- explicit Chapter E4 review status

## Process
1. Validate all required inputs and scope.
2. Classify flange and web slenderness for axial compression using AISC 360-16 Chapter B Table B4.1a paths represented by this skill.
3. Calculate `KL/r` and Euler elastic flexural buckling stress `Fe` about x and y.
4. Calculate Chapter E3 critical stress `Fcr` about both axes and identify the governing flexural-buckling axis.
5. If all compression elements are nonslender, use `Pn = Fcr Ag`.
6. If any supported I-shape element is slender, calculate Chapter E7 effective widths and effective area `Ae`, then use `Pn = Fcr Ae`.
7. Apply `phi_c = 0.90` for LRFD or `Omega_c = 1.67` for ASD.
8. Compare required and available strength, report DCR, governing axis/limit state, and QA/QC notes.

## Stop conditions
Stop if:
- either effective-length factor is unknown;
- the section family is unsupported;
- geometry required for compression-element classification is missing;
- Chapter E4 applicability has not been explicitly reviewed;
- an effective-area calculation becomes nonphysical.

## Definition of done
The result is not complete until it reports:
- Chapter B compression-element classification;
- `KL/r`, `Fe`, and `Fcr` about both axes;
- the governing flexural-buckling axis;
- E3 or E7 route;
- gross and effective area;
- nominal and available compressive strength;
- DCR and pass/fail;
- Chapter E4 and Chapter C limitations;
- engineer-review requirement.

## Benchmark basis
The nonslender E3 path is regression-tested against AISC 15th Edition Companion Example E.1D (W14x90 available strength calculation). The slender-web E7 path is regression-tested against Companion Example E.2 (built-up column with a slender web), using the 2016 effective-width formulation.
