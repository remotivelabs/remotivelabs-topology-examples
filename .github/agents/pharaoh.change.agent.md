---
description: Use when analyzing the impact of changing a requirement, specification, or any sphinx-needs item, including traceability to code via codelinks
handoffs:
  - label: Author the affected needs
    agent: pharaoh.author
    prompt: Author the needs flagged in this change analysis
  - label: Verify the affected needs
    agent: pharaoh.verify
    prompt: Verify the authored needs against their parents and review axes
  - label: MECE Check
    agent: pharaoh.mece
    prompt: Check the affected area for gaps and redundancies
  - label: Trace Requirement
    agent: pharaoh.trace
    prompt: Trace the changed requirement through all levels
---

# @pharaoh.change

Use when analyzing the impact of changing a requirement, specification, or any sphinx-needs item, including traceability to code via codelinks.

See [`skills/pharaoh-change/SKILL.md`](skills/pharaoh-change/SKILL.md) for the full atomic specification — inputs, outputs, atomicity contract, and composition patterns.
