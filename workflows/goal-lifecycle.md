# Goal lifecycle (single Eve activation)

> This file defines how Eve advances a Goal in a single external trigger. Eve itself does
> not loop; each activation handles exactly one Task — create / dispatch, supervise to
> closure, then end the turn. Long-term Goal progress depends on external scheduling.

## Single-activation flow

### 1. Inspect Goal state

- On activation, Eve first reads the target Goal file.
- Walk the success criteria and judge whether all are met.
  - If met → enter the "Completion and archival" step; this activation ends.
  - If not met → continue.

### 2. Split off the most urgent Task

- Analyze the unmet success criteria and current progress to identify the single most
  urgent, independently-advanceable piece of work.
- Turn it into a concrete Task using `task-template.md`, and link it to this Goal.
- Record the Task path in the Goal's related-task table.

### 3. Dispatch a subagent and wait for completion

- Pick a suitable subagent for the Task (create one if none exists yet).
- Pass the Task context to the subagent and require it to **finish the Task within this
  activation** (synchronous execution mode).
- The subagent follows `subagent-workflow.md`; Eve supervises and waits.

### 4. Review and close the Task

- After the subagent finishes, Eve reviews whether the Task output meets the completion
  criteria.
- On pass: close the Task, update the Goal's progress log, and process knowledge
  capture and handbook suggestions.
- On fail: require the subagent to fix it immediately (still within this turn), until
  the criteria are met or this turn's time runs out. If it cannot be completed, mark the
  Task blocked and record it for the next activation.

### 5. End this turn

- Update the Goal's `last-updated` timestamp.
- Eve exits. Regardless of whether the Goal is finished, this turn handled exactly one
  Task.
- The external scheduler may reactivate Eve afterwards to repeat the flow until the Goal
  is complete.

### 6. Write the session note

- Produce a session summary and save it as
  `./sessions/YYYY-MM-DD-HHMMSS-<goal-slug>.md`.
- Use the structure required by `./sessions/README.md`. Make sure it includes:
  - The Task name handled this turn and its outcome (done / blocked / failed).
  - Any Goal progress updates.
  - Which knowledge was captured or which handbooks were updated.
  - The suggested next Task direction (a hint is enough, even if not split off).
- Once written, this activation is officially over.

## Completion and archival

- If during an activation all success criteria are detected as met, Eve changes the Goal
  status to `completed`, archives the Goal and all of its Tasks, captures the final
  knowledge, and exits.
