# OpenStruct Skills v0.1

OpenStruct Skills is an open-source structural engineering skill library for AI-assisted design reasoning, bounded calculations, assumption control, and QA/QC under licensed engineer supervision.

The goal is not to replace engineering judgment. The goal is to make AI behave more like a careful junior structural engineer: classify the task, identify the code path, ask for missing inputs, avoid silent assumptions, perform bounded calculations, self-review, and hand off a reviewable result.

## Initial skills

1. `structural-response-protocol`
2. `assumption-guardrails`
3. `select-load-combinations`
4. `calculation-qaqc-review`
5. `steel-beam-gravity-check`

## How skills are structured

Each skill is a plain `SKILL.md` file with:

- trigger
- ground rules
- required inputs
- process
- guardrails
- definition of done
- handoffs to related skills

This keeps the library readable for engineers and usable by AI agents. Future versions can add YAML/JSON schemas and Python calculation modules.

## Safety and liability

These skills are for educational, preliminary, and engineer-supervised workflows only. They do not replace a licensed professional engineer, project-specific judgment, local code interpretation, peer review, or final approval for construction.

