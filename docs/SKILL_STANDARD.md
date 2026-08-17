# juniorSE Structural Skill Standard

Every juniorSE skill must be written as a reusable engineering method, not generic notes.

A skill should make AI behave like a cautious junior structural engineer working under supervision: classify the task, identify the code path, verify inputs, avoid silent assumptions, perform only bounded work, self-review, and hand off the result for engineer review.

## Required sections in every `SKILL.md`

1. Metadata frontmatter
2. Purpose
3. Trigger
4. Do not use when
5. Ground rules
6. Required inputs
7. Optional inputs
8. Stop conditions
9. Allowed assumptions
10. Forbidden assumptions
11. Process
12. QA/QC
13. Definition of done
14. Handoffs

## Required structure by maturity level

### Level 1 — Framework skills

Framework skills define global behavior. They may be conceptual, but whenever behavior can be checked automatically, they should include rules and tests.

Expected files:

- `SKILL.md`
- `rules.yaml` when the behavior can be expressed as enforceable rules
- `validator.py` when outputs or inputs can be checked
- `examples/` when the behavior benefits from passing/blocked examples
- `tests/` when the behavior can be validated automatically

### Level 2 — Validated skills

Validated skills are used when a wrong assumption, missing input, or wrong code path could produce unsafe or misleading output. They do not have to run full calculations, but they must be machine-checkable.

Required files:

- `SKILL.md` — human-readable engineering workflow
- `rules.yaml` — machine-readable required inputs, stop conditions, guardrails, and definition of done
- `validator.py` — Python validation for required inputs and stop conditions
- `examples/` — at least one passing example and one blocked/missing-input example
- `tests/` — automated tests proving the validator behaves correctly

### Level 3 — Executable skills

Executable skills validate first, then run bounded calculations.

Required files:

- `SKILL.md`
- `rules.yaml`
- `validator.py`
- `calculator.py`
- `examples/`
- `tests/`

Additional expectations:

- benchmark examples with known expected outputs
- tests for numerical results within a stated tolerance
- explicit limits on what the calculator does not yet cover

## Global principles

- No silent assumptions.
- No final engineering approval language.
- No mixing ASD demand with LRFD capacity or vice versa.
- No skipping serviceability when it is relevant.
- No code-path claims without stating the governing basis.
- No calculation output without a self-review.
- Uncertainty must be shown, not hidden.
- If a critical input materially affects safety, load path, demand, capacity, or serviceability, the skill must stop or label the output as preliminary with explicit assumptions.

## Standard output expectation

A completed engineering response should include:

1. Task classification
2. Input summary
3. Missing inputs or assumptions
4. Code/design basis
5. Load combination basis
6. Calculation steps
7. Limit-state checks
8. Serviceability checks, if applicable
9. Governing result
10. QA/QC review
11. Engineer review notes
