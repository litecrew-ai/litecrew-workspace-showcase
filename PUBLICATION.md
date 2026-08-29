# PUBLICATION.md — operator runbook

This is the operator's runbook for `litecrew-workspace-showcase`. It is not demo
content: the demo narrative never links here, and no steward-agent session ever
reads it. It exists so that the human operator — the person playing "the user"
and pressing git — runs every activation the same way, every time.

What this repo is: a real `litecrew-workspace` instance, driven through real
agent sessions, published as a lived-in exhibit. A fresh CLI session started
with this repo root as its working directory becomes the steward agent (Eve) by
loading `CLAUDE.md` -> `AGENTS.md`. The operator feeds it one baked user
request per activation. The git history — one commit per activation — is the
product being exhibited.

## 1. Provenance

- Skeleton imported from the public `litecrew-workspace` repository at commit
  `bedf834` (tree only; upstream history intentionally not preserved). At that
  commit the upstream already ships the `.claude/agents -> ../agents` mount,
  so a fresh session can dispatch the factory agent on day one with no
  operator patching.
- Operator additions folded into the import commit, so that everything after
  the `baseline` tag is demo-produced:
  - `.gitignore` divergence from the skeleton: this repo tracks `artifacts/`
    (the exhibits) and the `.claude` mount, while still ignoring local
    CLI state.
  - this runbook.
- Bootstrap probe (import day, one-shot headless session, cwd at repo root):
  confirmed (a) the workspace contract auto-loads and assigns the steward
  role, and (b) `workspace-archivist` is dispatchable as a subagent type.

## 2. The activation loop

