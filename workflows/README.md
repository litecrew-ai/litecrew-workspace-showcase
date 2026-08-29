# Workflows

This directory holds the standardized operating procedures for every core role in the
workspace. They are split into two layers.

## Layer 1: Role lifecycles

| File                  | Audience  | Purpose                                                                                  |
| --------------------- | --------- | ---------------------------------------------------------------------------------------- |
| `goal-lifecycle.md`   | Eve       | Defines how Eve advances one Goal during a single activation (split one Task, run it to closure). |
| `task-lifecycle.md`   | Eve       | Defines how Eve creates, dispatches, reviews, and closes a Task.                         |
| `subagent-workflow.md`| Subagent  | Defines the unified execution protocol for all subagents (startup, retrieval, execution, capture, handoff). |

## Layer 2: Capture and placement protocols (mandatory gates)

These protocols turn "capture knowledge" from a slogan into checkable gates. They
are referenced from `task-lifecycle.md §4.2`, which adds a fourth gate (handbook
review) that does not have its own protocol file.

| File                                | Audience        | Purpose                                                                                                |
| ----------------------------------- | --------------- | ------------------------------------------------------------------------------------------------------ |
| `knowledge-sediment-protocol.md`    | Eve + Subagent  | Topic classification, naming conventions, INDEX synchronization, and merge-over-fragmentation rules.  |
| `session-summary-protocol.md`       | Eve             | The `SUMMARY.md` rolling window (≤ 5000 tokens) and weekly archive — prevents single-file bloat.       |
| `artifacts-lifecycle.md`            | Eve + Subagent  | Per-business artifact placement, mixed active/archived storage, create/archive/cleanup rules.          |

## Principles

- Eve must follow the matching lifecycle file when advancing a Goal or Task.
- When Eve dispatches a Task to a subagent, the subagent is required to load and obey
  `subagent-workflow.md` plus any capture / artifact protocols relevant to the Task.
- These files are the "law" that keeps the workspace self-running. They are not optional.
- Once a new protocol lands, **before Eve closes any Task it must walk the gates in
  `task-lifecycle.md §4.2`**: knowledge sediment, artifact placement, session notes,
  handbook review.
