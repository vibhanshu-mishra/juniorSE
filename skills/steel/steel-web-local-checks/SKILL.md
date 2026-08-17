---
name: steel-web-local-checks
description: Check concentrated-force web local yielding and web crippling for I/W shapes under AISC 360-16 J10.2 and J10.3.
---
# Steel Web Local Checks

## Trigger
Use when a concentrated force or reaction bears on an unstiffened web and local web limit states must be checked.

## Checks
- J10.2 web local yielding.
- J10.3 web local crippling.

## Required inputs
- design method
- E, Fy
- d, tw, tf, k
- bearing length N
- concentrated force
- distance from member end

## Guardrails
- These are member web local checks, not connection or bearing-plate design.
- Do not infer bearing length or end distance.
- Web sidesway buckling, web compression buckling, and stiffener design are outside this skill.
