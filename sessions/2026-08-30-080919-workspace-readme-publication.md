# Session 2026-08-30 08:09 UTC — operational: README publication pass at operator instruction

## Trigger

User request: rewrite the root README (still the upstream workspace template) to
introduce the showcase generated using workspace, include a brief workspace
introduction, link to the workspace GitHub page for continued reading, and include
the archaeology preview link https://litecrew.ai/cases/internet-archaeology/.

## What was done

- No Task dispatched (operator-file edit, directly instructed). Root README.md is
  operator-whitelisted ("publication pass only") — this edit IS the publication
  pass, performed by Eve at the operator's explicit instruction; recorded here per
  the established deviation pattern (see sessions/2026-08-29-100422).
- Links verified before writing: github.com/litecrew-ai/litecrew-workspace answers
  ls-remote (HEAD bedf834, the exact import commit); the preview URL answers 200.
- New README (5.6KB, ASCII except the license-line copyright sign, matching
  LICENSE): showcase pitch; the Dead Web Gazette case summary with preview link and
  local-run commands; brief workspace introduction + "continue reading" link to the
  workspace repo; repository reading order; honesty notes updated to current truth
  (operator commits until 2026-08-29 10:04 UTC, agent commits at operator
  instruction since, each recorded in sessions/); MIT license retained.

## Decisions, on the record

- The honesty section now discloses the git-authorship change honestly instead of
  the pre-publication wording (all commits operator-made).
- Upstream's marketing content (badges, comparison tables, quick start for the
  product) belongs on the workspace repo, which the README now links to; this repo's
  README sells the exhibit, not the product.

## Follow-ups

- Commit+push follows per the standing submit-when-finished instruction.
- Same day, operator follow-up: "add screenshot" with /tmp/internet-archaeology.png
  (2880x1554 PNG, 481KB, operator-supplied). Copied to
  `docs/assets/internet-archaeology.png` (the established README-images directory;
  consistent in size with the skeleton's grandfathered images) and embedded in the
  README's case section directly under the preview link. Size note on the record:
  over the 100KB text-gate threshold, but a binary in the docs/assets convention;
  operator's gate call.
- Next productive activation under Goal `operate-internet-archaeology-blog`:
  cadence decision (SC1) or discovery enrichment (SC2).
