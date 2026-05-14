# Traceable Documentation for RemotiveLabs Topology

Hey team! This folder contains a **Sphinx-Needs** documentation project that adds ISO 26262-style traceability to our topology examples. This README walks you through what it is, how to use it, and what tools are available.

---

## What is Sphinx-Needs?

[Sphinx-Needs](https://sphinx-needs.readthedocs.io/) is an extension for [Sphinx](https://www.sphinx-doc.org/) (the Python documentation framework) that lets you create **structured, traceable engineering objects** — called "needs" — directly in `.rst` files. Think of it as requirements management inside your repo, version-controlled with Git.

A "need" looks like this in RST:

```rst
.. sysreq:: Hazard Light Safety
   :id: SYSREQ_HAZARD_LIGHT_SAFETY
   :status: draft
   :asil: B
   :satisfies: FEAT_STATE_MACHINE

   When the hazard light button is activated, the Body Control
   Module shall command simultaneous left and right turn indicator
   activation within one signal processing cycle.
```

This creates a requirement with a unique ID, metadata fields (status, ASIL rating), and a **traceability link** (`:satisfies:`) to a parent feature. Sphinx-Needs renders these as styled cards in HTML and tracks all the relationships.

### What we defined

The project currently has **124 needs** across 9 types:

| Type | Prefix | Count | Purpose |
|------|--------|-------|---------|
| Feature | `FEAT_` | 13 | User-facing capabilities from our docs |
| System Requirement | `SYSREQ_` | 12 | What the system shall do |
| Component Requirement | `COMP_REQ_` | 21 | What each ECU/module shall do |
| Architecture Element | `ARCH_` | 10 | Subsystem designs |
| ECU | `ECU_` | 13 | All 13 ECUs from the platform |
| Channel | `CH_` | 5 | Communication channels (CAN, LIN, SOME/IP) |
| Behavioral Model | `MDL_` | 6 | Behavioural models (Python or declarative) |
| Test Case | `TC_` | 35 | Verification test cases (4 in `draft` pending stimulus implementation) |
| FMEA Entry | `FMEA_` | 9 | Failure mode analysis |

### Traceability chain

```
Feature ← (satisfies) ← System Req ← (satisfies) ← Component Req ← (verifies) ← Test Case
                                                          ↑
                                               (mitigates) FMEA Entry
```

Every component requirement traces up to a system requirement, which traces up to a feature. Every component requirement has at least one test case. Safety-critical paths have FMEA entries.

---

## Demo provenance and review independence (ISO 26262-8 §6.4.6 caveat)

The 11 safety-relevant approved needs in this corpus carry
`:reviewer:` and `:approved_by:` role assignments (Max Pabinger and
Bartosz Burda respectively). ISO 26262-8 §6.4.6 additionally requires
independence of the reviewer and approver **from the author of the
requirement**. This demo corpus does not currently record an
`:author:` field, so independence-of-author cannot be verified from
the artefacts alone.

For a production deliverable an audit log would establish that
neither Max nor Bartosz authored the items they reviewed and
approved. For this useblocks × RemotiveLabs partnership example the
review/approval roles are illustrative of the §6.4.6 mechanism, not a
substantive compliance claim.

### Test-case scope honesty

Four test cases ship with `:status: draft` because their cited test
artefacts do not yet implement the verification steps the TC describes:

| TC | Verifies | Why draft |
|----|----------|-----------|
| `TC_BLINK_TIMING` | `COMP_REQ_BCM_TURN_BLINK` | Cited unit test exercises state-machine transitions only; numerical cadence measurement (1.0-2.0 Hz, 40-60 % duty) is not yet implemented |
| `TC_BRAKE_LIGHT` | `COMP_REQ_BCM_BRAKE_LIGHT` | Brake-pedal stimulus is not yet present in the cited pytest test path |
| `TC_SYS_BRAKE_LIGHT` | `SYSREQ_BRAKE_LIGHT_SAFETY` | Same — system-level brake-light integration test not yet implemented |
| `TC_TURN_SM_OUTPUTS` | `COMP_REQ_BCM_TURN_SM` | Complements `TC_TURN_SM` by adding BodyCan0 output verification on top of the state-machine state-name verification; integration scenario not yet present |

Each `draft` TC carries a `**Note:**` paragraph explicitly stating
what is missing and which file is the intended home for the test
implementation. The associated requirements remain `approved` because
their content is fixed; only the verification evidence is pending.

---

## How to build the documentation

### Prerequisites

```bash
pip install -r docs/requirements.txt
```

This pins the version set the corpus has been built and validated
against (sphinx >= 8, sphinx-needs >= 8, sphinxcontrib-mermaid,
sphinxcontrib-plantuml, furo, Pillow). `Pillow` is required by
PlantUML rendering used inside `needflow`.

### Build HTML

From the repo root:

```bash
cd docs
sphinx-build -W -b html . _build/html
```

`-W` treats every warning as an error — the corpus should build clean.
The HTML output lands in `docs/_build/html/`. Open
`docs/_build/html/index.html` in a browser, or serve it locally:

```bash
cd docs/_build/html
python3 -m http.server 8080
# Then open http://localhost:8080
```

You should see zero warnings. If you get a schema violation, that means someone introduced an invalid value (like an ASIL rating that isn't QM/A/B/C/D) — which is exactly what the validation is for.

---

## Key configuration files

| File | What it does |
|------|-------------|
| `conf.py` | Sphinx configuration — sets the Furo theme, loads sphinx-needs, points to `ubproject.toml` |
| `ubproject.toml` | **Single source of truth** for all need types, link types, and custom fields. Sphinx-needs reads this via `needs_from_toml` |
| `schemas.json` | Validation rules that run at build time (see below) |
| `pharaoh.toml` | Pharaoh framework config (reverse-engineering mode) |
| `.pharaoh/project/` | Tailoring files — ID conventions, workflows, artefact catalog, review checklists |

---

## Schema validation (`schemas.json`)

We have **13 validation rules** that run automatically on every `sphinx-build`. They catch problems early — before a PR is merged.

### Completeness rules (warnings)

These fire when required metadata is missing:

- **`sysreq-needs-asil`** — System requirements must have an ASIL rating
- **`comp-req-needs-asil`** — Component requirements must have an ASIL rating
- **`tc-must-have-verification-method`** — Test cases must specify how they verify (test, review, analysis, inspection)
- **`channel-must-have-protocol`** — Channels must declare their protocol (CAN, LIN, SOME/IP)

### Traceability rules (warnings)

These fire when traceability links are missing:

- **`sysreq-must-satisfy-feature`** — Every system requirement should link up to a feature
- **`comp-req-must-satisfy-sysreq`** — Every component requirement should link up to a system requirement
- **`tc-must-verify-something`** — Every test case should link to what it verifies
- **`fmea-must-mitigate`** — Every FMEA entry should link to what it mitigates

### Safety integrity rules (violations — build errors)

These are the serious ones:

- **`sysreq-asil-valid-value`** — ASIL must be one of: QM, A, B, C, D. Catches typos like `:asil: X`
- **`comp-req-asil-valid-value`** — Same for component requirements
- **`comp-req-satisfies-sysreq-type`** — Component requirements can only `:satisfies:` needs of type `sysreq` or `feat` (prevents linking to the wrong kind of need)
- **`fmea-must-have-ratings`** — FMEA entries must have severity, occurrence, and detection ratings
- **`safety-comp-req-traces-to-safe-sysreq`** — If a component requirement has ASIL A–D, at least one of its `:satisfies:` targets must *also* be ASIL A–D. This catches safety decomposition gaps.

### Try it yourself

Set `:asil: X` on any system requirement and rebuild. You'll see:

```
ERROR: Need 'SYSREQ_xxx' has schema violations:
  Severity:       violation
  User message:   ASIL rating must be one of: QM, A, B, C, D (ISO 26262)
```

---

## Using ubCode (VS Code extension)

[ubCode](https://ubcode.useblocks.com/) is a VS Code extension by useblocks that gives you a **live editing experience** for sphinx-needs projects. Install it from the VS Code marketplace.

### What it does

- **Live preview** — See how your needs render as you type, in under 0.2 seconds
- **Diagnostics panel** — The `schemas.json` rules run live in VS Code. Open the **Problems** panel (`Ctrl+Shift+M`) to see violations and warnings as you edit, without needing to run a full `sphinx-build`
- **Autocomplete** — Suggests need IDs when you type `:satisfies:`, `:verifies:`, etc.
- **Navigation** — Click on a need ID to jump to its definition
- **Validation** — Catches duplicate IDs, broken links, missing required fields

### The diagnostics view

When you open any `.rst` file in this project with ubCode installed, the Problems panel will show:

- **Violations** (red) — Invalid ASIL values, missing FMEA ratings, wrong link target types
- **Warnings** (yellow) — Missing traceability links, missing metadata fields

These come directly from `schemas.json`. If you add a new need and forget to set `:asil:`, you'll see a yellow warning immediately. If you set `:asil: X`, you'll see a red violation. No build required.

### Setup

1. Install the [ubCode extension](https://marketplace.visualstudio.com/items?itemName=useblocks.ubcode) in VS Code
2. Open this repo in VS Code
3. The extension auto-detects `ubproject.toml` and `schemas.json`
4. Start editing `.rst` files — diagnostics appear automatically

---

## Pharaoh — the AI agent framework

[Pharaoh](https://github.com/useblocks/pharaoh) is an AI-native requirements engineering framework by useblocks. It's **not a CLI tool you install** — it's a collection of skill instructions (`.md` files) that an AI agent reads and executes. The AI is the runtime.

### What we used it for

This entire documentation was generated by executing Pharaoh skills:

1. **pharaoh-setup** — Detected the project structure, scaffolded Sphinx config
2. **pharaoh-bootstrap** — Created `conf.py` and `ubproject.toml` with the right types
3. **pharaoh-tailor-bootstrap** — Generated ID conventions, workflows, and review checklists
4. **pharaoh-feat-draft-from-docs** — Read README.md and DOCS.md, extracted 13 features
5. **pharaoh-req-from-code** — Read BCM, GWM, SCCM source code, emitted component requirements with proper shall-clause form
6. **pharaoh-arch-draft** — Created architecture elements from the platform topology
7. **pharaoh-vplan-draft** — Generated test cases with preconditions, steps, and expected outcomes
8. **pharaoh-fmea** — Derived failure modes for safety-critical paths
9. **pharaoh-mece** — Ran gap analysis to find missing traceability links

### The 73 Copilot agents

We installed 73 Pharaoh agent files in `.github/agents/`. These are Copilot Workspace agents that you can invoke by name. Some useful ones:

| Agent | What it does |
|-------|-------------|
| `@pharaoh.req-from-code` | Read a source file, emit component requirements |
| `@pharaoh.req-review` | Review a requirement against the ISO 26262 checklist |
| `@pharaoh.arch-draft` | Derive an architecture element from a requirement |
| `@pharaoh.vplan-draft` | Create a test case for a requirement |
| `@pharaoh.fmea` | Derive a failure mode entry |
| `@pharaoh.mece` | Run gap analysis across all needs |
| `@pharaoh.diagram-lint` | Validate Mermaid/PlantUML diagrams |
| `@pharaoh.quality-gate` | Full quality check (build + schema + traceability) |

### How to use Pharaoh agents

In VS Code with GitHub Copilot, you can invoke an agent in chat:

```
@pharaoh.req-from-code Read remotive_car/models/bcm/python/bcm/__main__.py and emit component requirements
```

The agent reads its SKILL.md instructions and follows the exact procedure — proper shall-clause form, no internal implementation details, correct ID prefixes, traceability links.

### Papyrus prerequisite for rationale-aware agents

Six of the shipped agents read from or write to a [Papyrus](https://github.com/useblocks/papyrus) workspace — a sidecar memory store that holds decisions, findings, and project-specific terms linked to sphinx-needs IDs:

| Agent | What it uses Papyrus for |
|-------|--------------------------|
| `@pharaoh.papyrus-non-empty-check` | Verifies a Papyrus workspace exists before audit fan-out |
| `@pharaoh.context-gather` | Retrieves rationale memories relevant to the authoring context |
| `@pharaoh.decision-record` | Persists canonical decisions / facts / preferences |
| `@pharaoh.finding-record` | Persists audit findings with dedup on `(category, subject_id)` |
| `@pharaoh.audit-fanout` | Routes per-need audits and aggregates findings via Papyrus |
| `@pharaoh.req-from-code` | Looks up canonical concept names before naming new requirements |

Bootstrap a workspace at the repo root before invoking any of these:

```bash
pip install papyrus      # or: uv pip install papyrus
papyrus init .papyrus/
```

For semantic recall (used by `@pharaoh.context-gather`):

```bash
pip install "papyrus[semantic]"
papyrus --workspace .papyrus rebuild-index
```

The `.papyrus/` directory is already listed in `.gitignore` — the rationale store stays local by default. Share it across the team explicitly by removing the ignore entry once your conventions are settled.

---

## Directory structure

```
docs/
├── conf.py                    # Sphinx config
├── ubproject.toml             # Need types, links, fields
├── schemas.json               # 13 validation rules
├── pharaoh.toml               # Pharaoh framework config
├── requirements.txt           # Pinned build dependencies
├── index.rst                  # Landing page
├── features/                  # 13 feature needs
├── requirements/              # 12 system + 21 component requirements
├── architecture/              # 10 arch elements + 13 ECUs + 5 channels + 6 models
├── verification/              # 35 test cases (31 reviewed, 4 draft)
├── fmea/                      # 9 FMEA entries
├── _static/                   # Logos, CSS (useblocks brand colors)
└── .pharaoh/project/          # Tailoring (ID conventions, workflows, checklists)
```

---

## Quick reference

| Task | Command |
|------|---------|
| Build HTML | `cd docs && sphinx-build -b html . _build` |
| Serve locally | `cd docs/_build && python3 -m http.server 8080` |
| Count all needs | `grep -rh '^\.\. ' docs/ --include='*.rst' \| grep '::' \| wc -l` |
| Check traceability gaps | Run `@pharaoh.mece` in Copilot chat |
| Add a new requirement | Copy an existing one, change ID/title/body, add `:satisfies:` link |
| Validate without building | Open the file in VS Code with ubCode installed |

---

## Links

- [Sphinx-Needs docs](https://sphinx-needs.readthedocs.io/)
- [ubCode docs](https://ubcode.useblocks.com/)
- [useblocks website](https://useblocks.com/)
- [Pharaoh on GitHub](https://github.com/useblocks/pharaoh)
- [RemotiveLabs docs](https://docs.remotivelabs.com/)
