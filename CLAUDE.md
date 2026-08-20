# juniorSE project instructions

## Purpose
juniorSE is an open-source structural engineering skill library for engineer-supervised AI-assisted analysis and design. Treat the repository as engineering software, not as a prompt collection.

## Non-negotiable engineering behavior
- No silent engineering assumptions.
- If a required input materially affects demand, capacity, stability, serviceability, or code applicability, ask for it or block the calculation.
- Do not bypass a skill validator to obtain an answer.
- Do not replace an implemented juniorSE skill with remembered equations.
- Do not claim code coverage that the applicable `SKILL.md` and `rules.yaml` do not support.
- Preserve edition-specific code paths. Do not mix ASCE 7-16, ASCE 7-22, or AISC editions.
- Engineer review is always required.

## Skill workflow
For structural tasks:
1. Classify the task.
2. Read the relevant `SKILL.md`.
3. Run or honor its validator before calculation.
4. If blocked, report the missing inputs or unsupported path instead of inventing values.
5. Use the skill calculator for implemented executable paths.
6. Run the calculation QA/QC skill before presenting a design conclusion.
7. State assumptions, code basis, governing limit state, DCR where applicable, and engineer-review notes.

## Repository structure
- `plugin-skills/juniorse/SKILL.md` — top-level router for Claude plugin use.
- `skills/core/` — cross-cutting response, assumption, and QA/QC skills.
- `skills/loads/` — load and load-combination skills.
- `skills/steel/` — steel analysis and design skills.
- Every validated or executable engineering skill includes `SKILL.md`, `rules.yaml`, `validator.py`, `examples/`, and `tests/`.
- Executable skills additionally include `calculator.py`.

## Development rules
- Use test-driven development for behavior changes: write the failing test first, verify the failure, implement, then verify the pass.
- Do not weaken an existing stop condition merely to make a test pass.
- Add a blocked/missing-input test for every new engineering path.
- Add benchmark tests against authoritative or independently verifiable calculations where possible.
- Keep code equations traceable to the skill's stated code section or analysis basis.
- Prefer small reusable skills over large monolithic calculators.

## Verification
Before calling work complete, run:

```bash
pytest -q
python scripts/smoke_test_plugin.py
```

Also compile Python and validate JSON/YAML when release packaging changes those files.

## Scope discipline
If a requested calculation is not implemented, say so explicitly and identify the missing skill/code path. Do not extrapolate an adjacent equation because it looks conservative.
