# Phase 1 Steel Strength Implementation Plan

**Goal:** Refactor the gravity beam strength logic into reusable AISC 360-16 steel skills for section classification, flexure, shear, and web local checks, then orchestrate them from the gravity beam check.

**Architecture:** Each engineering limit-state family is a standalone executable skill with `SKILL.md`, `rules.yaml`, `validator.py`, `calculator.py`, `examples/`, and `tests/`. The existing gravity beam check calls these skills and remains responsible for serviceability and overall result aggregation.

**Tech Stack:** Python 3, PyYAML optional, pytest, Markdown, YAML.

## Global Constraints
- AISC 360-16 basis.
- Chapter B classification/limits.
- Chapter F flexure.
- Chapter G shear.
- Chapter J10.2/J10.3 for web local yielding/crippling.
- No connection/support bearing design.
- Block unsupported cases rather than invent assumptions.

## Tasks
- [x] Add section-classification skill with compact/noncompact/slender element routing.
- [x] Add flexure skill for doubly symmetric I/W shapes with compact web and compact/noncompact/slender flange paths.
- [x] Add shear skill with unstiffened-web Cv1 calculation across applicable slenderness regimes.
- [x] Add web-local-check skill for J10.2/J10.3 concentrated-force checks.
- [x] Refactor gravity beam check to orchestrate the reusable skills.
- [x] Add benchmark-style examples and automated tests.
- [x] Run full test suite and package release.
