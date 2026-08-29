# Agents (subagent definitions)

Each file in this directory is a **subagent definition**: a short Markdown spec that
turns a generic agent runtime into a focused worker for a specific role. Eve mounts this
directory at `.claude/agents` (or the equivalent in your runtime) so that subagents can
be loaded directly.

## File format

Every subagent file follows this shape (see `templates/agent-template.md`):

```markdown
---
name: <agent-identifier, lowercase-kebab, e.g. backend-engineer>
description: <one-line description, including when Eve should pick this agent>
skills:
  - find-skills
  - skill-creator
---

## Role

<One paragraph: this agent's domain of expertise and behavioral boundaries.>

## Skills

<Concrete skills this agent relies on. Keep it aligned with what is installed under
`skills/`. Eve refreshes this list at dispatch time.>

## Workflow constraints

<Read-only vs writable paths; subordinance to `workflows/subagent-workflow.md`;
boundaries vs other agents.>

## Output format

<Where progress is written (the Task file's "Execution log" table); where conclusions
go ("Conclusions and output"); how to surface knowledge-capture suggestions.>
```

## Adding a new subagent

1. **Pick a single, focused role.** Subagents work best when they have a clear domain
   ("backend engineer", "QA verifier", "data analyst"). Avoid kitchen-sink agents.
2. **Copy `templates/agent-template.md`** to `<name>.md` in this directory.
3. **Fill the frontmatter.** `name` must match the filename. `description` should make
   it obvious when Eve should dispatch *this* agent and not another.
4. **List only the skills the agent actually uses**, and make sure those skills are
   installed under `skills/`. Eve keeps this list current at each dispatch.
5. **Keep the file short.** Detailed procedures belong in a `handbooks/<topic>.md`;
   domain facts belong in `knowledge/<topic>/`. The agent file is an identity card, not
   a manual.

## Bundled example

- [`workspace-archivist.md`](./workspace-archivist.md) — the only subagent shipped with
  the open-source skeleton. It reorganizes knowledge, archive, sessions, and artifacts
  in line with the workspace protocols. Use it as a reference for how to scope your own
  agents.

## Maintenance

- Eve owns the final edit on every agent file.
- Subagents propose changes (e.g. "please add this skill to my list") in their Task's
  "Conclusions and output"; they do not edit agent files directly.
- When a subagent is retired, its file is moved to `archive/agents/<slug>.md` rather
  than deleted, so historical references stay valid.
