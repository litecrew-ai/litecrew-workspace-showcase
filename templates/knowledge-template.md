---
subject: <topic subdirectory, e.g. <your-business-1>/engines or workspace/tools>
slug: <filename without .md, e.g. engine-static-brief>
tags: [tag1, tag2, tag3]                       # Free-form tags for cross-topic retrieval; lowercase engine / tool names
related_goals: [<goal-slug>]                   # optional; filename under goals/
related_tasks: [<task-slug>]                   # optional; filename under tasks/ or archive/
related_knowledge: [<topic>/<slug>.md]         # optional; pointer to other knowledge files
last_verified_date: YYYY-MM-DD                 # Last date this was tested / re-verified; Eve re-checks after 90 days
status: active                                 # active / deprecated / superseded-by-<path>
---

# <Title: one sentence stating what this knowledge is about>

> One-paragraph elevator pitch: what problem does this knowledge solve, and what will the
> reader get out of it?

## Background and trigger conditions

When would you need this knowledge? Typical symptoms / error messages / trigger
conditions.

## Core conclusion

Give the answer / config / operation steps directly so the reader can act within 30
seconds.

## Detailed explanation

### Symptom

### Root cause

### Fix

### Verification

## Boundaries and counter-examples

When does this conclusion not apply? Known failure modes?

## Reuse checklist

- [ ] Check item 1
- [ ] Check item 2

## Related

- Upstream knowledge: `[[<topic>/<slug>]]`
- Downstream application: `[[<task-slug>]]` / `[[<goal-slug>]]`
- Backlinks (auto-formed from other files' `related_knowledge`)

## Change history

| Date       | Change                                       | Triggered by (Task / Goal) |
| ---------- | -------------------------------------------- | -------------------------- |
| YYYY-MM-DD | Initial version                              | archive/xxx.md             |
| YYYY-MM-DD | Added §3 boundary (a found infeasible case)  | archive/yyy.md             |
