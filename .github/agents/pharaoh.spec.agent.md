---
description: Use when generating a Superpowers-compatible spec and plan document from sphinx-needs requirements, bridging requirements to implementation
handoffs:
  - label: Execute Plan
    agent: pharaoh.plan
    prompt: Execute the plan table from the generated spec
  - label: Record Decision
    agent: pharaoh.decide
    prompt: Record a design decision for a gap in the requirements
  - label: MECE Check
    agent: pharaoh.mece
    prompt: Check for traceability gaps in the spec scope
---

# @pharaoh.spec

Use when generating a Superpowers-compatible spec and plan document from sphinx-needs requirements, bridging requirements to implementation.

See [`skills/pharaoh-spec/SKILL.md`](skills/pharaoh-spec/SKILL.md) for the full atomic specification — inputs, outputs, atomicity contract, and composition patterns.
