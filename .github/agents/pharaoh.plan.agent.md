---
description: Use when breaking requirement changes into structured implementation tasks with workflow enforcement and dependency ordering
handoffs:
  - label: Start Change Analysis
    agent: pharaoh.change
    prompt: Analyze the impact of the planned changes
  - label: Author the planned needs
    agent: pharaoh.author
    prompt: Author the needs identified in this plan, one per task
  - label: Verify the authored needs
    agent: pharaoh.verify
    prompt: Verify the authored needs against their parents and review axes
---

# @pharaoh.plan

Use when breaking requirement changes into structured implementation tasks with workflow enforcement and dependency ordering.

See [`skills/pharaoh-plan/SKILL.md`](skills/pharaoh-plan/SKILL.md) for the full atomic specification — inputs, outputs, atomicity contract, and composition patterns.

Related skills: [`pharaoh-write-plan`](skills/pharaoh-write-plan/SKILL.md) emits a `plan.yaml` from an intent; [`pharaoh-execute-plan`](skills/pharaoh-execute-plan/SKILL.md) is the generic DAG executor that runs it. Use those when authoring or running a Pharaoh plan-file pipeline.
