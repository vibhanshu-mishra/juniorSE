# juniorSE v0.1

juniorSE is an open-source structural engineering skill library for AI-assisted design reasoning, bounded calculations, assumption control, and QA/QC under licensed engineer supervision.

The goal is not to replace engineering judgment. The goal is to make AI behave like a careful junior structural engineer: classify the task, identify the code path, ask for missing inputs, avoid silent assumptions, perform bounded calculations only when allowed, self-review, and hand off a reviewable result.

Repository: https://github.com/vibhanshu-mishra/juniorSE/tree/main

## Initial skills

1. `structural-response-protocol`
2. `assumption-guardrails`
3. `select-load-combinations`
4. `calculation-qaqc-review`
5. `steel-beam-gravity-check`

## Skill maturity levels

juniorSE uses three skill levels.

### Level 1 — Framework skills

Framework skills govern behavior across the whole library. They define how the AI should classify tasks, communicate uncertainty, manage assumptions, and prepare reviewable outputs.

Expected files:

- `SKILL.md`
- examples or usage notes when helpful
- tests when behavior can be checked automatically

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

## Current implementation status

- `select-load-combinations` is a **validated skill**.
- `steel-beam-gravity-check` is an **executable skill starter**. Its calculator currently covers basic simple-span demand/reaction/deflection mechanics and enforces input completeness. Full AISC capacity checks require section-property and code-equation modules in later versions.
- Core skills remain Markdown-first framework skills.

## Safety and liability

These skills are for educational, preliminary, and engineer-supervised workflows only. They do not replace a licensed professional engineer, project-specific judgment, local code interpretation, peer review, or final approval for construction.
