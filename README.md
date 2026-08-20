# juniorSE

**juniorSE** is an open-source structural engineering skill library for AI-assisted, engineer-supervised design and analysis.

The goal is simple: give an AI a disciplined structural-engineering workflow so it behaves less like a general-purpose chatbot and more like a careful junior structural engineer working under review.

juniorSE is designed to make an AI:

- identify what kind of structural task it has been given
- determine which inputs and assumptions are required
- stop when critical information is missing
- avoid inventing engineering assumptions
- follow an explicit code and calculation path
- perform bounded analysis and design checks
- run QA/QC before presenting results
- explain what governed and why
- clearly identify what still requires engineer review

It is **not** intended to replace a structural engineer, professional judgment, project-specific code interpretation, or responsible charge.

---

## Install juniorSE in Claude Code

juniorSE can be used as a Claude Code plugin so users do not need to copy individual skills manually. The repository includes a Claude plugin manifest, marketplace definition, and a top-level `juniorse` router skill.

### Install from GitHub

After this repository version is pushed to GitHub, add the juniorSE marketplace and install the plugin:

```bash
claude plugin marketplace add vibhanshu-mishra/juniorSE
claude plugin install juniorse@juniorse
```

Restart Claude Code or run `/reload-plugins` if prompted. juniorSE skills are namespaced under the plugin. You can invoke the top-level router explicitly with:

```text
/juniorse:juniorse
```

or ask a structural-engineering question normally and allow Claude to select an applicable juniorSE skill from its descriptions.

### Test the plugin from a local checkout

From the repository root:

```bash
claude --plugin-dir .
```

Then invoke:

```text
/juniorse:juniorse
```

For repository-level development, `CLAUDE.md` supplies project instructions. Installed plugins do not rely on that file; the runtime structural-engineering operating rules live in the `juniorse` router skill itself.

### Other agents

The individual `SKILL.md` files remain plain-text Agent Skills and can be consumed by other compatible agents. `AGENTS.md` documents cross-agent contribution rules; the Python validators and calculators can also be used independently of Claude.

## Agent-facing architecture

```text
CLAUDE.md                         # repo-development instructions
AGENTS.md                         # cross-agent contributor rules
.claude-plugin/
├── plugin.json                   # Claude plugin manifest
└── marketplace.json              # installable GitHub marketplace entry
plugin-skills/
└── juniorse/
    └── SKILL.md                  # top-level runtime router
skills/
├── core/                         # assumptions, response protocol, QA/QC
├── loads/                        # ASCE 7 load-combination skills
└── steel/                        # analysis and steel design skills
```

The router does not contain duplicate engineering equations. It classifies the task and routes Claude into the narrowest existing skill, preserving that skill's validator, calculator, tests, and stop conditions.

---

## Why juniorSE exists

Large language models can do arithmetic, explain structural concepts, and often reproduce familiar engineering equations. That does not make them reliable structural engineers.

The larger failure modes are usually procedural:

- starting a calculation before enough information is known
- silently assuming material properties, support conditions, bracing, or code criteria
- mixing ASD and LRFD demand/capacity paths
- checking one limit state while forgetting another
- losing important load-case or governing-location information
- using an equation outside its valid range
- returning a confident answer when the correct response should be: **"I cannot complete this check until I know X."**

juniorSE addresses that problem by encoding structural-engineering work as reusable, testable skills with explicit guardrails.

---

## Core principles

### 1. No silent engineering assumptions

If a missing input materially affects demand, capacity, stability, serviceability, or code applicability, juniorSE must either:

- request the missing information, or
- proceed only under an explicitly stated and permitted preliminary assumption.

Critical assumptions must never be invented silently.

### 2. Block unsupported paths

If a skill does not implement the applicable engineering path, it should stop and say so.

juniorSE should prefer:

> This condition requires a design path that is not yet implemented.

instead of forcing the problem through a simpler but incorrect equation.

### 3. Separate analysis from design

Analysis produces demands.

Design skills evaluate those demands against code-based strength and serviceability requirements.

This separation allows the same design skills to work whether the governing demand came from a uniform load, point load, continuous beam, settlement, moving load, or another supported analysis case.

### 4. Human-readable and machine-testable

Skills should be understandable by structural engineers and also verifiable by software.

### 5. Engineer review is always required

juniorSE is an engineering assistant, not an engineer of record.

---

## Skill architecture

