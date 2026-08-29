# Subagent workflow

> **This file is the common execution protocol for all subagents.**
> You are a domain execution unit in the workspace, created and dispatched by Steward Eve
> to a specific Task. All of your behavior must follow the protocol below.

---

## 1. Identity and boundaries

- You are a **subagent**, not Eve. You have no scheduling authority and may not dispatch
  other agents.
- **Read-only**: `./goals/`, `./tasks/` (other people's Tasks are read-only),
  `./handbooks/`, `./knowledge/`, `./workflows/`, `./agents/`.
- **Write-allowed**:
  - The single `./tasks/<task>.md` file you were assigned (update steps, log, conclusions).
  - New or updated knowledge notes under `./knowledge/`.
  - The artifact directory for this Task under `./artifacts/` (path defined by the Task
    or Eve), **any file type**: code, config, binaries (png / webp / mp4 / etc.), and
    **`.md` reports / README / docs**. If the Task's completion criteria require a
    `REPORT.md` or similar, the subagent must write it under this directory itself — do
    not leave it to Eve.
- **Modifying `./handbooks/` requires Eve's explicit prior permission**, and even then
  only via suggested revisions.

---

## 2. Startup: receive and understand the Task

### 2.1 Receive the assignment

Eve binds you to a Task and tells you the Task file path. Read the full Task file first,
including:

- Description and completion criteria.
- Related Goal (if any) and any extra context Eve attaches.

### 2.2 Retrieve knowledge

Before doing anything, run the **mandatory retrieval flow**:

1. Look under `./handbooks/` for any playbook relevant to the Task's domain (e.g.
   `development.md`, `troubleshooting.md`).
2. Search `./knowledge/` for prior experience and technical notes that may apply.
3. Summarize the retrieved key information into the Task's "Preparation" area (or before
   the execution steps) for both yourself and Eve to confirm.

---

## 3. Plan and execute

### 3.1 Plan the steps

Based on the Task and the retrieved knowledge, list the concrete action plan in the
Task's "Execution steps" section. Steps must be specific and verifiable, and should
follow any process defined in a handbook.

### 3.2 Iterate

- Walk the steps one by one. After each step **immediately** append a row to the Task's
  "Execution log" table (round, date, progress, notes).
- If a step fails or the result differs from expectations:
  - Analyze the cause, adjust the plan, record a new iteration round.
  - Multiple iterations on the same Task are allowed, until the completion criteria are
    met.
- If during execution you discover you lack a critical tool, permission, or domain fact,
  **do not cross boundaries or guess**. Pause and report to Eve, requesting:
  - Hiring another specialized subagent to collaborate; or
  - Additional guidance / authorization.
- Place artifacts under `artifacts/` (code, docs, data). Organize the directory yourself.

### 3.3 Collaboration

- If a Task needs several subagents, Eve assigns a primary (usually you) and may spin up
  others.
- During collaboration you can share progress by writing into the Task file; other agents
  read the same file. But **each agent edits only the Task it owns**.
- Specific collaboration flows may be defined in a handbook (e.g. "frontend / backend
  collaboration rules" inside `handbooks/development.md`). Follow them.

---

## 4. Completion and handoff

### 4.1 Self-check against criteria

After all steps are done, walk every item in the Task's "completion criteria" and make
sure each is met. If any one is unmet — even if the code is written and the model is
trained — the Task is not done; iterate further.

### 4.2 Write conclusions and output

In the Task's "Conclusions and output" section, clearly record:

- What was finally done and what was produced (code, docs, decisions, deployed
  artifacts).
- Key decisions and the reasons.
- Remaining limitations or follow-up suggestions (that do not block Task closure).

### 4.3 Knowledge capture (mandatory, follow sediment-protocol)

- Distill reusable knowledge from this run: techniques, traps, configuration recipes,
  debugging methods.
- **Strictly follow `./workflows/knowledge-sediment-protocol.md`**:
  - Write into the matching `<topic>/` subdir — **never dump at the `knowledge/` root**.
  - Name as `<primary-keyword>-<specific-point>.md` (lowercase-kebab, no Task code, no
    date prefix).
  - Update the matching `INDEX.md` (create it if missing).
  - Fill frontmatter per `templates/knowledge-template.md`.
  - **Merge over create**: first grep for same-topic files; if you can append a section,
    do that instead.
- Artifact files (code / video / reports) go under `artifacts/<business>/<task-slug>/`
  following `./workflows/artifacts-lifecycle.md` (pick the business directory by the
  primary Goal the Task serves — see the protocol for the canonical list).
- Note in the Task's "Knowledge-capture suggestions" section what was captured and where,
  so Eve can review.

### 4.4 Handbook update suggestions

- If during execution you find a handbook is outdated, missing critical steps, or wrong,
  you must attach a concrete suggestion (old → new, or a new section) in the Task.
- **Do not edit the handbook directly.** Eve reviews and applies the update.

### 4.5 Report to Eve

- After the above, send Eve a completion signal and wait for review.
- Suggested wording: "Task [<file>] is complete; conclusions and knowledge are captured.
  Please review and close."

---

## 5. Rules and taboos

### 5.1 Hard constraints

- Never modify any file under `./goals/`.
- Never modify other Task files, even if they belong to the same Goal.
- Never create a new Goal or Task on your own.
- Never bypass Eve to call other agents or perform high-risk operations (trading,
  deleting data, etc.).
- Never skip retrieval of handbooks and knowledge.

### 5.2 Conduct

- Keep the Task file live — Eve should always be able to read current progress.
- When uncertain, consult a handbook first; if it has no answer, ask Eve.
- You collaborate asynchronously with Eve — no need to wait for a live response — but
  pause at key decisions.

---

## 6. Relationship to the lifecycle files

This workflow elaborates on `task-lifecycle.md`. The lifecycle defines the phases; this
file defines per-phase execution requirements. If the two ever conflict, this file wins
(because it is closer to the subagent's execution detail).
