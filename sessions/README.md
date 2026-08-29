# Sessions (session notes)

This directory holds the **session summaries** Eve writes after every external
activation, used to recover context across activations.

## Filename

Format: `YYYY-MM-DD-HHMMSS-<goal-slug>[-task-<slug>].md`
The timestamp is the activation time (UTC), precise to the second, ensuring uniqueness
and sortability.

## File contents

Each session note contains (use `templates/session-summary-template.md`):

- **Trigger time**
- **Active Goals** at the moment of activation
- **The Task handled this turn** (created or continued)
- **The dispatched subagent** and its execution summary
- **Key decisions and outputs**
- **Blockers and follow-up suggestions**
- **Knowledge and handbook changes this turn**

## Rolling summary

In addition to per-session files, this directory holds `SUMMARY.md` — a rolling 7-day
window into the workspace state. Older entries are archived weekly to
`sessions/archive/YYYY-WW.md`. See `workflows/session-summary-protocol.md` for the full
rules and token budgets.

## Purpose

- **Context recovery.** At the start of every new activation, Eve reads the latest 1–3
  session notes (plus `SUMMARY.md`) alongside current Goal status, to instantly
  understand "where we left off and what comes next".
- **Problem archaeology.** Helps debug or analyze the long-term trajectory of a Goal.
- **Automatic pruning.** Eve periodically archives old notes to `archive/` to keep this
  directory scannable.
