# Security Policy

## Reporting a vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Use GitHub's private vulnerability reporting instead:

➡️  **[Report a vulnerability](https://github.com/litecrew-ai/litecrew-workspace/security/advisories/new)**

Reports through this channel are visible only to repo maintainers. You can
coordinate fix disclosure and CVE issuance with us through the same channel.

If you cannot use GitHub's reporter, email `soraklein.fr@gmail.com` with
`[litecrew security]` in the subject line.

## Supported versions

Only the latest minor release receives security updates.

| Version | Supported          |
| ------- | ------------------ |
| 0.x     | :white_check_mark: |

## Scope

- The `litecrew-workspace` repo (paradigm files, workflows, templates, agent definitions).
- The bundled `find-skills` and `skill-creator` skills — these are verbatim copies of
  upstream; for those, also file a report upstream.

## Out of scope

- Vulnerabilities in AI CLI tools themselves (Claude Code, Codex, Cursor, Aider, …) —
  report to their respective vendors.
- Issues in forks or downstream derivatives of this repo.
- Vulnerabilities that require an already-compromised host. The workspace is plain
  Markdown — if your machine is compromised, the workspace is the least of your problems.
