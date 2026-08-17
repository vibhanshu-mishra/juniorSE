---
name: steel-section-classification
description: Classify flange and web slenderness for doubly symmetric I/W shapes for major-axis flexure under AISC 360-16 Chapter B.
---

# Steel Section Classification

## Trigger
Use before a Chapter F major-axis flexure check of a noncomposite doubly symmetric I- or W-shape.

## Required inputs
- `E_ksi`
- `Fy_ksi`
- `bf_in`
- `tf_in`
- `h_in`
- `tw_in`

## Process
1. Validate positive material and geometry inputs.
2. Compute flange slenderness `bf/(2tf)`.
3. Compute web slenderness `h/tw` using clear web depth `h`, not overall depth `d`.
4. Compare each element against the AISC 360-16 Chapter B flexural compactness limits implemented by this skill.
5. Return compact, noncompact, or slender classifications and the flexure route they imply.

## Guardrails
- Do not substitute `d/tw` for `h/tw` when `h` is unknown.
- Do not classify non-I shapes using this skill.
- Classification alone is not a strength check.

## Definition of done
Return slenderness ratios, limits, element classifications, flexure route, and engineer-review flag.
