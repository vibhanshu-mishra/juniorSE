---
name: steel-flexure-check
description: Perform a bounded AISC 360-16 Chapter F major-axis flexural strength check for doubly symmetric I-shaped steel members, including F2, F3, F4 and F5 routes.
---
# Steel Flexure Check

## Trigger
Use for engineer-supervised major-axis simple bending checks of doubly symmetric I-shaped steel members under AISC 360-16.

## Process
1. Confirm AISC 360-16, ASD/LRFD, simple major-axis bending, and doubly symmetric I-shape scope.
2. Use Chapter B classification to route the member:
   - compact web + compact flange -> F2
   - compact web + noncompact/slender flange -> F3
   - noncompact web -> F4
   - slender web -> F5
3. Evaluate all implemented Chapter F limit states for that route.
4. Apply ASD/LRFD available-strength conversion only after nominal strength is established.
5. Report every candidate nominal strength, governing limit state, DCR, assumptions, and review notes.

## Guardrails
- Never apply F2/F3 equations to a noncompact or slender web.
- F4/F5 in Phase 1B are validated only for doubly symmetric I-shaped members. Block singly symmetric members.
- Do not infer geometric properties or bracing data.
- Do not silently substitute F5 for F4 unless a future skill explicitly permits a conservative alternate route.
- Do not treat this skill as torsional, biaxial, composite, or connection design.

## F4 implementation
For doubly symmetric I-shapes with noncompact webs, evaluate compression-flange yielding, lateral-torsional buckling, and compression-flange local buckling when applicable. The implementation uses the F4 web plastification and effective LTB radius framework. Tension-flange yielding is non-governing for the validated doubly symmetric path where Sxt = Sxc.

## F5 implementation
For doubly symmetric I-shapes with slender webs, evaluate compression-flange yielding, lateral-torsional buckling, compression-flange local buckling when applicable, and tension-flange yielding when Sxt < Sxc. Apply the F5 bending-strength reduction factor Rpg.

## Definition of done
The output is complete only when it reports the Chapter F route, limit-state nominal strengths, governing limit state, available strength, demand, DCR, pass/fail, and engineer-review flag.

## Benchmark policy
F4 is regression-tested against AISC 15th Edition Manual Companion v15.1 Example F.15. F5 is equation-path tested against AISC 360-16 because a dedicated F5 slender-web Chapter F Companion example was not identified.
