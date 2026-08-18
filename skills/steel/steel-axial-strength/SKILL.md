---
name: steel-axial-strength
description: Route a signed steel axial demand to the appropriate juniorSE AISC 360-16 Chapter D tension or Chapter E compression skill and return a standardized axial-strength result for downstream Chapter H interaction checks.
---

# steel-axial-strength

## Trigger
Use this skill when a steel member has a known signed axial force and the task needs a single axial-strength interface without manually choosing between the Chapter D tension and Chapter E compression skills.

## Sign convention
Phase 3C uses one explicit convention only:

- positive `required_axial_kip` = tension
- negative `required_axial_kip` = compression
- zero = no axial demand

The input `sign_convention` must therefore be `tension_positive`.

## Process
1. Validate the signed axial force and sign convention.
2. If force is positive, call `steel-tension-check` and pass the magnitude as `required_tension_kip`.
3. If force is negative, call `steel-compression-check` and pass the absolute magnitude as `required_compression_kip`.
4. If force is zero, return a zero-demand result without invoking a design chapter.
5. Preserve the child skill's guardrails and blocked status.
6. Normalize the successful child result into `axial_strength_result` for downstream Chapter H use.

## Guardrails
- This skill contains no independent Chapter D/E capacity equations.
- Never invent tension connection inputs such as `An`, `Ae`, or `U`.
- Never invent compression stability inputs such as `Kx`, `Ky`, or `e4_review_status`.
- Do not allow a second required-strength field inside `member_inputs`; the signed axial force is the single source of demand.
- A blocked child skill means this skill is blocked.

## Output contract
A complete nonzero case returns at minimum:

- `source_skill`
- `source_chapter`
- `signed_required_axial_kip`
- `child_result`
- `axial_strength_result`

The normalized `axial_strength_result` carries:

- `force_type`
- `chapter`
- `required_strength_kip`
- `available_strength_kip`
- `dcr`
- `governing_limit_state`
- `passes`

## Definition of done
The skill is complete only when the sign has been routed explicitly, the relevant Chapter D/E skill has completed, its guardrails have been preserved, and the normalized axial-strength output is ready for a later Chapter H interaction skill.
