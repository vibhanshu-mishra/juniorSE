---
name: steel-flexure-check
description: Check major-axis flexural strength of noncomposite doubly symmetric I/W shapes under AISC 360-16 Chapter F for compact-web F2/F3 routes.
---
# Steel Flexure Check

## Trigger
Use after section classification for major-axis flexure of a noncomposite doubly symmetric I/W shape.

## Implemented routes
- F2: compact web + compact flange.
- F3: compact web + noncompact or slender flange, including compression-flange local buckling reduction.

## Guardrails
- If the web is noncompact, stop and identify Chapter F4 as required.
- If the web is slender, stop and identify Chapter F5 as required.
- Never silently use F2/F3 for F4/F5 members.
- `Cb` must be supplied or explicitly accepted as 1.0.

## Definition of done
Return the Chapter F route, yielding/LTB/local-buckling nominal strengths as applicable, governing nominal strength, available strength, DCR, and governing limit state.
