---
description: Use when setting up Pharaoh in a sphinx-needs project for the first time, scaffolding Copilot agents, or reconfiguring project detection
handoffs:
  - label: Run MECE Check
    agent: pharaoh.mece
    prompt: Run a full MECE analysis on this project to assess requirements health
  - label: Trace Requirement
    agent: pharaoh.trace
    prompt: Trace a requirement through all levels
---

# @pharaoh.setup

Use when setting up Pharaoh in a sphinx-needs project for the first time, scaffolding Copilot agents, or reconfiguring project detection.

See [`skills/pharaoh-setup/SKILL.md`](skills/pharaoh-setup/SKILL.md) for the full atomic specification — inputs, outputs, atomicity contract, and composition patterns.
