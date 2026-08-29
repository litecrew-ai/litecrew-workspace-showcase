---
subject: writing
slug: post-generation-pipeline
tags: [content-pipeline, python-stdlib, static-site, deterministic-generation, editorial-split]
related_goals: [internet-archaeology-blog]
related_tasks: [blog-v0-pipeline, blog-design-overhaul, blog-publish-all]
related_knowledge: [writing/dead-web-source-catalog.md]
last_verified_date: 2026-08-29
status: active
---

# Recipe: a deterministic discovery-to-post pipeline with a human editorial gate

> How to build a recurring content pipeline in Python 3.11 stdlib only that
> discovers subjects, distills sourced fact sheets, drafts posts, illustrates
> them procedurally, and assembles a file://-safe static site -- while keeping
> human editorial text untouchable by automation.

## Background and trigger conditions

You need to produce a recurring publication (blog, digest, gazette) where
research is automated but publishing is human-gated, on a machine where no
package installs, no servers, and no LLM API keys are available. Also applies
whenever you want deterministic rebuilds of a content product.

## Core conclusion

Five stages, one command, two invariants:

    discover -> fact sheets -> scaffold drafts -> SVG illustration -> site build
    invariant 1: ledger dedup -- a covered subject is never drafted twice
    invariant 2: never clobber -- existing drafts/posts are never overwritten

The editorial split does the human gating: the pipeline writes only to
`content/drafts/`; publishing is the manual act of writing the edited post
into `content/posts/`; the site builds exclusively from `posts/`. Working
reference implementation: `artifacts/writing/internet-archaeology-blog/`
(`run.py` plus `pipeline/` package).

## Detailed explanation

### Stage layout

| Stage | Module | Artifact | Key rule |
| ----- | ------ | -------- | -------- |
| Discovery | fetch keyless APIs + seed corpus | candidate list with per-subject provenance | every API call has a timeout and a recorded fallback mode |
| Facts | merge fetched sources with confidence-tagged seed facts | `data/facts/<slug>.json` (distilled only, never raw dumps) | each fact carries confidence + canonical source URL |
| Drafting | deterministic template assembly | `content/drafts/<slug>.md` | no LLM needed; every sentence is a fact plus citation marker |
| Illustration | seeded procedural generation (`random.Random(crc32(slug))`) | inline SVG, also stored standalone | same slug in, same artwork out (assert in verify) |
| Site | tiny Markdown-subset renderer + page templates | static HTML, one copied stylesheet, inline SVG, RSS | relative links only; renders via file:// |

### The decisions that mattered

1. **Determinism everywhere.** Seeded randomness for art, sorted JSON dumps,
   stable candidate ordering. Clean-state builds are byte-identical to the
   tracked build, which makes "it works" an auditable claim (`diff -r`).
2. **Never clobber.** `write_draft` returns early if the file exists. This is
   what makes human editing safe alongside automation -- re-runs can never
   destroy an editorial pass.
3. **Glyph hygiene as a hard error.** The drafter raises if content contains
   non-ASCII; fetched text is folded to ASCII at ingestion (en dash -> "--",
   curly quotes -> straight). Without the boundary check, one fetched em dash
   crashes the publication gate later (this happened; see the artifact
   RESULT.md honesty notes).
4. **Verification is a run mode, not an afterthought.** `--verify` re-derives
   artwork, re-parses every HTML file with a tag-stack checker, resolves every
   internal link to a file, checks word counts, and walks the ledger. It found
   two real defects in v0 before shipping.
5. **Provenance travels with the post.** Front matter records the exact
   data-source mode string; the site renders it. Degraded runs cannot
   masquerade as fully-sourced ones.

### The presentation layer (from the design overhaul)

The template/CSS layer can be replaced wholesale without touching content
or the data stages -- the stages communicate only through parsed front
matter. What made the redesign low-risk (and what to copy):

