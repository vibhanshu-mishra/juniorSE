---
name: steel-minor-axis-flexure-check
description: Check bounded AISC 360-16 Chapter F6 minor-axis flexural strength for doubly symmetric I-shaped steel members.
---
# Steel Minor-Axis Flexure Check

Use this skill when a doubly symmetric I-shaped member has bending about its minor principal axis.

## Guardrails
- Do not infer section properties.
- Do not use this skill for torsion or non-I-shapes.
- Do not treat this as a Chapter H interaction check; it supplies `Mcy` for that skill.

## Process
1. Validate material and section properties.
2. Classify the flange for minor-axis flexure.
3. Check yielding and flange local buckling per the implemented F6 path.
4. Apply LRFD or ASD available-strength factors.
5. Return available strength and DCR.

## Definition of done
Return code basis, flange classification, nominal strengths by limit state, governing limit state, available strength, demand, DCR, pass/fail, and engineer-review flag.
