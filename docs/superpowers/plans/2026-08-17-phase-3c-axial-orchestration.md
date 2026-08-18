# Phase 3C Axial Strength Orchestration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a single `steel-axial-strength` interface that routes axial tension to the existing Chapter D skill and axial compression to the existing Chapter E skill, preserving all child-skill guardrails and returning one standardized axial-strength result for future Chapter H use.

**Architecture:** `steel-axial-strength` is an orchestration skill, not a new design-equation skill. It validates a signed axial demand plus a nested member/design payload, maps positive tension and negative compression into the child skill's expected required-strength input, calls the existing calculators without duplicating Chapter D/E equations, and normalizes the output.

**Tech Stack:** Markdown, YAML, Python 3, pytest, JSON examples.

**Spec:** Phase 3C design approved in conversation on 2026-08-17.

## Global Constraints

- No duplication of Chapter D or Chapter E equations in the orchestrator.
- Positive signed axial demand means tension; negative means compression; zero force returns a zero-demand result without invoking a design chapter.
- Preserve child skill blocks and errors exactly enough for an engineer to understand why the calculation stopped.
- Do not invent shear-lag, net-area, effective-length, or E4-review inputs.
- Return a standardized `axial_strength_result` for future Chapter H use.
- Both validated and executable skills include `SKILL.md`, `rules.yaml`, `validator.py`, `calculator.py`, `examples/`, and `tests/`.

---

### Task 1: Axial router contract and failing tests

**Files:**
- Create: `skills/steel/steel-axial-strength/tests/test_axial_strength.py`

**Interfaces:**
- Consumes: `calculate(inputs: dict)` from the future orchestrator.
- Produces: tests for tension routing, compression routing, zero axial force, unknown sign convention, and child-skill block propagation.

### Task 2: Skill validator and calculator

**Files:**
- Create: `skills/steel/steel-axial-strength/validator.py`
- Create: `skills/steel/steel-axial-strength/calculator.py`

**Interfaces:**
- Consumes: signed `required_axial_kip`, `sign_convention`, and `member_inputs`.
- Produces: normalized `axial_strength_result` plus `source_skill`, `source_chapter`, and child details.

### Task 3: Skill documentation, machine rules, examples

**Files:**
- Create: `skills/steel/steel-axial-strength/SKILL.md`
- Create: `skills/steel/steel-axial-strength/rules.yaml`
- Create: `skills/steel/steel-axial-strength/examples/*.json`

### Task 4: README and release verification

**Files:**
- Modify: `README.md`

**Verification:**
- Run full pytest suite.
- Compile all Python files.
- Parse all JSON and YAML files.
- Check ZIP integrity.
