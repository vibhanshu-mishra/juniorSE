# Phase 2 Demand Envelope to AISC Strength Integration Plan

**Goal:** Connect generalized beam-analysis demand envelopes to existing AISC 360-16 Chapter F, G, and J10 skills without duplicating analysis logic.

**Architecture:** `steel-beam-gravity-analysis` owns demand generation and locations. `steel-beam-gravity-check` consumes the standardized analysis result, runs section classification, separate positive/negative Chapter F checks, Chapter G shear, and explicitly requested J10 local web cases. Torsional demand is reported but not treated as covered by F/G/J10.

**Tech Stack:** Python, NumPy, PyYAML, pytest.

## Tasks
- Add governing demand locations to the analysis envelope.
- Add envelope-consumer mode to steel-beam-gravity-check.
- Route positive and negative moments separately to Chapter F.
- Route governing shear to Chapter G.
- Route explicit support-reaction or concentrated-load cases to J10.
- Add regression tests for UDL, point load, continuous beam, moving load, and J10 routing.
- Update rules, examples, and documentation.
