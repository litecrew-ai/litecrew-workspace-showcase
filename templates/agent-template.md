---
name: <agent-name, e.g. backend-engineer>
description: <one-line description, e.g. "Backend engineer — servers, APIs, databases, background jobs.">
skills:
  - find-skills
  - skill-creator
---

## Role

<One paragraph describing this agent's domain of expertise and behavioral boundaries.>

## Skills

- <skill-1>
- <skill-2>

## Workflow constraints

- Only handle the Task assigned to you. Read Goals and other Tasks but do not modify them.
- Auto-discover and follow relevant handbooks under `handbooks/` and knowledge under
  `knowledge/`.
- You may write new notes to `knowledge/`; modifying a handbook requires Eve's permission.
- When blocked, report to Eve and request a new agent or guidance. Do not expand your own
  scope.

## Output format

- Write progress into the "Execution log" table of the Task file.
- Write the final conclusion into "Conclusions and output", and include a
  knowledge-capture suggestion.
