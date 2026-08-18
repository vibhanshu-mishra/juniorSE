---
name: steel-combined-forces-check
description: Evaluate bounded AISC 360-16 Chapter H1 axial-force and biaxial-flexure interaction using reusable juniorSE axial and flexure strength skills.
---
# Steel Combined Forces Check

Use this skill for a doubly symmetric I-shaped steel member subject to axial force plus major- and/or minor-axis flexure.

## Guardrails
- Do not invent axial or flexural capacities.
- Reuse `steel-axial-strength`, `steel-flexure-check`, and `steel-minor-axis-flexure-check`.
- Required strengths must come from an explicitly acknowledged second-order or Chapter C-compatible analysis basis.
- This skill does not certify global Chapter C stability compliance.
- Do not use this H1 implementation for torsion or specialized H2/H3 cases.

## Process
1. Obtain axial available strength from Chapter D/E through `steel-axial-strength`.
2. Obtain major-axis flexural available strength from the existing Chapter F skill.
3. Obtain minor-axis flexural available strength from the F6 skill.
4. Form `Pr/Pc`, `Mrx/Mcx`, and `Mry/Mcy`.
5. Route to H1-1a when axial utilization is at least 0.20; otherwise route to H1-1b.
6. Report the interaction ratio and all component ratios.

## Definition of done
Return the child strength results, H1 equation used, component utilization ratios, final interaction ratio, pass/fail status, analysis-basis note, and engineer-review flag.
