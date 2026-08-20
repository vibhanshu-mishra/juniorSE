---
name: assumption-guardrails
category: structural-core
description: Prevent silent assumptions in structural engineering tasks. Use before calculations, design checks, code-path decisions, or engineering conclusions.
---

# assumption-guardrails

This skill controls what the AI is allowed to assume, what it must ask for, and when it must stop.

The goal is to prevent the AI from cooking up missing structural information and presenting it as engineering fact.

## Trigger

Use this skill whenever:

- a structural task has incomplete inputs
- the user asks for a calculation or design check
- the AI is tempted to assume code edition, design method, material grade, support condition, load path, or bracing
- a preliminary calculation may be possible but final design is not

## Ground rules

- No silent assumptions.
- Critical assumptions must be either provided by the user or explicitly approved as preliminary.
- If an unknown input can change demand, capacity, stability, serviceability, or code applicability, it is critical.
- If a value is assumed for demonstration only, the answer must say it cannot be used for final design.
- Do not use typical defaults as if they are project facts.

## Critical inputs that usually cannot be invented

The AI must not silently invent:

- governing code edition
- jurisdiction or local amendments when relevant
- risk category
- occupancy/use category
- design method: ASD or LRFD
- material type and grade/species/strength
- member size/section properties
- span and geometry
- support condition/end fixity
- load path
- load magnitude and source
- whether loads are service-level or factored
- tributary width/area
- unbraced length/lateral bracing condition
- diaphragm flexibility or load path
- seismic design category/site class when seismic design is involved
- wind exposure/enclosure/topographic assumptions when wind design is involved
- deflection/drift criteria
- connection assumptions
- foundation soil bearing values

## Input classification

Classify every input into one of four groups:

1. **Provided** — explicitly given by the user or source material.
2. **Derived** — calculated from provided information, with math shown.
3. **Assumed for preliminary check** — stated clearly and not treated as final.
4. **Missing critical input** — required before completion.

## Stop conditions

Stop and ask for information when:

- design method is unknown and demand/capacity comparison depends on it
- material grade/species/strength is unknown
- loads are unknown or unclear
- load status is unclear: service-level vs factored
- support condition or span is unknown
- unbraced length/bracing condition is required for stability checks
- the applicable code/design basis is not known and cannot be reasonably bounded
- the requested task requires system behavior that has not been defined
- the user asks for final approval, stamping, or construction-ready acceptance

## Allowed preliminary assumptions

The AI may propose preliminary assumptions only if:

- the assumptions are clearly marked
- the calculation is labeled `PRELIMINARY`
- the conclusion says what must be verified
- the assumption is conservative or explicitly for demonstration
- the user is not asking for final construction approval

Example format:

```text
I cannot complete a final check yet. I can proceed with a PRELIMINARY check only if you approve these assumptions:
- Code/design basis: [assumption]
- Design method: [assumption]
- Material grade: [assumption]
- Support/bracing: [assumption]
- Serviceability limit: [assumption]
```

## Forbidden behavior

Do not:

- say “typically” and then calculate as if it is confirmed
- assume continuous bracing for a steel beam unless stated
- assume pinned/fixed support conditions unless stated
- assume loads are service-level or factored without confirmation
- mix code editions
- use a default material strength without labeling it preliminary
- hide missing inputs in footnotes
- give a clean pass/fail when the input set is incomplete

## Definition of done

This skill is complete when the response contains:

- provided inputs
- derived inputs, if any
- missing critical inputs
- proposed preliminary assumptions, if applicable
- stop/proceed decision
- explanation of why each missing critical input matters
