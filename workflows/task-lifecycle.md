# Task lifecycle

> **This file is for Steward Eve only.** It describes Eve's steps and decision logic when
> managing Tasks.
> The detailed execution protocol for subagents lives in
> `./workflows/subagent-workflow.md`. Eve ensures that any dispatched subagent loads and
> follows it.

---

## 1. Create a Task

- When Eve decides an atomic unit of work is needed (split off from a Goal or raised
  independently), generate a new Task file from `./templates/task-template.md`.
- Fill in: description, completion criteria, related Goal (if any).
- Decide which subagent(s) should execute it. If none exists under `./agents/`, Eve must
  first create the subagent definition file.
- Write the primary responsible subagent into the Task's `assigned_agent` field.
- Set status to `todo`.

---

## 2. Dispatch the subagent

- Eve hands the Task file path to the chosen subagent with explicit instructions:
  - Must follow `./workflows/subagent-workflow.md`.
  - Must auto-discover the relevant handbook and knowledge.
  - Must write progress and conclusions back into the Task file, respecting read/write
    boundaries.
- For multi-agent collaboration, record each agent's role and responsibilities in the
  Task file and dispatch each accordingly.

---

## 3. Synchronous execution and monitoring

- In the current activation, after Eve dispatches the Task it stays in supervisor mode
  until the subagent reports completion or a blocker.
- Eve does not interfere with execution details, but guarantees a result this turn
  (done, blocked, or failed).
- If the subagent requests an additional agent or extra authorization, Eve coordinates
  in-turn to close the loop this activation.

---

## 4. Review and close

### 4.1 Completion-criteria check

- When the subagent reports completion, Eve reviews:
  - Walk each item in the Task's "completion criteria" — are they all met?
  - Are the conclusions clear and the artifacts verifiable?
- On a failed review:
  - Append requirements in the Task and instruct the subagent to iterate (record the new
    round).
  - If the cause is an external dependency, mark the Task `blocked`, record it on the
    Goal, and wait for the next activation.

### 4.2 Capture and placement gates (mandatory · no closure without passing)

After completion criteria pass, Eve must walk the following four gates. **Any unmet item
sends the Task back to the subagent for in-turn fix — never "close now, top up later".**

- [ ] **Knowledge sediment** — fully meets all 6 items in
      `workflows/knowledge-sediment-protocol.md §5`:
  - Topic placement (file went into the right `<topic>/` subdir, not dumped at the root)
  - Naming compliant (lowercase-kebab, no Task code, no date prefix)
  - INDEX in sync (the matching `INDEX.md` got a new row, or was created)
  - Frontmatter complete (see `templates/knowledge-template.md`)
  - Merge check (grepped same-topic files; confirmed this cannot be merged in)
  - References updated (renames update links across the whole workspace)

- [ ] **Artifact placement** — fully meets all 4 items in
      `workflows/artifacts-lifecycle.md §7`:
  - Artifacts placed correctly (right business directory)
  - Artifact directory has a README/RESULT note
  - References to live assets are registered in the Goal's "related assets" field
  - Large binaries are listed in `.gitignore`

- [ ] **Session notes** — all 5 steps of
      `workflows/session-summary-protocol.md §2.1` are done:
  - Single-session detail file written (timestamp precise to the second)
  - The "Recent 7-day sessions" table in `SUMMARY.md` got a new row
  - Key decisions added to the "Important decisions" section (≤ 3 lines each)
  - Goal status changes mirrored to "Active Goal snapshot"
  - Open-Task changes mirrored to "Currently open Tasks"
  - If `SUMMARY.md` already ≥ 4000 tokens, the weekly archive has been triggered

- [ ] **Handbook review** — if this Task exposed a missing "how to" (a handbook that
      should exist but doesn't), Eve decides to (a) write that handbook now, or (b) log
      it in the backlog inside `handbooks/README.md`.

### 4.3 Close

Once all four gates pass:

- Update the Task status to `done`.
- Update the linked Goal's (if any) progress log.
- Approve and apply writes to `./knowledge/` or `./handbooks/` (Eve edits handbooks
  directly when needed).
- Archive the Task to `./archive/`.

---

## 5. Cancel a Task

- If the user or Eve decides a Task is no longer needed (e.g. direction change), Eve
  sets its status to `cancelled`, records the reason, and archives it.

---

## 6. Eve's hard constraints

- Eve **must not** perform any business operation inside a Task (writing code, running
  commands, debugging).
- Eve maintains the workspace's structure, consistency, and knowledge capture, but all
  productive work goes through a subagent.
- At dispatch time, ensure the subagent knows its boundaries: only the assigned Task and
  `./knowledge/` are writable; never edit other Tasks or any Goal.

## 7. Session notes

- After a Task closes, Eve must write a session summary to `./sessions/` before this
  activation ends, following `goal-lifecycle.md`.