1. **Design brief before templates.** Write a `docs/design.md` with a
   concept, type scale, palette (hex), grid, component inventory, and
   numbered decisions (D1, D2, ...), then a traceability matrix mapping
   every template element to a decision ID. The matrix is what keeps later
   template edits from drifting into "generic bootstrap" territory.
2. **Stylesheet as a build product.** Keep the hand-written CSS at a source
   path (`src/styles.css`) and have the builder copy it byte-identical into
   the output tree (`site/styles.css`). Pages link the built copy. This
   preserves the clean-state guarantee: a build into an empty directory
   reproduces the tracked output exactly, stylesheet included.
3. **Config, not code, for environment facts.** Feed URLs (RSS `base_url`),
   site title, and description live in a small JSON config with documented
   defaults; templates never bake in a domain.
4. **Assert data renders, not that boxes exist.** A verifier check like
   "PROVENANCE box present" passes on an empty box. The v0 site shipped
   "(no sources recorded)" in every SOURCES box because of a falsy-list
   front-matter parser bug (`if line.startswith("  - ") and current_list:`
   -- a freshly opened list is empty, hence falsy, so items were silently
   dropped). Fix once, then add the regression guard: every front-matter
   source URL must literally appear in the built page. The general trap:
   truthiness guards on containers that legitimately start empty; use
   `is not None`.
5. **Verifier additions that generalize to any generated site**: stylesheet
   resolves relative to every page; no `<script>` anywhere; feeds parse as
   XML and list exactly the published items; and the clean-state
   byte-identical rebuild belongs *inside* `--verify` (temp dir + recursive
   file-set and byte compare), not in a manual `diff -r` someone might
   forget.
6. **Deterministic ornament.** Decorative numbers (hit counter, exhibit
   numbers, plate numbers) are functions of build inputs (post count,
   publication order). Never `datetime.now()` in templates; RSS dates come
   from post front matter, so the feed is byte-stable across rebuilds.

### Editorial batch at scale (from the publish-all run)

Publishing 17 narratives in one batch is where the truthfulness law meets
real fabrication pressure. What held it, as reusable practice:

1. **Numbers are where fabrication hides.** In one drafting pass, unsourced
   texture numbers appeared four times -- a reader count for a panic, a
   derived percentage for an acquisition, "selling at a loss" specifics, even
   a pronunciation aside. The countermeasure: after drafting, audit every
   number, date, name, and superlative back to the fact sheet; hedge
   ("reported at the time", "by most accounts", "the company's own claims")
   or delete; record the caught items in the run log so the audit is
   visible. Interpretive prose is free; facts are not. Commentary can carry
   a post to length without a single new claim.
2. **Thin sheets can carry honest posts.** The thinnest subject (3 facts, no
   reaction threads) reached the word floor by saying the quiet part out
   loud -- "that is nearly the whole sourced record, and this gazette will
   not decorate it" -- and cross-citing a sibling subject's already-sourced
   facts for era context (add the cross-cited source to front matter).
   Declared thinness beats padded texture and reads better anyway.
3. **Probe the evidence API once more before accepting thinness.** A second
   pass over the reaction API (same keyless endpoint, the pipeline's own
   evidence function plus raw query variants) sometimes finds citable
   threads the discovery pass missed. If it finds nothing, that is a fact
   about the subject, not a license to invent.
4. **Index shape for scale: lead-plus-register.** A card grid that reads at
   3 posts walls up at 20. The shape that scales: category chips with
   counts, one lead card (newest, the only inline SVG on the page -- size
   gate stays trivial), then a compact complete-dispatch list so every post
   is one click from the front page. Rewrite the verifier to assert the
   arrangement (lead count and identity, row count, chip counts, order),
   not just presence.
5. **Ledger drift is usually stale prose, not lost work.** A ledger count
   that disagrees with a Task record often means a one-off run landed
   between two Task closures (here: an 11 -> 12 draft that the earlier Task
   conclusion never saw). Diagnose before mutating: assert set equality of
   seed corpus / ledger / posts, then reconcile mechanically
   (`post_exists`, draft lifecycle) and explain the drift in the run log.
