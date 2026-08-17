---
name: steel-beam-gravity-check
description: Run AISC 360-16 Chapter B/F/G/J10 steel beam checks from a completed juniorSE generalized beam-analysis result.
---

# Steel Beam Gravity Check

## Trigger
Use this skill after `steel-beam-gravity-analysis` has produced a completed analysis result and the engineer wants member strength/serviceability checks.

## Preferred workflow
1. Receive `analysis_result` from `steel-beam-gravity-analysis`.
2. Confirm AISC 360-16, ASD/LRFD method, section properties, material properties, bracing assumptions, and noncomposite status.
3. Read the standardized `demand_envelope`; do not recalculate beam mechanics in this skill.
4. Classify the section under the juniorSE Chapter B classification skill.
5. Run separate Chapter F checks for positive and negative moment demands. Preserve the sign, location, and governing analysis case in the output.
6. Run Chapter G using the governing absolute shear demand and its location.
7. Run J10.2/J10.3 only for explicitly identified local-force cases. A support-reaction case resolves the force from the analysis result; an explicit-force case must state the force.
8. Use `service_analysis_result` when the strength analysis uses factored loads and a separate service-level analysis is available.
9. Report torsion separately. Do not imply Chapter F/G/J10 constitutes a torsional strength check.
10. Run QA/QC and report governing DCR plus engineer-review notes.

## Guardrails
- Never replace a generalized demand envelope with an equivalent UDL inside this skill.
- Never discard negative moment on continuous beams.
- Do not invent support reactions or concentrated forces for J10.
- Do not treat moving-load demand as static UDL demand.
- Do not treat Saint-Venant torsion analysis as a completed torsional strength design.
- Do not silently use factored-load results for serviceability.

## Definition of done
The output identifies the source demand envelope, positive/negative Chapter F results, Chapter G result, any requested J10 cases, serviceability status, torsion status, governing DCR, and engineer-review requirement.

## Legacy mode
The original simple-span uniform-load input remains supported only for backward compatibility. New work should use the generalized `analysis_result` interface.
