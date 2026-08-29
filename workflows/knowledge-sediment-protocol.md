# Knowledge sediment protocol

> **This file is for everyone who writes to `./knowledge/` (Eve and subagents).** It
> turns "capture knowledge" from a slogan into a checkable gate.
> Before Eve closes a Task, walk the §5 audit checklist. Any unmet item sends the Task
> back to the subagent for an in-turn fix — **never "close now, top up later"**.

---

## 0. Why this protocol exists

Without an enforced rule, knowledge directories converge to flat dumps of prefixed
filenames (multiple files about the same topic spread across different prefixes, with no
clear ownership or discoverability). The root cause is "encourage, don't enforce" —
subagents do not know where to write, so they dump at the root and invent their own
prefixes.

The goal of this protocol is: **place every new piece of knowledge correctly the moment
it is written**, instead of cleaning up afterwards.

---

## 1. Business subdirectories (business)

`knowledge/` uses a **business-first** layout: top-level directories are **business
domains** (not technical topics), so a reader can tell at a glance "which business this
serves". Only when one business grows too crowded do we split a second level (a technical
subdirectory).

### 1.1 Picking your business directories

The shipped workspace is empty by design. You decide your own business domains. Pick a
small set (typically 2–5) that match your actual work. Placeholder examples:

| business              | Serves Goal                          | Holds                                                                  | Split second level?                   |
| --------------------- | ------------------------------------ | ---------------------------------------------------------------------- | ------------------------------------- |
| `<your-business-1>/`  | your first long-term Goal            | Full-stack notes for that business (engine capabilities, pipelines, evaluation, platforms) | Once ≥ 10 files                       |
| `<your-business-2>/`  | your second long-term Goal           | Domain operations, playbooks, benchmarks                               | No (until it grows)                   |
| `workspace/`          | shared across businesses             | Workspace infrastructure (tooling, skill usage, generic traps)         | Once ≥ 10 files (e.g. infra/skills/tools) |
| `meta/`               | the workspace itself                 | Protocol notes, naming conventions, migration logs                     | No                                    |

### 1.2 When to split a second level (the writer decides)

- **Top-level directory has ≥ 10 files**: consider splitting by technical axis (e.g.
  `engines/` `evaluation/` `pipeline/` `platforms/`).
- **Top-level directory has < 10 files**: keep flat, do not split.
- **When adding a new file**: if a second-level directory already exists for the
  business, drop the file there; if not and the top level is under 10, drop it at the
  top level; if not and the top level has reached 10, the subagent creates the new
  second level (mirroring the split pattern of existing businesses) and updates the
  INDEX.

**Principle**: the top-level business directory is stable; second levels grow on demand.
A subagent that introduces a new second level must explain "why this split" in the Task
report.

### 1.3 Adding a new top-level business

Decided by Eve. Triggers: a new long-term Goal appears, or some business has already
accumulated ≥ 5 knowledge notes currently filed under `workspace/`.

### 1.4 Cross-business knowledge

If a note naturally spans two businesses (e.g. a generic tool used by both), **file it
under the single primary business** (the one where readers are most likely to look for
it), and add a pointer from the other business's `INDEX.md`.

---

## 2. Naming conventions

### 2.1 Slug format

```
<primary-keyword>-<specific-point>.md
```

- All lowercase, hyphen-separated, no date prefix (the date goes in frontmatter
  `last_verified_date`).
- Do not use Task-internal code prefixes (no `m9-`, `g01-`, etc.) — those are internal
  Task numbers and have nothing to do with discoverability.
- When a tool or engine name is the keyword, use the public name; internal project codes
  go in `tags`.

### 2.2 Anti-patterns → corrections

| Anti-pattern                              | Better                                    | Why                                            |
| ----------------------------------------- | ----------------------------------------- | ---------------------------------------------- |
| `t42-prop-benchmark.md`                   | `<biz>/prop-anatomy-limits.md`            | Drop the Task code, name by capability axis    |
| `internal-g01-distilled-fight.md`         | `<biz>/distilled-fight-behavior.md`       | Drop internal project codes                    |
| `random-tool-cdn-workaround.md`           | `workspace/tools/<tool>-cdn-workaround.md`| Tool traps belong in workspace/tools           |
| `keep-alive-decoupled.md`                 | `workspace/infra/keep-alive-decoupled.md` | Infrastructure belongs in workspace/infra      |

### 2.3 What about historical names

When a physical rearrangement happens, the subagent migrates files following §2.2;
**renames must also update every reference** (grep the whole workspace). After the
rearrangement, all new files follow this convention.

---

## 3. Index synchronization (INDEX.md)

Every topic subdirectory has an `INDEX.md` with a compact 3-field format (tags live in
frontmatter to avoid duplication):

