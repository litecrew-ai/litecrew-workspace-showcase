# Archive

This directory holds every Goal and Task that has been **completed (`completed`)**,
**cancelled (`cancelled`)**, or **abandoned (`abandoned`)**.

## When to archive

- A Goal reaches all its success criteria → Eve moves it here.
- A Task passes review and closes → Eve moves it here.
- Anything the user or Eve actively aborts is preserved here permanently.

## Purpose

Keep `goals/` and `tasks/` lean — only items currently being worked on — while retaining
a permanent history for review, audit, and knowledge archaeology.

## Historical-snapshot exemption

Files in this directory **reference each other with whatever paths they originally
used**. Cross-area reference updates (per
`workflows/knowledge-sediment-protocol.md §6`) do **not** rewrite paths inside
`archive/`. Treat this directory as a frozen historical snapshot.
