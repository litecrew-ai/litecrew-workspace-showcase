---
status: done
goal: internet-archaeology-blog.md
assigned_agent: web-product-engineer
created: 2026-08-29
updated: 2026-08-29
---

# Task: Blog v0 — discovery-to-post pipeline and first published posts

## Description

First Task of Goal `internet-archaeology-blog`. Build the v0 of the product as a live
asset at `artifacts/writing/internet-archaeology-blog/` (Eve-approved live-asset path —
this is the ongoing blog product, not one-shot Task output), and produce the first
batch of posts with it.

The product is a static blog that regularly scours the internet for subjects from the
dead and old web (defunct websites, old forums, 2000s blogs, early internet products,
strange personal homepages, dead startups, old software, online subcultures, forgotten
stories) and generates an illustrated post per subject. Working display title: "The
Dead Web Gazette" (you may rename it — record the rationale in the artifact README).

v0 scope, end to end:

1. **Discovery** — a module that assembles candidate subjects from at least two live
   keyless public APIs (suggested: Wikimedia category/API for defunct-site lists,
   Internet Archive Wayback CDX for domain lifespan metadata, Hacker News Algolia for
   shutdown stories). It must degrade gracefully to a bundled offline seed corpus
   (10-20 well-documented subjects) when the network is unavailable, and record which
   data-source mode (live / offline) produced each post.
2. **Fact research** — per subject, distill a fact sheet (founded, by whom, peak
   users/traffic if attestable, shutdown date, cause, afterlife) from fetched sources
   (Wikipedia extracts, archive metadata). In offline mode, only facts you can attest
   with high confidence, conservatively worded, with canonical source URLs listed for
   human verification.