A juniorSE skill is a reusable engineering method rather than a one-off prompt.

Validated and executable skills follow a common structure:

```text
skill-name/
├── SKILL.md
├── rules.yaml
├── validator.py
├── examples/
└── tests/
```

Executable skills additionally include:

```text
calculator.py
```

### What each file does

| File | Purpose |
|---|---|
| `SKILL.md` | Human-readable engineering workflow, trigger, process, guardrails, and definition of done |
| `rules.yaml` | Machine-readable required inputs, stop conditions, supported paths, and constraints |
| `validator.py` | Enforces input completeness and guardrails before calculation |
| `calculator.py` | Performs bounded calculation or analysis logic for executable skills |
| `examples/` | Passing, blocked, edge-case, and benchmark examples |
| `tests/` | Automated regression and validation tests |

The intent is that **Markdown teaches the method, rules constrain the method, Python executes or validates it, and tests prove expected behavior.**

---


## ASCE 7 Chapter 2 load combinations

`select-load-combinations` is an edition-aware Chapter 2 router/evaluator for **ASCE 7-16** and **ASCE 7-22**.

Current executable scope includes:

- basic LRFD and ASD combinations
- ASCE 7-16 vs ASCE 7-22 companion-load differences
- `F` fluid-load inclusion with the applicable dead-load factor
- explicit `H` stabilizing/destabilizing handling
- wind directionality
- ASCE 7-22 tornado effect `WT` routing
- ASCE 7-16 legacy resolved seismic effect `E`
- ASCE 7-22 resolved `Ev` + `Eh` / `Emh` seismic combination routing
- governing positive, negative, and absolute scalar effects
- serviceability routing outside strength-combination generation

The skill also recognizes the Chapter 2 families for flood, atmospheric ice / wind-on-ice, self-straining effects, nonspecified loads, extraordinary events, general structural integrity, and the ASCE 7-22 alternative water-in-soil method. These special families currently require **explicitly resolved code-defined combinations** rather than allowing juniorSE to invent unverified factors.

Edition-specific machine-readable metadata lives in:

```text
skills/loads/select-load-combinations/rules/asce7_16.yaml
skills/loads/select-load-combinations/rules/asce7_22.yaml
```

## Current steel skill stack

The current steel workflow is intentionally modular:

```text
steel-beam-gravity-analysis
            ↓
standardized demand envelope
            ↓
steel-section-classification
            ↓
steel-flexure-check
steel-minor-axis-flexure-check
steel-shear-check
steel-web-local-checks
steel-tension-check
steel-compression-check
            ↓
steel-axial-strength
            ↓
steel-combined-forces-check
            ↓
steel-beam-gravity-check / future steel-member-check
            ↓
governing result + QA/QC
```

### Available steel skills

- `steel-beam-gravity-analysis`
- `steel-section-classification`
- `steel-flexure-check`
- `steel-minor-axis-flexure-check`
- `steel-shear-check`
- `steel-web-local-checks`
- `steel-tension-check`
- `steel-compression-check`
- `steel-axial-strength`
- `steel-combined-forces-check`
- `steel-beam-gravity-check`

`steel-beam-gravity-check` acts as the orchestration skill. It consumes analysis results and routes the relevant demands into the reusable design skills.

---

## Current analysis capabilities

`steel-beam-gravity-analysis` uses direct beam analysis rather than relying on copied lookup-table coefficients.

Supported behavior currently includes:

- simple beams
- cantilevers
- fixed beams
- propped cantilevers
- multi-span continuous beams
- full-span uniform loads
- partial uniform loads
- concentrated point loads
- applied concentrated moments
- triangular line loads
- trapezoidal line loads
- mixed loading
- piecewise-variable `EI`
- imposed vertical support settlements
- moving axle-pattern envelopes
- optional Timoshenko shear deformation with explicit `G` and effective `Av`
- bounded elastic geometric-stiffness second-order analysis with explicit axial force
- Saint-Venant torsion with point/distributed torque and piecewise `GJ`

The analysis engine can produce standardized envelopes for:

- reactions
- shear
- positive moment
- negative moment
- absolute governing moment
- deflection
- governing locations
- moving-load effects
- torsional demand where requested

AISC Manual Tables 3-22a, 3-22b, 3-22c, and 3-23 are treated as useful reference and benchmark families, while juniorSE analyzes the actual beam system directly.

### Important analysis boundaries

