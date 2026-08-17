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

### AISC 360-16 scope in v0.6
- Chapter B flexural element classification for doubly symmetric I/W shapes.
- Chapter F2 compact-web/compact-flange major-axis flexure.
- Chapter F3 compact-web/noncompact-or-slender-flange major-axis flexure.
- Chapter G unstiffened-web shear with calculated `Cv1`.
- Chapter J10.2 web local yielding.
- Chapter J10.3 web local crippling.
- Live-load deflection limit: `L/240`.
- Dead + live deflection limit: `L/360`.

### Intentionally blocked in v0.6
- Chapter F4 noncompact-web flexure.
- Chapter F5 slender-web flexure.
- Continuous beam analysis.
- Point-load analysis.
- Composite beams.
- Torsion and biaxial bending.
- Connection, bearing-plate, stiffener, web sidesway buckling, and web compression buckling design.

The library must block unsupported paths rather than silently substitute a simpler equation.

## Engineering responsibility
juniorSE is intended for engineer-supervised workflows. Results require review by a qualified structural engineer and are not a substitute for project-specific code interpretation, engineering judgment, or professional responsibility.
