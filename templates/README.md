# Templates

Standardized templates for Goals, Tasks, agents, knowledge, and session summaries. Eve
uses these when creating new items so that format and required fields stay consistent.

## Available templates

- `goal-template.md` — for new long-term Goals.
- `task-template.md` — for new short-term Tasks.
- `agent-template.md` — for new subagent definitions.
- `knowledge-template.md` — for new knowledge notes (must be paired with
  `workflows/knowledge-sediment-protocol.md`).
- `session-summary-template.md` — for single-session detail files written by Eve.

## Usage

When Eve creates a Goal, Task, agent, or knowledge note, base the file on the matching
template and replace placeholders (e.g. `{{title}}`, `{{date}}`) with real values.

## Evolution

If practice shows that a field is missing or the structure needs adjustment, Eve may
modify a template — keeping backward compatibility with existing files and the lifecycle
protocols.
