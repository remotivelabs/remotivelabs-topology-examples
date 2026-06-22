# RemotiveCar Traceable Documentation

This folder contains a **Sphinx-Needs** documentation project that adds ISO 26262-style traceability to this example, developed in collaboration with [useblocks](https://useblocks.com/). Notice that this is just a limited sample of what the full documentation would look like. The goal is to show how this type of documentation can be added when working with RemotiveTopology.

This README walks you through what it is, how to use it, and what tools are available.

## What is Sphinx-Needs?

[Sphinx-Needs](https://sphinx-needs.readthedocs.io/) is an extension for [Sphinx](https://www.sphinx-doc.org/) (the Python documentation framework) that lets you create **structured, traceable engineering objects** — called "needs" — directly in `.rst` files. Think of it as requirements management inside your repo, version-controlled with Git.

A "need" looks like this in RST:

```rst
.. sysreq:: Hazard Light Safety
   :id: SYSREQ_HAZARD_LIGHT_SAFETY
   :status: draft
   :asil: B

   When the hazard light button is activated, the Body Control
   Module shall command simultaneous left and right turn indicator
   activation within one signal processing cycle.
```

This creates a requirement with a unique ID, metadata fields (status, ASIL rating), and a **traceability link** (`:satisfies:`) to a parent feature. Sphinx-Needs renders these as styled cards in HTML and tracks all the relationships.

### Defined needs

The project currently has a number of needs across 9 types:

| Type                  | Prefix      | Count | Purpose                                                                |
| --------------------- | ----------- | ----- | ---------------------------------------------------------------------- |
| Feature               | `FEAT_`     | 13    | User-facing capabilities from our docs                                 |
| System Requirement    | `SYSREQ_`   | 12    | What the system shall do                                               |
| Component Requirement | `COMP_REQ_` | 21    | What each ECU/module shall do                                          |
| Architecture Element  | `ARCH_`     | 10    | Subsystem designs                                                      |
| ECU                   | `ECU_`      | 13    | All 13 ECUs from the platform                                          |
| Channel               | `CH_`       | 5     | Communication channels (CAN, LIN, SOME/IP)                             |
| Behavioral Model      | `MDL_`      | 6     | Behavioural models (Python or declarative)                             |
| Test Case             | `TC_`       | 35    | Verification test cases (4 in `draft` pending stimulus implementation) |
| FMEA Entry            | `FMEA_`     | 9     | Failure mode analysis                                                  |

### Traceability chain

```
Feature ← (satisfies) ← System Req ← (satisfies) ← Component Req ← (verifies) ← Test Case
                                                          ↑
                                               (mitigates) FMEA Entry
```

Every component requirement traces up to a system requirement, which traces up to a feature. Every component requirement has at least one test case. Safety-critical paths have FMEA entries.

## How to build the documentation

### Prerequisites

1. (Install plantuml)[https://plantuml.com/starting]
2. Install python 3.10 or later
3. Install python depdendencies, see below

```bash
cd remotive_car
pip install -r docs/requirements.txt
```

This pins the version set the corpus has been built and validated
against (sphinx >= 8, sphinx-needs >= 8, sphinxcontrib-mermaid,
sphinxcontrib-plantuml, furo, Pillow). `Pillow` is required by
PlantUML rendering used inside `needflow`.

### Build HTML

From the repo root:

```bash
cd remotive_car
sphinx-build -W -b html docs build/html
```

`-W` treats every warning as an error — the corpus should build clean.
The HTML output lands in `build/html/`. Open
`build/html/index.html` in a browser, or serve it locally:

```bash
cd build/html
python3 -m http.server 8080
# Then open http://localhost:8080
```

You should see zero warnings. If you get a schema violation, that means someone introduced an invalid value (like an ASIL rating that isn't QM/A/B/C/D) — which is exactly what the validation is for.

## Key configuration files

| File             | What it does                                                                                                                |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `conf.py`        | Sphinx configuration — sets the Furo theme, loads sphinx-needs, points to `ubproject.toml`                                  |
| `ubproject.toml` | **Single source of truth** for all need types, link types, and custom fields. Sphinx-needs reads this via `needs_from_toml` |
| `schemas.json`   | Validation rules that run at build time (see below)                                                                         |

## Schema validation (`schemas.json`)

The example include **13 validation rules** that run automatically on every `sphinx-build`. They catch problems early — before a PR is merged.

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
- **`safety-comp-req-traces-to-safe-sysreq`** — If a component requirement has ASIL A–D, at least one of its `:satisfies:` targets must _also_ be ASIL A–D. This catches safety decomposition gaps.

### Try it yourself

Set `:asil: X` on any system requirement and rebuild. You'll see:

```
ERROR: Need 'SYSREQ_xxx' has schema violations:
  Severity:       violation
  User message:   ASIL rating must be one of: QM, A, B, C, D (ISO 26262)
```

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

## Links

- [Sphinx-Needs docs](https://sphinx-needs.readthedocs.io/)
- [ubCode docs](https://ubcode.useblocks.com/)
- [useblocks website](https://useblocks.com/)
