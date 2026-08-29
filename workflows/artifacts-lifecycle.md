# Artifacts lifecycle protocol

> **This file is for Eve and subagents.** It defines the classification, naming,
> live-asset identification, and cleanup rules for everything under `./artifacts/`.
>
> Design choice: top-level by business domain (matching `knowledge/`), with active and
> archived items stored together; a per-business README distinguishes them.

---

## 0. Business-top-level, mixed active/archived storage

`artifacts/` is split at the top level by **business domain** (matching `knowledge/`).
Each business directory mixes:

- **Live assets**: project-level assets referenced across many Tasks (e.g. your primary
  application repo, third-party forks you depend on).
- **Archived Task output**: outputs kept after a Task closes (e.g. a one-off benchmark,
  a research probe).

**Tell them apart by naming convention**:

- Live assets use a **project name** (no Task suffix): e.g. `my-app/`, `benchmark-suite/`.
- Archived Tasks use a **Task slug** (the suffix gives it away): words like `-trial`,
  `-benchmark`, `-research`, `-render`, `-probe`, `-poc`, `-skill`, `-mgmt`,
  `-trial-v2`.

Every business directory must have a `README.md` that explicitly lists the **current
live assets** (archived Tasks do not need to be listed one by one — they are recognized
by Task-slug naming).

---

## 1. Directory structure

```
artifacts/
├── README.md                       # Overview + pointers to each business directory
├── <your-business-1>/              # Your first business domain
│   ├── README.md                   # Live-asset manifest
│   ├── <primary-project>/          ← Live asset (project name, no Task suffix)
│   ├── <third-party-fork>/         ← Live asset
│   ├── <task-slug>-trial/          ← Archived Task output (Task slug with suffix)
│   ├── <task-slug>-benchmark/
│   └── ...
├── <your-business-2>/              # Your second business domain
├── workspace/                      # Workspace infrastructure (cross-business)
│   ├── README.md
│   ├── <task-slug>-skill/          ← Skill-internal artifacts
│   └── _misc/                      ← Loose files that did not fit elsewhere
└── (no active/ or task-archive/ subdirectories)
```

### 1.1 Naming conventions

- Business directory name: kebab-case business name (e.g. `<your-business-1>`,
  `workspace`).
- Subdirectory name:
  - **Live asset**: project name (kebab-case, no Task suffix).
  - **Archived Task**: Task slug (carries a suffix like `-trial` / `-benchmark` /
    `-research` / `-render` / `-probe` / `-poc` / `-skill` / `-mgmt`).
- Do not stuff a version number into a Task slug (e.g. avoid `<slug>-v2`); use subdirs
  `v1/` `v2/` instead.

### 1.2 Anti-patterns to avoid

- Loose files at the root of a business directory (e.g. an old `notes.html`) — every
  file must belong to a Task subdirectory or live in `workspace/_misc/`.
- One Task's artifacts scattered across multiple business directories — file them under
  the single primary business the Task serves.
- Skill-internal artifacts leaking into `artifacts/` — keep them in
  `skills/<name>/artifacts/`.

---

## 2. Creating artifacts (subagent executing a Task)

### 2.1 Default path

The subagent writes artifacts directly to the final business directory:

- **Task one-shot output**: `artifacts/<business>/<task-slug>/<sub-path>/`
- **Cross-Task live asset** (requires Eve's explicit instruction):
  `artifacts/<business>/<asset-name>/`

**Important**: when a Task closes, artifact paths do **not** migrate. Write to the final
path during execution; the path is stable.

### 2.2 Choosing the business directory

Pick the business directory by the Task's primary serving Goal:

| Task serves Goal                    | Business directory          |
| ----------------------------------- | --------------------------- |
| `<your-business-1>` long-term Goal  | `<your-business-1>/`        |
| `<your-business-2>` long-term Goal  | `<your-business-2>/`        |
| Workspace infrastructure (tooling, skill engineering, ops) | `workspace/` |

When unsure which business, pick by "where is the reader most likely to look for it",
and record the choice in the Task report so Eve can double-check.

### 2.3 Multi-version artifacts

Multiple iterations of the same Task (v1 / v2 / v3) live as version subdirectories under
one Task-slug directory:

```
artifacts/<your-business-1>/<task-slug>-render/
├── v1/
├── v2/
└── v3/
```

---

## 3. Live-asset registration (mandatory)

Every business directory that **has live assets** must have a `README.md` listing them
explicitly:

```markdown
# <your-business-1> business live assets

> Last maintained: YYYY-MM-DD by Eve

## Live-asset manifest (referenced across Tasks)

| Asset directory                | Purpose                       | Referenced by                                  | Status   |
| ------------------------------ | ----------------------------- | ---------------------------------------------- | -------- |
| `<primary-project>/`           | Project main directory        | Multiple Tasks + goals/<goal-1>.md             | active   |
| `<third-party-fork>/`          | Reference / dependency code   | archive/<old-task>.md                          | frozen   |

## Pending cleanup (archived Task output unreferenced for 90 days)

- none
```

**Goal file related-assets field** (kept as-is): the body of `goals/<goal>.md` must
contain:

```
Related assets: artifacts/<your-business-1>/README.md
```

---

## 4. Cleanup rules

### 4.1 Archived Task output

- **Unreferenced by any Task / Goal / knowledge for 3 months**: Eve may (a) delete large
  files but keep the `.md` report, or (b) move the whole thing to
  `artifacts/_cold-storage/<YYYY-MM>/`.
- **Referenced by some knowledge**: keep forever.
- Before deleting, grep the whole workspace to confirm no references.

### 4.2 Live assets

- When a Goal moves to `completed`, move its live assets to that business's
  `_closed-goals/<goal-slug>/` subdirectory, or pack them into cold storage.
- If a live asset is unreferenced for 6 months and has no Goal, mark it `frozen` in the
  README; after 1 year, demote it to archived.

### 4.3 Disallowed operations

- A subagent must never delete anything under `artifacts/` (even files it created) —
  cleanup is Eve's call.
- No "for cleanliness" batch `rm` — every cleanup item must be checked individually for
  references.

---

## 5. Audit checklist (Eve, before closing any Task)

- [ ] Are the artifacts placed in the correct business directory?
- [ ] Does the artifact directory have a `README.md` or `RESULT.md` note?
- [ ] If the Task references live assets, are they registered in the business README?
- [ ] Are large binaries listed in `.gitignore`?

---

## 6. Relationship to other files

- Supplements `workflows/subagent-workflow.md §3.2 artifact placement` (path rules).
- Embedded in `workflows/task-lifecycle.md §4` as one of the close gates.
- Pairs with `workflows/knowledge-sediment-protocol.md`: business directory naming
  matches `knowledge/`.
