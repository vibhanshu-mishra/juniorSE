# Phase 2B General Beam Analysis Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Extend `steel-beam-gravity-analysis` to support linearly varying/trapezoidal loads, concentrated moments, support settlements, variable EI, moving-load envelopes, optional shear deformation, bounded second-order analysis, bounded Saint-Venant torsion, and unified demand envelopes.

**Architecture:** Keep bending analysis as a finite-element demand engine independent of AISC capacity checks. Add load/stiffness/effect primitives behind a stable `calculate(inputs)` interface, retain explicit validation/stop conditions, and keep torsion in a separate analysis channel. Phase 2B ends at standardized demand envelopes; Chapters F/G/J10 orchestration is a later step.

**Tech Stack:** Python 3, NumPy, PyYAML, pytest.

**Spec:** Approved in chat on 2026-08-17.

## Global Constraints

- Do not invent structural properties, settlements, stiffness, shear area, torsional restraints, or second-order axial forces.
- Keep LL deflection limit at L/240 and D+L deflection limit at L/360.
- Use direct analysis rather than transcribing proprietary AISC Manual table coefficients.
- Treat AISC 360-16 as design/analysis context; this module produces demands and does not itself claim member strength adequacy.
- Torsion in this phase is Saint-Venant torsion only; warping torsion is outside scope unless explicitly implemented later.
- Second-order analysis in this phase is a bounded elastic geometric-stiffness formulation, not a full Direct Analysis Method implementation.

---

### Task 1: Variable Distributed Loads and Concentrated Moments
- [x] Write failing tests for triangular, trapezoidal, and nodal concentrated moment benchmarks.
- [x] Implement exact/numerically integrated consistent nodal loads.
- [x] Verify tests pass.

### Task 2: Variable EI and Support Settlements
- [x] Write failing tests for two-segment EI and imposed settlement cases.
- [x] Implement element-level stiffness lookup and prescribed support displacement solution.
- [x] Verify tests pass.

### Task 3: Moving-Load Envelopes
- [x] Write failing tests for a single moving point load on a simple span.
- [x] Implement axle-pattern stepping and response envelopes.
- [x] Verify tests pass.

### Task 4: Shear Deformation
- [x] Write failing test against a simply supported center-point-load Timoshenko deflection benchmark.
- [x] Implement optional Timoshenko element stiffness requiring G and shear area.
- [x] Verify tests pass.

### Task 5: Second-Order Effects
- [x] Write failing tests for zero-axial-force equivalence and compressive-force amplification.
- [x] Implement elastic geometric stiffness with explicit axial-force inputs and stability blocking.
- [x] Verify tests pass.

### Task 6: Torsion
- [x] Write failing tests for a prismatic Saint-Venant torsion benchmark.
- [x] Implement separate torsion finite-element channel requiring G, J, torsional restraints, and applied torque.
- [x] Verify tests pass.

### Task 7: Unified Demand Envelopes, Rules, Examples, Docs
- [x] Add standardized reaction/shear/moment/deflection/torsion envelope output.
- [x] Update validator, `rules.yaml`, `SKILL.md`, examples, and README.
- [x] Run full pytest, compile check, JSON validation, and ZIP integrity check.