```markdown
# <Topic> knowledge index

> Last maintained: YYYY-MM-DD by Eve

## Current entries

| slug                                  | One-line purpose                          | Status   |
| ------------------------------------- | ----------------------------------------- | -------- |
| `engine-static-brief.md`              | Static-shot baseline behavior             | active   |
| `engine-i2v-overshoot.md`             | First-3-frame overshoot and mitigation    | active   |
| `engine-fast-limits.md`               | 4-step lower-bound constraints            | active   |

## Deprecated / superseded

| slug                          | Superseded by                              | Reason                |
| ----------------------------- | ------------------------------------------ | --------------------- |
| `two-layer-principle.md`      | `evaluation/four-layer-principle.md`       | Upgraded when layer D was added |
```

### 3.1 Write / update rules

- **New knowledge**: the subagent must add a row to the matching topic's `INDEX.md`. If
  it does not exist, create it (with table header).
- **Update knowledge**: if `status` changes, mirror it in `INDEX.md`; if only `tags`
  change, edit frontmatter, not the INDEX.
- **Deprecate knowledge**: do not delete the file. Set frontmatter `status: deprecated`
  or `superseded-by: <path>`, and move the row to the "Deprecated" section.
- **`git add` immediately when creating new knowledge**: this preserves history during
  future rearranges via `git mv`. (Lesson learned the hard way: untracked files lose
  history on rearrange.)

---

## 4. Merge over fragment

A recurring failure mode: a subagent volunteers to "capture 6 new knowledge notes", Eve
merges them into 2–3, and the result is far better.

### 4.1 Decision rules

Before writing, ask yourself three questions:

1. **Does a same-topic file already exist?** Grep; if yes, Edit-append a section (with
   §N numbering) instead of creating a new file.
2. **Can this fit in an existing file as a section?** If yes, put it there — a long file
   is fine (an 800-line `pipeline/<recipe>.md` beats 6 fragments).
3. **Is this a Task-specific conclusion or reusable knowledge?** Detail only useful to
   this Task belongs in the Task file's "Conclusions and output", not in knowledge.

### 4.2 When a new standalone file is justified

- The topic is genuinely independent (a new engine, a new tool, a new platform).
- Adding it to an existing file would break that file's structure.
- A single note is expected to exceed ~300 lines and would dominate the file.

---

## 5. Audit checklist (Eve, before closing any Task)

Each time a subagent reports completion and Eve prepares to close the Task, walk this:

- [ ] **Topic placement**: did the new knowledge go into the right `<topic>/` subdir, not
      dumped at the `knowledge/` root?
- [ ] **Naming**: does the slug match §2.1 (lowercase-kebab, no Task code, no date
      prefix)?
- [ ] **INDEX in sync**: did the matching `INDEX.md` get a new row (or get created)?
- [ ] **Frontmatter complete**: new files must follow `templates/knowledge-template.md`
      (legacy files are grandfathered and may be incomplete).
- [ ] **Merge check**: did you grep same-topic files and confirm this cannot be merged?
- [ ] **References updated**: see §6 for the cross-area responsibility split.

Any unmet item: **send back to the subagent for an in-turn fix**. Never "close now, top
up later".

## 6. Cross-area reference-update responsibility

Intra-`knowledge/` references: **the writer owns them** (when a subagent writes new
knowledge, it updates all the cross-refs inside `knowledge/`).

Cross-area references (mentions of an old knowledge path inside `goals/`, `tasks/`,
`archive/`, `sessions/`, `agents/`, `workflows/`):

| Scenario                                  | Owner                          | Scope                                                                  |
| ----------------------------------------- | ------------------------------ | ---------------------------------------------------------------------- |
| Subagent writes new knowledge             | the subagent                   | inside `knowledge/` + the assigned `tasks/<my-task>.md`                |
| Eve captures knowledge                    | Eve                            | inside `knowledge/` + all `goals/` + all `workflows/`                  |
| Archivist big rearrange (rearrange Task)  | archivist (boundary widened)   | whole workspace **except** historical snapshots in `archive/`, `sessions/` |
| Historical snapshots (archive, sessions)  | exempt                         | old paths preserved as-is (historical original)                        |

**Principle**: bulk cross-Goals / cross-Tasks reference updates are delegated by Eve to
the archivist in one shot, not done piecemeal by each Task's subagent editing other
people's Task files.

---

## 7. Relationship to other files

- This protocol is the mandatory refinement of `workflows/subagent-workflow.md §4.3
  knowledge capture`. On conflict, this protocol wins.
- `templates/knowledge-template.md` is the format template; use it together with this
  file.
- `workflows/task-lifecycle.md §4 review and close` embeds this §5 checklist as a close
  gate.
