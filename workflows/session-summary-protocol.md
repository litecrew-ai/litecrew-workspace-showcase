# Session summary protocol

> **This file is for Eve.** It solves the problem of `sessions/SUMMARY.md` growing
> without bound and exploding the token budget.

---

## 0. Problem diagnosis

Old practice: every session appended a line to the top of `SUMMARY.md` ("last updated:
... + ... + ..."). The single file ended up stacking dozens of entries plus full
"recent key decisions" entries of hundreds of words each, plus a full "active Goal
snapshot". Consequences:

- The agent paged through it on entry and missed early decisions.
- Token usage grew linearly and would eventually overflow.
- A single file failed single-responsibility: it mixed "diary" with "index".

This protocol turns `SUMMARY.md` from "full history" into a **rolling window plus weekly
archive**.

---

## 1. File layout

```
sessions/
├── SUMMARY.md                          # Rolling window, ≤ 5000 tokens
├── README.md                           # Protocol description (points here)
├── YYYY-MM-DD-HHMMSS-<task-slug>.md    # Single-session detail
└── archive/
    ├── 2026-W28.md                     # Weekly archive (one week of activity)
    └── 2026-W29.md
```

### 1.1 Single-session detail

- Filename: `YYYY-MM-DD-HHMMSS-<task-slug>.md`, **timestamp precise to the second** (the
  old minute-only convention produced collisions).
- Content: which Task this session handled, output, decisions, next step. See
  `templates/session-summary-template.md`.
- When: Eve must write it before the session ends — **never leave it to next time**.
- Audience: anyone later revisiting a specific decision; Eve merges references into the
  weekly archive.

### 1.2 SUMMARY.md (rolling window)

Keep only 4 sections, each strictly length-capped:

```markdown
# Workspace recent summary

> Last updated: YYYY-MM-DD HH:MM by Eve
> Window: last 7 days · full history in sessions/archive/

## Active Goal snapshot (≤ 30 lines per Goal, only current state + next step)

- **<goal-1>** (active): success criteria 1/3; next: <next Task hint>
- **<goal-2>** (active): <status>; next: <next Task hint>

## Last 7 days of sessions (reverse chronological, ≤ 3 lines each)

| Date       | Task                                  | Result  | Key output                                |
| ---------- | ------------------------------------- | ------- | ----------------------------------------- |
| YYYY-MM-DD | <task-slug>                           | done    | <one-line summary, see detail file>       |
| ...        | ...                                   | ...     | ...                                       |

## Currently open Tasks (active items in tasks/)

- `tasks/<task-slug>.md` (in_progress, <blocker>)
- `tasks/<task-slug>.md` (todo)

## Important decisions (last 7 days only · older decisions in archive/)

- YYYY-MM-DD: <one-line decision>, see `sessions/<detail-file>.md`
```

### 1.3 Weekly archive (archive/YYYY-WW.md)

Every Monday (or when `SUMMARY.md` approaches 4000 tokens — whichever fires first), Eve
cuts the "last 7 days of sessions" table and "important decisions" section out and merges
them into `sessions/archive/YYYY-WW.md`:

```markdown
# 2026-W28 session archive (MM-DD ~ MM-DD)

## Session list this week (details in each single-session file)

[Table migrated from SUMMARY.md]

## Important decisions this week

[Migrated decisions, each keeping the original detail-file link]

## New knowledge this week (grouped by topic)

- <biz>-engines/: <slug>.md / <slug>.md
- <biz>-pipeline/: <slug>.md
- ...
```

After the archive, those two sections in `SUMMARY.md` reset to empty and only the new
rolling window is kept.

---

## 2. Operating rules

### 2.1 At session end (before Eve's single activation ends)

1. Write the single-session detail file
   `sessions/YYYY-MM-DD-HHMMSS-<task-slug>.md`.
2. Insert a row at the top of the "last 7 days of sessions" table in `SUMMARY.md`.
3. If a key decision was made, add a row to "Important decisions" (≤ 3 lines; link to the
   detail file for the rest).
4. If Goal status changed, update "Active Goal snapshot".
5. If an open Task changed, update "Currently open Tasks".

### 2.2 Triggers for weekly archive (any one fires)

- **Time**: first activation on Monday.
- **Token budget**: `SUMMARY.md` is detected over the cap (≥ 4000 tokens read) or
  estimated ≥ 4000 tokens.
- **Manual**: Eve judges the current SUMMARY to be confusing (e.g. legacy cleanup).

### 2.3 Weekly-archive steps

1. Read `SUMMARY.md`, identify items outside the window (> 7 days old sessions /
   decisions).
2. Create or append `sessions/archive/YYYY-WW.md` (WW = ISO week).
3. Move those items, with original detail-file links, to the archive.
4. Replace the corresponding location in `SUMMARY.md` with "see archive/YYYY-WW.md" or
   clear it.
5. Leave single-session detail files alone (historical original, permanent).

---

## 3. Token budget

| File                                | Soft cap      | Hard cap (archive immediately when crossed) |
| ----------------------------------- | ------------- | ------------------------------------------- |
| `SUMMARY.md`                        | 4000 tokens   | 5000 tokens                                 |
| Single-session detail              | 5000 tokens   | 8000 tokens                                 |
| Weekly archive `archive/YYYY-WW.md` | 8000 tokens   | none (already history)                      |

After writing, Eve **self-checks**: if the file looks truncated or is felt to be over
budget, trigger §2.2 immediately.

---

## 4. Relationship to other files

- This protocol extends `workflows/goal-lifecycle.md §6 write session note` — fixing the
  format and limits.
- The internal structure of single-session detail is in
  `templates/session-summary-template.md`.
- This protocol pairs with `task-lifecycle.md §7 session notes`: Task closes → Eve
  writes single-session detail → updates SUMMARY.
