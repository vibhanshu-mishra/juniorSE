# juniorSE

juniorSE is an open-source structural engineering skill library for AI-assisted design reasoning, bounded calculations, assumption control, and QA/QC under licensed engineer supervision.

The goal is not to replace engineering judgment. The goal is to make AI behave like a careful junior structural engineer: classify the task, identify the code path, ask for missing inputs, avoid silent assumptions, perform bounded calculations only when allowed, self-review, and hand off a reviewable result.

## v0.4 contents

This release contains the core skills plus the upgraded load-combination selector and the split steel beam gravity analysis/check skills.

| Skill | Type | Status |
|---|---:|---|
| `structural-response-protocol` | framework / validated behavior | has `SKILL.md`, `rules.yaml`, `validator.py`, examples, tests |
| `assumption-guardrails` | framework / validated behavior | has `SKILL.md`, `rules.yaml`, `validator.py`, examples, tests |
| `select-load-combinations` | executable skill | has `SKILL.md`, `rules.yaml`, `validator.py`, `calculator.py`, examples, tests |
| `calculation-qaqc-review` | framework / validated behavior | has `SKILL.md`, `rules.yaml`, `validator.py`, examples, tests |
| `steel-beam-gravity-analysis` | executable skill | simple-span uniform-load reactions, shear, moment, and deflection checks |
| `steel-beam-gravity-check` | executable skill | wraps analysis into serviceability checking and strength-readiness review |

## Skill maturity levels

### Level 1 — Framework skills

Framework skills govern behavior across the whole library. They define how the AI should classify tasks, communicate uncertainty, manage assumptions, and prepare reviewable outputs.

Expected files:

- `SKILL.md`
- examples or usage notes when helpful
- tests when behavior can be checked automatically
- `rules.yaml` and `validator.py` when the framework behavior can be made machine-checkable

### Level 2 — Validated skills

Validated skills guide bounded engineering reasoning with enforceable guardrails. They may not perform full engineering calculations, but they must validate inputs, stop conditions, and output requirements.

Required files:

- `SKILL.md`
- `rules.yaml`
- `validator.py`
- `examples/`
- `tests/`

### Level 3 — Executable skills

Executable skills validate first, then perform bounded calculations or checks.

Required files:

- `SKILL.md`
- `rules.yaml`
- `validator.py`
- `calculator.py`
- `examples/`
- `tests/`

## Current execution boundary

The steel beam workflow is intentionally split:

- `steel-beam-gravity-analysis` calculates simple-span uniform-load reactions, maximum shear, maximum moment, and service deflections.
- `steel-beam-gravity-check` compares Live Load deflection to **L/240** and Dead + Live Load deflection to **L/360**, then reports AISC strength checks as incomplete/not implemented in the current version.

It does **not** yet perform AISC section capacity, compactness, LTB strength, shear capacity, bearing, web local yielding/crippling, or final adequacy checks.

That limitation is intentional. juniorSE should under-claim rather than over-claim.

## Safety and liability

These skills are for educational, preliminary, and engineer-supervised workflows only. They do not replace a licensed professional engineer, project-specific judgment, local code interpretation, peer review, or final approval for construction.

## Running tests

From the repository root:

```bash
python -m pytest
```


## v0.3 update

The `select-load-combinations` skill was upgraded from a validated skill to a bounded executable skill. It now includes:

- `rules.yaml` with supported load cases, stop conditions, calculator scope, and definition of done.
- `validator.py` that blocks missing inputs, unsupported load cases, nonnumeric load effects, and unsafe service/factored load mixing.
- `calculator.py` that evaluates common ASCE 7-16/ASCE 7-22 style ASD and LRFD scalar combinations for D, L, Lr, S, R, W, and E.
- positive and negative wind/seismic direction variants for scalar target effects.
- examples for LRFD gravity, ASD gravity, wind directionality, missing design method, and unsupported load cases.
- tests covering validator and calculator behavior.

The load-combination selector is intentionally preliminary and engineer-supervised. It does not implement special seismic effects, overstrength combinations, flood, soil, self-straining, crane, construction, ponding, ice, local amendments, automatic live-load companion reduction eligibility, or multi-axis envelope logic.


## v0.4 update

The steel gravity beam workflow is now split into two skills:

- `steel-beam-gravity-analysis` performs simple-span uniform-load mechanics and deflection calculations.
- `steel-beam-gravity-check` uses the analysis results for a bounded serviceability check and strength-readiness review.

Per project direction, the default serviceability checks are:

- Live Load deflection <= L/240
- Dead + Live Load deflection <= L/360

The skill intentionally does not claim AISC strength adequacy yet.
