# Knowledge (reusable notes)

This directory holds **reusable knowledge fragments**: techniques, pitfalls, configuration
recipes, decision rationale — distilled from Task execution into shared, long-term memory.

## Read this before writing

**Everyone who writes here (Eve and subagents) must first read
`workflows/knowledge-sediment-protocol.md`.** This directory uses a **business-first
layout**: top-level directories are business domains (not technical topics), so a reader
can tell at a glance which business a note serves. Within a business, split a second
level only when the top level grows past ~10 files.

## Layout (business-top-level, on-demand second level)

The shipped workspace is empty — **you decide your own business directories**. A typical
layout looks like:

```
knowledge/
├── README.md                  # This file
├── <your-business-1>/         # Your first business domain
│   ├── INDEX.md               # Topic index (mandatory)
│   ├── <topic-subdir>/        # Optional second level when business has ≥ 10 notes
│   └── <slug>.md              # Individual knowledge notes
├── <your-business-2>/         # Your second business domain
├── workspace/                 # Workspace infrastructure, shared across businesses
│   ├── INDEX.md
│   ├── infra/                 # Optional second level
│   ├── skills/
│   └── tools/
└── meta/                      # Notes about the workspace itself (protocols, naming)
```

For the canonical list of business directories, second-level split rules, and
cross-business handling, see `workflows/knowledge-sediment-protocol.md §1`.

## Write checklist (mandatory)

- [ ] Picked the right **business-top-level** directory.
- [ ] If that business has a second level, picked the right second-level subdir.
- [ ] The slug matches the naming convention (lowercase-kebab, no Task code, no date
      prefix).
- [ ] Frontmatter is complete (see `templates/knowledge-template.md`).
- [ ] The matching `INDEX.md` was updated.
- [ ] Grepped same-topic files and confirmed this cannot be merged into an existing note.

## Who can write here

- **Eve**: may capture high-value notes at any time.
- **Subagent**: after Task completion, follows `subagent-workflow.md §4.3`. **Eve audits
  against the `task-lifecycle.md §4.2` gate before closing the Task**; unmet items go
  back.

## Knowledge vs Handbooks

- **Handbook**: process — "how to do" — typically with steps and norms that guide future
  action.
- **Knowledge**: discrete fact — "what we know" — leaning toward experience, technical
  detail, and problem/solution pairs.

Together they form the workspace's growing intelligence layer.