3. **Post writing** — generate posts from fact sheets. The requested narrative style
   is evocative and terse ("In 2004, someone built a website. That website once had
   3 million users. Today, no one remembers it."). v0 pipeline output is a scaffolded
   draft assembled deterministically from the fact sheet; the editorial quality pass
   for this first batch is performed by you (the resident writer) directly in the
   post files. Document the future LLM-API hook as an extension point (no API keys
   exist in this environment — do not call any LLM API).
4. **Illustration** — at least one procedurally generated SVG per post, deterministic
   per subject (seeded by slug), in a period-appropriate early-web aesthetic (88x31
   buttons, hit counters, table borders, tiled starfields, marquee vibes). No external
   image services.
5. **Site** — a static site (index, post pages, about page stating what the blog is
   and how posts are generated) built by a Python 3.11 stdlib-only build script.
   Rendering must work when opened via file:// (no server, no JS build step).
6. **Recurring runs** — a single-command entry point (`python3 run.py` or equivalent)
   that performs discover -> skip-already-covered (dedup ledger at
   `data/ledger.json`) -> generate -> rebuild. Include a scheduling recipe (cron line
   plus a CI workflow sample) as a doc inside the artifact directory. Do not create
   or modify anything under `.github/`.

## Completion criteria

- [ ] `artifacts/writing/internet-archaeology-blog/README.md` exists and explains:
      architecture, data sources, pipeline stages, run instructions, key decisions,
      and the v0 limitations (manual editorial pass, LLM-API extension point).
- [ ] The pipeline runs end to end via the documented single command; a run log
      (e.g. `RESULT.md`) records what ran, in which data-source mode, and how it was
      verified.
- [ ] At least 3 posts are published on the built site. Each post has: a narrative of
      at least 400 words in the requested style; at least one generated SVG
      illustration; front matter / metadata listing sources and provenance
      (data-source mode, generation date, generator).
- [ ] The site builds from a clean state and renders; you verified rendering (open
      the output HTML and check structure — links resolve, SVGs inline, index lists
      all posts) and recorded the verification method in the run log.
- [ ] The dedup ledger exists and a second run correctly skips covered subjects.
- [ ] Content rules hold everywhere: English only; no emoji; no check-mark or
      checkbox glyphs (U+2713, U+2714, U+2705, U+2611 and family — use plain "OK" /
      "pass"); no invented statistics or quotes — every factual claim traceable to a
      cited source or explicitly hedged.
- [ ] Knowledge captured per `workflows/knowledge-sediment-protocol.md` under
      `knowledge/writing/` (suggested: a dead-web source catalog note and a post-
      generation pipeline note; merge if one file serves better), with `INDEX.md`
      updated and template-compliant frontmatter.
- [ ] Artifact placement per `workflows/artifacts-lifecycle.md`: business README at
      `artifacts/writing/README.md` listing the live asset, and a root
      `artifacts/README.md` pointer (Eve grants writes to these two shared files for
      this Task only).

## Context and constraints

- **Workspace**: your cwd is the workspace root. Read `goals/internet-archaeology-blog.md`
  for product framing. No handbook exists yet for development work — check
  `handbooks/` and `knowledge/` (both effectively empty) and note the gap if it bites.
- **Write boundaries**: the Task file (this file), `knowledge/writing/`,
  `artifacts/writing/internet-archaeology-blog/`, `artifacts/writing/README.md`,
  `artifacts/README.md`. Nothing else. Never edit goals, other tasks, handbooks,
  workflows, templates, or agent definitions.
- **Publication standards** (this repo is a published exhibit; operator gates block
  violations): no CJK text; no emoji; no check-mark glyphs; no single text file over
  100KB — keep any fetched-data cache trimmed to distilled facts, never raw dumps.
- **Stack**: Python 3.11 stdlib only. No pip installs, no Node, no servers. Network
  limited to the keyless public APIs named above; degrade to offline mode on failure.
- **Git**: run no git commands at all. The human operator commits at the activation
  boundary. (This intentionally supersedes the `git add` advice in
  knowledge-sediment-protocol section 3.1 for this repo — operator-side single commit
  achieves the same history preservation.)
- **Truthfulness law**: a post may be dramatic in tone but never fictional in fact.
  If a number cannot be sourced, it does not appear, or appears hedged ("reported at
  the time as...") with the source named.

## Execution steps

<!-- Subagent fills -->

### Preparation (mandatory retrieval, round 1)

- `handbooks/`: only `README.md` exists; no domain playbook (e.g. `development.md`).
  Gap noted — worked from the Goal text, the Task constraints, and stdlib habits instead.
- `knowledge/`: only `README.md`; nothing to retrieve. This run therefore creates the
  first notes under `knowledge/writing/`.
- Read in full: Goal, this Task, `workflows/subagent-workflow.md`,
  `workflows/knowledge-sediment-protocol.md`, `workflows/artifacts-lifecycle.md`,
  `templates/knowledge-template.md`. Read-only compliance pass over `PUBLICATION.md`
  gates (business whitelist `writing/` OK; ASCII-only; no check-mark glyphs; no absolute
  operator paths in produced files; 100KB text cap) and `.gitignore` (artifacts tracked).
- Environment probe: Python 3.11.2. Network: `hn.algolia.com` reachable (HTTP 200);
  `en.wikipedia.org` and `web.archive.org` time out from this environment. The pipeline
  will implement all three keyless APIs with short timeouts and degrade per stage, and
  the run log will record the mixed mode honestly.

### Plan

1. Scaffold artifact directory `artifacts/writing/internet-archaeology-blog/` with
   `pipeline/` package, `data/seed_corpus.json`, `run.py`, `docs/`, `content/posts/`.
2. Implement discovery (HN Algolia live; Wikipedia category + Wayback CDX with timeout
   and fallback), fact-sheet distillation, deterministic post scaffolding, seeded SVG
   illustration generator (88x31 button, hit counter, tiled starfield, table border),
   and a stdlib-only static-site builder that inlines SVGs (file:// safe).
3. Implement `data/ledger.json` dedup and the never-clobber rule for existing post
   files (so editorial passes survive re-runs).
4. Run the pipeline; write the first 3 posts' editorial pass by hand on top of the
   generated scaffolds; rebuild the site.
5. Verify: second run skips covered subjects; HTML structure check (links resolve,
   inline SVG present, index lists all posts); record method and results in `RESULT.md`.
6. Write artifact `README.md`, `docs/scheduling.md` (cron + CI sample, no `.github/`
   changes), `RESULT.md`.
7. Register live asset in `artifacts/writing/README.md` and root `artifacts/README.md`.
8. Capture knowledge under `knowledge/writing/` (source catalog + pipeline recipe)
   with `INDEX.md`, per sediment protocol.
9. Final self-check against every completion criterion; fill Conclusions.

## Execution log

<!-- Append after each subagent iteration -->

| Round | Date       | Progress | Notes |
| ----- | ---------- | -------- | ----- |
| 1 | 2026-08-29 | Retrieval done, plan set, environment probed | No handbooks/knowledge exist (gap); Algolia reachable, Wikipedia + Wayback CDX not; mixed-mode design chosen |
| 2 | 2026-08-29 | Pipeline implemented (discovery/facts/writing/svgart/site, run.py, seed corpus 20 subjects) | First run live Algolia + offline wiki/CDX; 3 drafts |
| 3 | 2026-08-29 | Draft crash fixed | Fetched HN title carried U+2013 en dash; glyph guard aborted a draft. Added ASCII-fold at ingestion (boundary rule). Crash recorded honestly in RESULT.md |
| 4 | 2026-08-29 | 11 subjects drafted, ledger proven across runs (run 2 skipped 3; later run skipped all 11, 0 new) | Dedup criterion demonstrated |
| 5 | 2026-08-29 | Editorial pass 1 written for 3 posts (geocities 553w, google-reader 534w, winamp 442w); site rebuilt | Post URLs cross-checked against fact sheets (caught 3 mis-transcribed HN item ids before publishing); one unsourced age/superlative/nationality claim softened or removed |
| 6 | 2026-08-29 | Verification: --verify found 2 real defects (about home link; verifier/builder SVG drift), fixed; final ALL CHECKS PASS; clean-state build byte-identical (diff -r to scratch dir); SVG XML parse OK; browser file:// navigation OK but screenshot tooling broken (recorded honestly) | Verification methods + results in artifacts/writing/internet-archaeology-blog/RESULT.md |
| 7 | 2026-08-29 | Docs closed out: artifact README, docs/scheduling.md (cron + CI sample), RESULT.md verification record; live asset registered in artifacts/writing/README.md and artifacts/README.md; knowledge captured under knowledge/writing/ (+INDEX) | Tree-wide gate scan of all 51 produced files: zero glyph violations, zero oversize |

## Conclusions and output

### What was built

- **Live asset** at `artifacts/writing/internet-archaeology-blog/` (The Dead
  Web Gazette, title kept; rationale in its README).
- **Pipeline** (Python 3.11 stdlib only, `run.py` + `pipeline/` package):
  discovery (HN Algolia live + Wikipedia category + Wayback CDX with
  per-source timeout/degradation, offline seed corpus of 20 subjects),
  fact-sheet distillation (confidence-tagged, canonical URLs, distilled
  only), deterministic post scaffolding into `content/drafts/`, seeded
  procedural SVG illustration, and static-site assembly from
  `content/posts/` (file:// safe, inline CSS/SVG, no JS).
- **Published posts (3)**: GeoCities (553 words), Google Reader (534),
  Winamp (442). Each: narrative in the requested register, at least one
  generated SVG (inline + standalone), front matter with sources and
  provenance (data-source mode, dates, generator, editor), rendered
  PROVENANCE and SOURCES boxes on the page. 8 further subjects sit as
  drafts awaiting future editorial passes.
- **Dedup ledger** `data/ledger.json` (11 subjects covered) proven across
  runs; never-clobber rule protects editorial work.
- **Docs**: artifact README (architecture, sources, decisions, limitations),
  `docs/scheduling.md` (cron line + CI workflow sample as documentation;
  nothing under `.github/` touched), `RESULT.md` run log + verification
  record.

### Key decisions and why

- Drafts vs posts split: automation drafts, the human pass publishes; this
  is the honest reading of the Task's editorial requirement and makes the
  LLM extension point a one-function swap in `pipeline/writing.py`.
- ASCII-fold fetched text at ingestion + hard-error glyph guard in the
  drafter: publication gates are enforced at write time, not at commit time
  (one real crash proved the guard works).
- Determinism asserted by the verifier (regenerate-and-compare, clean-state
  build byte-identical to the tracked build).
- Mode honesty: every post carries its exact data-source mode string; in
  this environment HN Algolia answered while Wikipedia/CDX did not, so
  facts trace to the seed corpus plus live citable HN threads.

### Verified versus assumed

- Verified: end-to-end runs in mixed mode; 3 published posts render with
  inline SVG, resolve all internal links, list on the index; word counts
  >= 400; second run skips covered subjects (20 candidates -> 11 skipped,
  0 new); clean-state build identical to tracked build; all SVG parses as
  XML; tree-wide glyph/size gates clean (51 files); one real browser
  navigation of the index via file:// succeeded.
- Assumed / not verified: pixel-level rendering by eye (browser screenshot
  tooling failed in this environment -- recorded in RESULT.md); Wikipedia
  and CDX code paths work as written but were only exercised through their
  failure handlers here.

### Limitations and follow-up suggestions

- Editorial passes for the remaining 8 drafts (aim, napster, friendster,
  msn-messenger, altavista, myspace, delicious, google-plus) -- good
  material for the next Task toward the Goal's 12-post SC2.
- 9 seed subjects not yet drafted; discovery depends on HN-era chatter, so
  pre-2007 deaths rely on the seed corpus.
- No RSS feed yet; site styling is deliberately spartan.
- Handbook gap: no `handbooks/development.md` existed. Suggested new
  section (Eve to review): "Content products: verify what you publish" --
  the five checks from run.py --verify (link resolution, tag balance,
  regeneration determinism, glyph gate, size gate) as the default exit
  criteria for any Task that produces generated text or HTML. The deeper
  detail already lives in `knowledge/writing/post-generation-pipeline.md`.

## Knowledge-capture suggestions

Captured under `knowledge/writing/` (business dir `writing`, first notes
there; INDEX.md created; frontmatter per template; merge-over-create
checked against an empty knowledge tree):

- `knowledge/writing/dead-web-source-catalog.md` -- the three keyless APIs,
  what each yields for dead-web research, reachability reality from this
  environment, and ingestion traps (Unicode titles, pre-2007 blind spot).
- `knowledge/writing/post-generation-pipeline.md` -- the deterministic
  discovery-to-post recipe: ledger dedup, never-clobber editorial split,
  glyph hygiene at boundaries, verifier-first mindset, LLM hook location.

Eve may also want to note the session-level lesson: publication gates are
cheap when enforced at write time inside generators, expensive when
discovered at commit time.

