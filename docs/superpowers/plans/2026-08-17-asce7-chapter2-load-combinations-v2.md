# ASCE 7 Chapter 2 Load Combinations v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:test-driven-development while implementing this plan. Steps use checkbox syntax for tracking.

**Goal:** Upgrade `select-load-combinations` from a common-case subset into an edition-aware ASCE 7 Chapter 2 router and evaluator for ASCE 7-16 and ASCE 7-22.

**Architecture:** Keep the skill API stable, move edition-specific rules into `rules/asce7_16.yaml` and `rules/asce7_22.yaml`, and make Python load/evaluate those rules. Exact verified basic, fluid/soil, wind/tornado, and seismic combinations are executable. Special Chapter 2 families are recognized and routed with explicit applicability requirements; they block rather than guess when the required code-defined effect/factor is not supplied.

**Tech Stack:** Python 3, PyYAML, pytest, Markdown/YAML/JSON skill artifacts.

## Global Constraints
- No silent assumptions for code edition, ASD/LRFD, load level, load direction, H stabilizing/destabilizing status, or special-hazard applicability.
- Preserve ASCE 7-16 and ASCE 7-22 differences.
- Do not treat serviceability as a Chapter 2 strength/ASD load-combination problem.
- Do not reproduce proprietary code tables verbatim; encode formulas/rules needed for execution and cite sections in metadata.
- Any Chapter 2 family not numerically verified from an authoritative source must be recognized and safely blocked pending resolved code-defined inputs.

### Tasks
- [x] Add edition-specific rule files.
- [x] Add tests for 7-16 vs 7-22 basic combinations.
- [x] Add F and H inclusion rules.
- [x] Add 7-22 W_T and separated seismic load-effect handling.
- [x] Add Chapter 2 special-family routing for flood, ice, self-straining, nonspecified, extraordinary, structural integrity, and 7-22 water-in-soil.
- [x] Add serviceability routing guardrail.
- [x] Add examples and README updates.
- [x] Run full regression and release verification.
