---
name: steel-beam-gravity-check
description: Orchestrate a bounded AISC 360-16 gravity beam check using reusable analysis, classification, flexure, shear, serviceability, and optional web-local skills.
---
# Steel Beam Gravity Check

## Trigger
Use for a bounded noncomposite doubly symmetric I/W gravity-beam check under engineer supervision.

## Process
1. Validate required project/member/load inputs.
2. Analyze service and strength uniform loads.
3. Check LL deflection against L/240 and D+L against L/360.
4. Run `steel-section-classification`.
5. Run `steel-flexure-check` using the Chapter F route allowed by classification.
6. Run `steel-shear-check`.
7. If a concentrated force/reaction and bearing geometry are supplied, run `steel-web-local-checks`.
8. Aggregate DCRs and report any blocked Chapter F route.

## Guardrails
- Do not invent `h`, `Lb`, `Cb`, bearing length, k-distance, or end distance.
- Do not use F2/F3 equations when the web classification requires F4/F5.
- Do not call connection or bearing-plate design complete.
- Engineer review remains mandatory.
