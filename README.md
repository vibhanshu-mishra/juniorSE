# juniorSE

juniorSE is an open-source structural engineering skill library for AI-assisted, engineer-supervised structural design and analysis.

The project is designed to make an AI behave more like a disciplined junior structural engineer: validate inputs, refuse unsupported assumptions, follow a defined code path, perform bounded calculations, run QA/QC, and hand back reviewable engineering work.

## Skill standard
Validated and executable skills include:
- `SKILL.md`
- `rules.yaml`
- `validator.py`
- `examples/`
- `tests/`

Executable skills additionally include `calculator.py`.

## Current steel stack
- `steel-beam-gravity-analysis`
- `steel-section-classification`
- `steel-flexure-check`
- `steel-shear-check`
- `steel-web-local-checks`
- `steel-beam-gravity-check` (orchestrator)

### AISC 360-16 scope through v0.9
- Chapter B flexural element classification for doubly symmetric I/W shapes.
- Chapter F2 compact-web/compact-flange major-axis flexure.
- Chapter F3 compact-web/noncompact-or-slender-flange major-axis flexure.
- Chapter F4 doubly symmetric I-shaped members with noncompact webs.
- Chapter F5 doubly symmetric I-shaped members with slender webs.
- Chapter G unstiffened-web shear with calculated `Cv1`.
- Chapter J10.2 web local yielding.
- Chapter J10.3 web local crippling.
- Live-load deflection limit: `L/240`.
- Dead + live deflection limit: `L/360`.

### Phase 1B benchmark policy
- F4 is regression-tested against AISC 15th Edition Manual Companion v15.1, Volume 1, Example F.15 (Plate Girder Flexural Member).
- The Companion is keyed to ANSI/AISC 360-16.
- No dedicated F5 slender-web Chapter F example was identified in the v15.1 Companion chapter examples. F5 is therefore tested equation-by-equation against the AISC 360-16 F5 framework and is not mislabeled as Companion-benchmarked.


### Phase 2 beam-analysis scope
`steel-beam-gravity-analysis` now supports a direct finite-element demand engine for:
- simple, cantilever, fixed, propped, and multi-span continuous beams
- full-span and partial uniform loads
- concentrated point loads and applied concentrated moments
- triangular and trapezoidal line loads
- mixed loading
- piecewise-variable EI
- imposed vertical support settlements
- moving axle-pattern envelopes
- optional Timoshenko shear deformation with explicit `G` and effective `Av`
- bounded elastic geometric-stiffness second-order analysis with explicit axial force
- a separate Saint-Venant torsion channel with point/distributed torque and piecewise `GJ`
- unified reaction/shear/moment/deflection/torsion demand envelopes

The implementation analyzes the actual system directly rather than copying Manual lookup tables. AISC 15th Edition Manual Tables 3-22a, 3-22b, 3-22c, and 3-23 remain reference/benchmark families.

Second-order mode is deliberately labeled as an elastic geometric-stiffness analysis aid, **not** a complete AISC 360-16 Direct Analysis Method implementation. Torsion is Saint-Venant only; restrained warping remains outside Phase 2B.

### Intentionally blocked / future phases
- Singly symmetric F4/F5 member implementation.
- Composite beams.
- Restrained warping torsion and biaxial bending strength interaction.
- Full axial tension/compression capacity and Chapter H beam-column interaction.
- Connection and bearing-plate design.

The library must block unsupported paths rather than silently substitute a simpler equation.

## Engineering responsibility
juniorSE is intended for engineer-supervised workflows. Results require review by a qualified structural engineer and are not a substitute for project-specific code interpretation, engineering judgment, or professional responsibility.

## v1.0 — Phase 2 demand-to-strength integration

The generalized `steel-beam-gravity-analysis` demand envelope now feeds the existing AISC 360-16 strength modules. `steel-beam-gravity-check` preserves positive and negative moment separately for Chapter F, sends governing shear to Chapter G, resolves explicitly requested support-reaction/local-force cases to J10.2/J10.3, and reports torsional demand separately rather than treating F/G/J10 as a torsional design check. The older simple-span UDL interface remains compatibility-only.