Second-order analysis is currently an **elastic geometric-stiffness analysis aid**. It is not represented as a complete AISC 360-16 Direct Analysis Method implementation.

Torsion currently covers **Saint-Venant torsion only**. Restrained warping and associated warping stresses are not yet implemented.

When support settlement is present, juniorSE does not automatically treat absolute displacement as the applicable code deflection. The result is flagged because serviceability may need to be measured relative to the displaced support chord.

---

## Current AISC 360-16 design scope

The current steel design path uses AISC 360-16 and includes:

### Chapter B — Design requirements / section classification

- flexural-element classification for the currently supported doubly symmetric I-shaped/W-shape path
- compact, noncompact, and slender classification logic used to route the member to the applicable Chapter F path


### Chapter D — Tension members

- gross-section yielding
- net-section rupture
- effective net area supplied directly or calculated as `Ae = An × U`
- explicit shear-lag guardrail: juniorSE does not invent `U`
- ASD/LRFD available tension strength and DCR
- optional `L/r` advisory when member length and minimum radius of gyration are supplied

Connection block shear, bolt/weld strength, and connection design remain outside this skill.

### Chapter E — Compression members

- flexural buckling about both principal axes for supported doubly symmetric rolled and built-up I-shapes
- explicit `Kx` and `Ky`; juniorSE does not assume effective-length factors
- Chapter B axial-compression flange/web slenderness routing
- **E3** nonslender-member flexural buckling
- **E7** effective-width/effective-area treatment for supported slender I-shape flanges and webs
- ASD/LRFD available compression strength and DCR
- standardized `axial_strength_result` for Chapter H orchestration

Chapter E4 torsional/flexural-torsional buckling is not yet calculated. The skill requires that its applicability be explicitly reviewed rather than silently ignored.

### Axial-strength orchestration

`steel-axial-strength` provides a single signed-force interface for axial member checks:

- positive axial demand routes to `steel-tension-check` / Chapter D
- negative axial demand routes to `steel-compression-check` / Chapter E
- zero axial demand returns a zero-demand result without invoking a design chapter
- child-skill guardrails and blocked states are preserved
- the orchestrator does not duplicate Chapter D or Chapter E equations
- successful results are normalized into a common `axial_strength_result` contract for Chapter H interaction

The Phase 3C sign convention is explicit: `tension_positive`.

### Chapter F — Flexure

- **F2** — compact web / compact flange major-axis flexure
- **F3** — compact web with noncompact or slender flange
- **F4** — supported doubly symmetric I-shaped members with noncompact webs
- **F5** — supported doubly symmetric I-shaped members with slender webs
- **F6** — bounded minor-axis flexure for doubly symmetric I-shaped members, including yielding and flange local buckling
- yielding and lateral-torsional-buckling paths applicable to the implemented major-axis cases
- compression-flange local-buckling behavior for the implemented cases
- ASD/LRFD available strength and demand-capacity reporting


### Chapter H — Combined axial force and flexure

- **H1** interaction for the currently supported doubly symmetric I-shaped member path
- axial tension strength supplied by Chapter D through `steel-axial-strength`
- axial compression strength supplied by Chapter E through `steel-axial-strength`
- major-axis flexural strength supplied by `steel-flexure-check`
- minor-axis flexural strength supplied by `steel-minor-axis-flexure-check` / F6
- explicit routing between H1-1a and H1-1b based on axial utilization `Pr/Pc`
- component ratios `Pr/Pc`, `Mrx/Mcx`, and `Mry/Mcy` are reported separately
- required strengths must come from an explicitly acknowledged second-order or Chapter C-compatible analysis basis

The current Chapter H skill does **not** independently certify global Chapter C stability compliance and does not cover torsion or specialized H2/H3 interaction provisions.

### Chapter G — Shear

- unstiffened-web shear
- calculated `Cv1` for the implemented web-slenderness range
- ASD/LRFD available shear strength and DCR

### Chapter J10 — Web local checks

- **J10.2** web local yielding
- **J10.3** web local crippling

Support/connection bearing design is intentionally not included at this stage.

### Serviceability defaults

Current default beam deflection criteria are:

```text
Live load deflection        ≤ L/240
Dead + live load deflection ≤ L/360
```

These are explicit juniorSE defaults and should be overridden when project-specific criteria require something else.

---

## Demand-to-strength workflow

The generalized analysis engine now feeds the existing AISC strength modules through a standardized demand envelope.

For example:

