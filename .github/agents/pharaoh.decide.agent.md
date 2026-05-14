---
description: Use when recording a design decision as a traceable sphinx-needs object with alternatives, rationale, and links to affected requirements
handoffs:
  - label: Trace Decision
    agent: pharaoh.trace
    prompt: Trace the decision through all linked needs
  - label: Generate Spec
    agent: pharaoh.spec
    prompt: Generate a spec document from the affected requirements
---

# @pharaoh.decide

Use when recording a design decision as a traceable sphinx-needs object with alternatives, rationale, and links to affected requirements.

See [`skills/pharaoh-decide/SKILL.md`](skills/pharaoh-decide/SKILL.md) for the full atomic specification — inputs, outputs, atomicity contract, and composition patterns.
