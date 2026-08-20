# juniorSE agent contributor guide

juniorSE is an engineer-supervised structural engineering skill library. Agents working in this repository must preserve the library's guardrails and testability.

## Required behavior
- Read the applicable `SKILL.md` before changing engineering behavior.
- Treat `rules.yaml` as the machine-readable contract for required inputs, stop conditions, supported paths, and definitions of done.
- Never invent engineering inputs to make a validator pass.
- Keep code-edition logic explicit and separate.
- Preserve engineer-review requirements in outputs.

## Skill standard
Validated and executable skills require:
- `SKILL.md`
- `rules.yaml`
- `validator.py`
- `examples/`
- `tests/`

Executable skills also require `calculator.py`.

## Changes
Write or update tests before changing calculation behavior. Run `pytest -q` and `python scripts/smoke_test_plugin.py` before completion.
