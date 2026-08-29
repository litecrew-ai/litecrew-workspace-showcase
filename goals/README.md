# Goals (long-term objectives)

This directory holds every **long-term Goal** — active, paused, or completed. Each Goal
is one `.md` file, created and maintained by Eve.

## What a Goal file does

- Describes a macroscopic objective that needs many days and many iterations to reach
  (for example "Build and operate a quantitative trading app" or "Ship a personal blog").
- Records measurable **success criteria** — the only judge of whether the Goal is met.
- Links every Task split off from it, forming an auditable progress chain.
- Logs iteration progress and key decisions over time.

## Lifecycle

A Goal follows `../workflows/goal-lifecycle.md`: check whether the Goal is met → if not,
split off the single most urgent Task → wait for the Task to close → check again.
When every success criterion is met, the Goal moves to `completed` and is then archived
to `../archive/`.

## Filename convention

- Lowercase English with hyphens, e.g. `quant-trading-app.md`.
- Avoid special characters; keep it short.
