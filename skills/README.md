# Skills

Skills are modular, self-contained packages that extend an agent's capabilities with
specialized workflows, tool integrations, and bundled resources. They are loaded at
dispatch time according to each subagent's `skills:` list (see `agents/`).

## What ships here

The open-source skeleton bundles two **meta skills** — the ones that help you find, add,
and create *more* skills:

- [`find-skills/`](./find-skills/) — discover and install skills from the open agent
  skills ecosystem via the Skills CLI (`npx skills find` / `npx skills add`).
- [`skill-creator/`](./skill-creator/) — a guide and tooling for authoring new skills:
  directory layout, `SKILL.md` structure, progressive-discipline, validation scripts.

Domain skills (rendering, social, reporting, etc.) are intentionally **not** bundled
here — they are project-specific. Use `find-skills` to pull what you need from the
ecosystem, or write your own with `skill-creator`.

## Installing a new skill

Inside the workspace, install a skill into this directory:

```bash
npx skills add <owner>/<repo>
```

The skill lands at `skills/<skill-name>/` and is picked up automatically by the next
dispatch.

After installing, refresh the `skills:` list of any subagent that should use it (Eve
does this at dispatch time, but you can also edit `agents/<agent>.md` directly).

## Skill layout (canonical)

A skill is a directory containing at least a `SKILL.md`:

```
skills/
└── <skill-name>/
    ├── SKILL.md                  # Required. Frontmatter: name, description, license.
    ├── references/               # Optional. Reference docs the skill loads on demand.
    ├── scripts/                  # Optional. Helper scripts the skill calls.
    └── assets/                   # Optional. Bundled binary assets (templates, fonts).
```

See [`skill-creator/SKILL.md`](./skill-creator/SKILL.md) for the full authoring guide.

## Maintenance

- Skills are versioned alongside the workspace in git. Pin to a specific commit if you
  need reproducibility.
- Skills must keep their internal files in English (the meta skills bundled here are
  already English).
- Skill internals are **not** subject to the workspace's translate-on-import rule — they
  ship as-is from their upstream authors.

## See also

- `workflows/subagent-workflow.md` — how skills are loaded at dispatch time.
- `agents/README.md` — the per-agent `skills:` list.