```text
Actual beam + loading
        ↓
Beam analysis
        ↓
M+, M-, |M|max, Vmax, reactions, locations
        ↓
Chapter F flexure checks
Chapter G shear check
J10 local web checks where applicable
        ↓
Serviceability
        ↓
QA/QC
        ↓
Governing DCR + governing limit state + governing location
```

Positive and negative moments are preserved separately so continuous-beam behavior is not collapsed into one unsigned number.

Moving-load envelopes can feed the same strength workflow.

Torsional demand is reported separately and is **not** treated as fully covered by Chapters F, G, and J10.

---

## Verification and benchmark philosophy

juniorSE should not be considered trustworthy because an equation "looks right."

Every validated or executable skill should include tests that cover, where applicable:

- valid inputs
- missing critical inputs
- blocked unsupported conditions
- limit-state transitions
- unit consistency
- known-answer calculations
- regression cases
- independent benchmark problems

Where official worked examples exist, they are preferred benchmark sources.

For the current flexural implementation:

- the F4 path includes a regression benchmark based on **AISC 15th Edition Manual Companion v15.1, Volume 1, Example F.15 — Plate Girder Flexural Member**
- the Companion is keyed to ANSI/AISC 360-16
- no dedicated F5 slender-web Chapter F example was identified in the Companion examples used during development, so F5 is tested against the AISC 360-16 equation path and is **not** labeled as Companion-benchmarked

The distinction between an official worked-example benchmark and an equation-path test should remain explicit throughout the project.

---

## Guardrails and intentionally unsupported paths

The current library should block rather than improvise when a requested task falls outside the implemented scope.

Current notable limitations include:

- singly symmetric F4/F5 implementation
- composite beam design
- restrained-warping torsion
- torsional strength interaction
- Chapter E4 torsional/flexural-torsional compression buckling
- connection design
- bearing-plate design

These are roadmap items, not capabilities that should be inferred from adjacent implemented skills.

---

## Example behavior

A user should be able to give juniorSE a bounded task such as:

> Check this W-shape beam for the given loading using AISC 360-16 LRFD.

Before calculating, the applicable skills should determine whether enough information exists to proceed.

If critical information is missing, juniorSE should respond with something like:

```text
I cannot complete this check until the following are known:
- steel grade
- member section
- support condition
- lateral bracing / unbraced length
- load magnitudes and load status
- design method
```

When sufficient information exists, the workflow should produce:

1. task classification
2. input summary
3. assumptions
4. code/design basis
5. analysis results
6. strength checks
7. serviceability checks
8. governing limit state and DCR
9. QA/QC review
10. engineer-review notes

The objective is a result that a structural engineer can review—not an opaque answer that must be reconstructed from scratch.

---

## Roadmap

The next major steel milestone is **Phase 3D: Chapter H axial + flexure interaction**, using the standardized axial-strength interface from Phase 3C.

Planned areas include:

- expanded Chapter E shape families and Chapter E4 buckling
- integration of standardized axial strength with major/minor-axis flexure
- biaxial interaction
- expanded torsional design behavior
- additional steel-member and system skills
- concrete design skills
- wood / NDS design skills
- broader loading, wind, seismic, diaphragm, drift, and lateral-system workflows
- calculation-package generation and review
- code-navigation and code-reasoning skills

The long-term goal is not a single steel-beam calculator. It is a broad, reusable structural design and analysis skill library that AI agents can build on while remaining explicit about scope, assumptions, and engineer supervision.

---

## Contributing

Contributions should improve engineering reliability, not merely add more output.

When proposing a new validated or executable skill, include:

- a clear trigger and scope
- required inputs
- explicit stop conditions
- supported and unsupported paths
- `SKILL.md`
- `rules.yaml`
- `validator.py`
- `examples/`
- `tests/`
- `calculator.py` when the skill performs calculations
- code references or benchmark basis where applicable

New engineering paths should be benchmarked against reliable worked examples or independently verified calculations whenever possible.

If a contribution cannot support a condition safely, the skill should block that condition rather than silently approximate it.

---

## Engineering responsibility

juniorSE is intended for **engineer-supervised workflows**.

Outputs require review by a qualified structural engineer and are not a substitute for:

- project-specific code interpretation
- engineering judgment
- construction-document review
- professional responsibility
- responsible charge by the engineer of record

The project is designed to make AI-assisted structural work more disciplined, transparent, testable, and reviewable—not autonomous.
