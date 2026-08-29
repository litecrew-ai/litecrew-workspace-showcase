# Handbooks (domain process playbooks)

This directory holds **domain process playbooks** — process-oriented "how to do" guides
with steps and norms that guide future work. The boundary vs `knowledge/` (discrete "what
to know" — experience and technical detail) is described in `knowledge/README.md` under
"Knowledge vs Handbooks".

> **One-line rule**: a handbook is **navigation + decision tree + per-stage artifacts**;
> knowledge is the **detail pool**. After reading a handbook, a new subagent should know
> "which phases, which knowledge to read in each, what the artifact is, and which
> knowledge the key decisions live in" — concrete numbers, templates, and failure modes
> are looked up in knowledge.

## How to write a new handbook (checklist, mandatory)

- [ ] **Right boundary.** Process content (how to), not discrete experience (what is) —
      the latter goes to knowledge.
- [ ] **Per-paragraph body ≤ 10 lines**; anything longer is split out to knowledge.
- [ ] **Per-stage artifact called out.**
- [ ] **Decision tree drawn in a code block** (branch by scenario / quality / duration).
- [ ] **References to knowledge use relative paths**, e.g.
      `knowledge/<your-business-1>/<topic>/<slug>.md`.
- [ ] **End with "Last updated + maintenance notes."**

## Current handbooks

> The open-source skeleton ships none. Add your own as your workspace matures. A row in
> the table below is the canonical way to register a new handbook.

| Handbook                    | Scope                          | Status |
| --------------------------- | ------------------------------ | ------ |
| _(none yet — add your own)_ |                                |        |

## Backlog (candidate handbooks, ordered by Eve)

> When a Task exposes a missing "how to", Eve either writes the handbook immediately or
> logs it here for later.

- _(empty)_

## Organization

A handbook may be **a single Markdown file or a directory of related files** (e.g. a
future `publish-ops/` could be split into `xhs.md`, `bilibili.md`, `twitter.md`). Simple
domains are one file; complex domains expand to a subdirectory.

## Who maintains handbooks

- **Eve** owns the final edit. Eve updates handbooks based on subagent suggestions or
  pro-active review.
- **Subagents** propose concrete revisions (old → new, or new section) inside their
  Task's "Conclusions and output" — they **do not edit handbooks directly**, unless Eve
  explicitly authorizes it in the Task (e.g. workspace-archivist during a workspace
  reorg).
- **workspace-archivist** may create or edit handbooks during a big rearrange, but must
  follow the "navigation not detail" rule (body paragraphs ≤ 10 lines + knowledge link).
