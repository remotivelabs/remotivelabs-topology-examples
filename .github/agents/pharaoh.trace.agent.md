---
description: Use when navigating traceability links between requirements, specifications, implementations, tests, and code in a sphinx-needs project
handoffs:
  - label: Analyze Impact
    agent: pharaoh.change
    prompt: Analyze the impact of changing this requirement
  - label: Check Gaps
    agent: pharaoh.mece
    prompt: Check for traceability gaps in this area
---

# @pharaoh.trace

Use when navigating traceability links between requirements, specifications, implementations, tests, and code in a sphinx-needs project.

See [`skills/pharaoh-trace/SKILL.md`](skills/pharaoh-trace/SKILL.md) for the full atomic specification — inputs, outputs, atomicity contract, and composition patterns.
