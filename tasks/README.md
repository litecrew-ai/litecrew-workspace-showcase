# Tasks (short-term work units)

This directory holds every **short-term executable Task**. Each Task is one `.md` file,
created by Eve and dispatched to a specific subagent.

## What a Task file does

- States what to do, why, and the completion criteria.
- Binds the responsible subagent (or several, when collaborating).
- Records the subagent's execution steps, iteration history, final conclusions, and
  output.
- Acts as the information conduit between Eve and the subagent.

## Read / write permissions

- **Eve**: create, modify, close, and archive any Task.
- **Subagent**: may only **update the single Task file assigned to it**; cannot modify
  other Tasks or any Goal. May write progress, conclusions, and a knowledge-capture
  suggestion.

## Iteration

A single Task may go through several subagent iterations (re-planning on a blocker,
re-running). Each iteration appends a row to the file's "Execution log" table.

## Filename convention

- Lowercase English with hyphens, e.g. `fix-auth-token-refresh.md`.
- Encode the core action in the slug to make search easier.
