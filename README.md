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

### AISC 360-16 scope in v0.8
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
`steel-beam-gravity-analysis` now supports direct linear-elastic analysis for:
- simple beams
- cantilevers
- fixed-fixed and propped cantilevers
- multi-span continuous beams with explicit pinned/roller/fixed supports
- full-span and partial uniform loads
- concentrated point loads
- mixed point + uniform loading
- reactions, positive/negative moments, shear, and deflection

The implementation uses a direct Euler-Bernoulli stiffness solution instead of copying Manual lookup tables. It aligns behaviorally with the beam-analysis families identified by AISC 15th Edition Manual Tables 3-22a, 3-22b, 3-22c, and 3-23. Concentrated loads are kept at their actual locations rather than being replaced with equivalent uniform loads unless an engineer explicitly requests that approximation.

Current Phase 2 limits include constant EI, no applied concentrated moments, no linearly varying/trapezoidal distributed loads, no support settlement, no moving-load envelope, and no second-order effects.

### Intentionally blocked / future phases
- Singly symmetric F4/F5 member implementation.
- Composite beams.
- Torsion and biaxial bending.
- Full axial tension/compression capacity and Chapter H beam-column interaction.
- Connection and bearing-plate design.

The library must block unsupported paths rather than silently substitute a simpler equation.

## Engineering responsibility
juniorSE is intended for engineer-supervised workflows. Results require review by a qualified structural engineer and are not a substitute for project-specific code interpretation, engineering judgment, or professional responsibility.