One activation advances at most one Task of one Goal to closure (that is the
workspace's own lifecycle rule — do not batch).

1. Pick the next baked user request from the scenario plan. Use it verbatim;
   do not coach, do not add hints.
2. Start a fresh session with the repo root as cwd, using the headless form
   measured in section 4 (pinned cwd, bypassed permissions, interactive
   questions disallowed, generous turn budget, full transcript captured as
   operator evidence outside this repo). The session is Eve.
3. Let the turn run to completion. If the session's final message asks
   clarifying questions, answer them briefly and in character in the next
   one-shot call.
4. When the turn ends, run every gate in section 5. Zero hits required.
5. Commit exactly once, per section 3.
6. Between activations, let real calendar time pass — Goals should spread
   across one to two weeks so timestamps and commit dates look like work,
   not like a batch run.

## 3. Commit convention — one activation, one commit

Commits happen only at activation boundaries. Never mid-task, never two per
activation, never zero (a turn that produced no commit is a red flag to
investigate, not to paper over).

Message format (conventional commits):

```
task(<goal-slug>): <verb> <task-slug> [(hire <agent-slug>)]

- Task: tasks/<task>.md closed after N round(s)
- Knowledge: knowledge/<topic>/<note>.md (+INDEX)
- Artifacts: artifacts/<biz>/<slug>/
- Session: sessions/<file>.md
```

List only the lines that apply; add one line per knowledge note or artifact
directory. House rules:

- `main` only, strictly linear. No merges, no rebases, no amends, no squashes
  of existing commits — a botched message stays botched.
- The `baseline` tag sits on the import commit. Invariant:
  `git diff --name-only baseline..HEAD` must only ever contain demo-produced
  paths. This is why every operator file (this runbook, the `.gitignore`
  divergence) was folded into the import commit itself.
- Closing meta work after the last Goal uses `task(workspace): ...` in the
  same format.
- All commits are authored by the operator. The steward agent has no git
  access by design; the published README states this plainly.

## 4. Dispatch protocol — command form and the session agent-registry cache

Measured command form (drives one full activation end to end):

```bash
cd <repo-root>   # the session's cwd IS the workspace
env -u CLAUDECODE -u CLAUDE_CODE_ENTRYPOINT -u CLAUDE_CODE_EXECPATH \
    -u CLAUDE_CODE_SESSION_ID -u CLAUDE_CODE_SSE_PORT \
    claude -p \
      --permission-mode bypassPermissions \
      --disallowedTools AskUserQuestion \
      --output-format stream-json --verbose \
      --max-turns 80 \
      "<baked request verbatim>"
```

Why each piece:

- The env vars are stripped because the call is normally made from inside
  another CLI session; leaving them set makes the nested CLI misidentify
  itself as a child of the operator's session.
- `--permission-mode bypassPermissions`: the run is unattended; no permission
  prompt may block it. (Requires a non-root account.)
- `--disallowedTools AskUserQuestion`: forces the session to proceed on its
  best understanding instead of stalling headlessly on a question. If it
  truly needs the user, it will say so in its final message.
- `--output-format stream-json --verbose`: the full transcript streams into
  the operator's evidence log outside this repo; nothing is paraphrased
  after the fact.
- `--max-turns 80`: measured sufficient with headroom — full-lifecycle
  activations have landed at 53 and 62 turns. Gate-fix rounds (section 5)
  are short dispatched rounds: give them `--max-turns 16` to `20`.

Registry-cache pitfall (verified three times in the maintainers' source
workspace): Claude Code caches the subagent registry when a session starts.
An agent file created during the current activation cannot be dispatched by
`subagent_type` in that same session — the type simply is not registered
yet. Protocol:

- In the activation where a new agent is hired, dispatch a general-purpose
  container instead, and open its prompt with the full text of the agent
  definition file as the role contract. The agent then behaves as defined
  even though the runtime cannot address it by type.
- From the next activation on, dispatch the agent normally by
  `subagent_type`.
- Never rename or delete an agent definition between activations without
  checking which sessions referenced it.

Cost control: drive every activation with the minimal prompt (the baked
request verbatim); one-shot headless calls only.

## 5. Leak gates — after every activation, before its commit

Any hit blocks the commit. Fix by dispatching another round (the fix becomes
part of the honest history), never by silently hand-editing demo content.

Gate 1 — no CJK anywhere in tracked text:

```bash
git grep -InP '[\x{4e00}-\x{9fff}]'
```

(`-I` skips the binary images shipped with the skeleton.)

Gate 2 — forbidden token pack. The pack lives in the operator's private leak
checklist and is substituted at run time; quoting any token here would make
the gate self-match. The pack bans, by category: vendor and engine names tied
to the source workspace, IM-bridge codenames, Chinese platform names, the
maintainers' private workspace name, internal project labels, and absolute
paths of the operator machine. Run:

```bash
TOKEN_PACK='<substitute the pack from the private leak checklist>'
git grep -nE "$TOKEN_PACK"
```

Scoping decisions, on the record: per activation the pack must cover at least
the paths changed since `baseline`; the publication pass runs it tree-wide.
The imported skeleton passes the pack's published form with zero hits. One
upstream file (`handbooks/README.md`) names romanized Chinese platforms inside
a hypothetical example; that is upstream content outside the demo's edit scope
and outside the pack's published form — recorded here so the publication pass
decides it consciously instead of discovering it late.

Gate 3 — no emoji in demo-produced content, and none ever in operator files:

```bash
EMOJI='[\x{1F000}-\x{1FAFF}\x{2600}-\x{27BF}\x{FE0F}]'
git diff --name-only baseline..HEAD -z | xargs -0 -r grep -nP "$EMOJI" --
grep -nP "$EMOJI" PUBLICATION.md README.md .gitignore
```

Scoping decisions, on the record: the imported skeleton ships a handful of
emoji in upstream files (a security-contact badge, checklist marks in a
template, marks inside the vendored skill-creator scripts) — grandfathered as
upstream content, out of the gate's scope. Arrow glyphs are typography, used
throughout the upstream skeleton, and are deliberately not in the class.

Gate 4 — size and truthfulness:

```bash
find . -path ./.git -prune -o -type f -size +100k -print
```

No text file over 100KB — split it or move bulk data out and leave a pointer.
The skeleton's README images under `docs/assets/` are the known binary
exceptions (they ship with the upstream skeleton). Then spot-check that the
session note written this activation matches `git show --stat` of the commit
it lands in (anti-whitewash check: the note must not claim more or less than
the diff shows).

Gate 5 — business directory whitelist. Top-level topic directories under
`artifacts/` and `knowledge/` must be within:

```
research/  tools/  market-briefing/  writing/  workspace/
```

Directory names borrowed from the source workspace's internal vocabulary are
the most common leak vector; when in doubt, rename via a dispatched round.

## 6. Operator file whitelist

The operator may only ever create or edit:

- `.gitignore`
- `PUBLICATION.md` (this file)
- root `README.md` (publication pass only)
- git actions: add, commit, tag
- the `.claude` mount symlink (shipped with the import; keeping it intact is
  an operator responsibility, not demo work)

Everything else — `goals/`, `tasks/`, `knowledge/`, `sessions/`, `agents/`,
`archive/`, `artifacts/`, `handbooks/`, `workflows/`, `templates/` — is
demo-produced and lands exactly as the sessions left it. If demo content
fails a gate, the fix is another dispatched round, visible in history.

## 7. Honesty law

Higher priority than the exhibit looking good:

- Failed rounds, rejections, downgrades, and retries stay in the history
  exactly as they happened. No staging, no cosmetic re-runs over an unlucky
  result, no tidying session notes after the fact.
- A human played the user; every commit is one real activation; only
  `README.md`, `PUBLICATION.md`, and `.gitignore` are hand-written. The
  published README states all of this in the first screen.
- If an activation goes off the rails, commit the mess or record the abort —
  then steer the next activation. Never rewind.