6. **Scaffolds are disposable; published text is not.** Once an editorial
   pass exists in `posts/`, the machine scaffold has served its purpose and
   can be retired (`draft: null` in the ledger) so the drafts directory
   reads as "awaiting editorial pass", not "duplicate corpus". This does
   not weaken never-clobber: that rule protects files from automation
   during runs, and the facts persist in the fact sheets regardless.

### Future LLM hook

Replace the draft renderer's body function with an API call that takes the
fact sheet and returns prose under the same rules (no unsourced numbers, keep
the sources list). Nothing else in the pipeline changes. Until keys exist,
deterministic scaffolding is honest about being scaffolding.

### Verification

- End-to-end runs in live + degraded modes logged in the artifact RESULT.md.
- `--verify` ALL CHECKS PASS after two real failures were fixed.
- Second-run dedup proven: 20 candidates, 11 in ledger, 0 new drafts.
- Design overhaul: `--verify` ALL CHECKS PASS (63 checks) with the
  presentation-layer extensions; clean-state rebuild byte-compare now runs
  inside `--verify`; post bodies proven byte-identical (sha256) across the
  additive front-matter dek edit.
- Publish-all batch: 20 posts published (17 editorial passes in one run,
  442-615 words each), ledger/drafts/posts reconciled 20/0/20,
  `--verify` ALL CHECKS PASS (286 checks) including the D10 index-shape
  assertions; several unsourced texture numbers caught and removed during
  drafting, recorded in the artifact RESULT.md.

## Boundaries and counter-examples

- Deterministic scaffolds are not prose; publishing still requires a human
  (or a future LLM pass). Do not let scaffolds reach `content/posts/`.
- The tiny Markdown subset (headings, lists, quotes, links, bold) is a
  feature: editorial passes stay portable and the renderer stays auditable.
  If you need tables or images, extend the renderer, do not switch to a
  heavyweight framework for one feature.
- Per-subject fact files must stay distilled; storing raw API payloads will
  blow the 100KB-per-file gate and bury the facts.

## Reuse checklist

- [ ] Ledger written at draft time (coverage = drafted, not published).
- [ ] Never-clobber rule on every content path.
- [ ] ASCII-fold fetched text at ingestion; glyph-scan before writing files.
- [ ] Determinism assertions (regenerate-and-compare) in the verify mode.
- [ ] Per-post provenance (data-source mode) rendered on the public page.
- [ ] Design brief with decision IDs before writing templates; template
      elements traceable to the brief.
- [ ] Hand-written stylesheet copied from a source path by the builder, so
      clean-state rebuilds reproduce the output tree exactly.
- [ ] Verify asserts data *content* renders (e.g. each source URL on the
      page), not just that a container box exists.
- [ ] Clean-state byte-compare runs inside `--verify`, not as a manual step.
- [ ] No truthiness guards on containers that legitimately start empty.
- [ ] In batch editorial passes: audit every number back to the fact sheet
      before publishing; hedge or delete, and log what was caught.
- [ ] At corpus scale, assert the index arrangement (lead/rows/chips/order),
      not just that links exist.
- [ ] Reconcile ledger against seed corpus and posts by set equality before
      mutating any of them.

## Related

- Upstream knowledge: `[[writing/dead-web-source-catalog]]`
- Downstream application: `[[internet-archaeology-blog]]`

## Change history

| Date       | Change                                       | Triggered by (Task / Goal) |
| ---------- | -------------------------------------------- | -------------------------- |
| 2026-08-29 | Initial version from v0 blog build           | tasks/blog-v0-pipeline.md  |
| 2026-08-29 | Merged presentation-layer section (design brief workflow, stylesheet-as-build-product, falsy-list parser trap, render-regression guards) | tasks/blog-design-overhaul.md |
| 2026-08-29 | Merged editorial-batch-at-scale section (number auditing, thin-sheet honesty, evidence re-probe, lead-plus-register index, ledger-drift diagnosis, scaffold retirement) | tasks/blog-publish-all.md |
