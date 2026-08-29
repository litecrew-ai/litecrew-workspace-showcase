---
subject: writing
slug: post-generation-pipeline
tags: [content-pipeline, python-stdlib, static-site, deterministic-generation, editorial-split]
related_goals: [internet-archaeology-blog]
related_tasks: [blog-v0-pipeline, blog-design-overhaul, blog-publish-all, blog-screenshots-and-paths, blog-screenshot-renderer, blog-render-timeout-fix, blog-render-profile-fix, blog-image-search-route]
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

### Truthful images: real screenshots versus generated art (from the screenshots-and-paths run, strategy fixed in blog-screenshot-renderer)

When a content product shows pictures "of" a subject, the truthfulness law
needs an image-mode equivalent. What generalized:

1. **Two modes, no middle state.** A plate is either a *screenshot* (pixels
   a real browser rendered from the subject's real archived page) or
   *generated* (the product's own procedural art). Both carry a visible
   label; the mode lives in front matter (`illustration: screenshot |
   generated`) plus provenance fields (subject URL, archived playback URL,
   snapshot timestamp, fetch date) and renders into the page's provenance
   box. Anything else -- a mockup, a stand-in, a "representative" image --
   is fabrication.
2. **Verify the endpoint's contract before designing around it -- and get
   evidence from a reachable network.** The documented Wayback screenshot
   service (`web.archive.org/screenshot/<url>`) turned out to be dead: an
   operator run from a network with archive egress got HTTP 404 with an HTML
   error page for all 20 subjects. From inside a blocked network, "dead" and
   "blocked" look identical (both fail at the connection layer), so the
   design error was only provable once someone with egress ran it. When an
   integration is untestable from your box, ship the honest degraded path
   AND an operator-runnable probe, then believe the probe's output over the
   documentation.
3. **Render, don't fetch -- and bound the capture with the BROWSER'S OWN
   `--timeout`, not your wall clock.** The robust way to picture an
   archived page is the playback URL itself: resolve a timestamp (CDX), then
   have a real browser screenshot `https://web.archive.org/web/<ts>/
   <original-url>`. No image API in the middle to die. The browser is an
   external binary invoked with `subprocess` (stdlib only): locate it via
   `$CHROME_BIN`, else a PATH probe of common names, else macOS app bundles;
   run it once per subject with `--headless=new --screenshot=<tmp>
   --window-size=... --virtual-time-budget=~10000 --timeout=~30000
   --hide-scrollbars --disable-gpu --no-first-run
   --no-default-browser-check --disable-crash-reporter
   --disable-component-update --disable-background-networking
   --user-data-dir=<fresh temp profile per render>` (see item 12 for why the
   profile and the suppression flags are load-bearing).
   The lesson cost one full laptop run (20/20 renders dead): a
   `--virtual-time-budget`-only invocation NEVER fires a capture while a
   network load is pending -- Wayback pages chain every subresource through
   more archive redirects, "load complete" never arrives, and your wall kill
   is the only thing that stops the process, with no file written.
   `--timeout=<ms>` is the mechanism that actually captures: the browser
   exits at ~timeout+1s and always writes the PNG, whether the page stalled
   on a hanging subresource or an unroutable host (both measured). Keep the
   wall budget (process-group kill) only as the outer guard with clear
   headroom, and pipe the browser's stderr into the failure log with
   chrome/updater noise lines filtered and BOTH the head (~400) and tail
   (~500) kept -- on
   the reference chromium it literally says `Page load timed out ...
   N bytes written to file`, which is what makes the next run
   self-diagnosing. Caveat to state honestly: on current new-headless
   chromium (150) the timeout capture of a never-loading page is a BLANK
   frame (headless does not composite before load-complete), so the
   calibrated floor still rejects it -- the subject degrades, but with the
   reason on the record instead of a silent kill.
4. **Hanging networks and failing networks produce different forgeries.**
   Measured with a real chromium: pointed at an unroutable host, the
   browser *never exits and writes no file* (killed at 100s) -- your own
   subprocess timeout is the only bound. Pointed at a fast-failing target
   (closed port, NXDOMAIN), it *writes a genuine PNG of its own error
   page* (21768 bytes at 1024x640) that passes any magic-byte check. So
   payload sniffing alone cannot keep a browser error page out of the
   product. Layer the guards: (a) HTTP 200 pre-check of the exact URL you
   are about to render, plus a content check that the body is a playback
   page; (b) PNG magic bytes; (c) exact window dimensions; (d) a size floor
   **calibrated locally** by rendering a blank page (3301 bytes), the error
   page (21768), and a real content page (67398) -- the floor sits just
   above the error page. Every rejected render degrades that subject with
   the reason logged.
5. **Resolve the browser once; degrade once.** Discovering the binary is a
   per-run step, not a per-subject one. No browser found means zero network
   work: skip every subject with one actionable message ("set CHROME_BIN or
   install Chrome/Chromium"), not twenty identical apologies. A broken
   CHROME_BIN must be reported as such, never silently fallen back.
6. **Budget for the slow index, and degrade to an ERA-ANCHORED nearest
   capture -- never the bare most-recent form.** CDX
   answered only 5 of 20 lookups inside 5s from a reachable network (a later
   run: 17 of 20 with a 25s budget); the working budget is a 25s timeout,
   one retry, and a circuit breaker that skips remaining lookups after ~4
   consecutive transport failures. A CDX miss of ANY kind (timeout, no
   status-200 row, open breaker) should not skip the render -- but the naive
   fallback `https://web.archive.org/web/2/<url>` resolves to the MOST
   RECENT capture Wayback has, and for a dead site whose domain is now
   parked that means a screenshot of the parked page (observed in the
   operator's third-run log: altavista resolving to a 2026 parked page).
   Anchor the fallback instead: `https://web.archive.org/web/<YYYY>/<url>`
   resolves to the capture nearest that year, so take YYYY from the
   subject's own sourced fact sheet with a deterministic, unit-tested
   priority -- a peak phrasing ("most-visited...", "tens of millions...")
   beats a death phrasing ("shut ... down", "closed", "retired",
   "bankruptcy", "sunset"; mind verb-object forms like "shut AltaVista
   down"), which beats a launch phrasing; a sheet with no year degrades to
   /web/2/ as the documented last resort. Recover the real
   timestamp from the redirect target's final URL when the pre-check fetch
   reports it, and label the plate "nearest capture" when it does not --
   never date a plate by guesswork, and never present the anchor year as the
   snapshot date. Politeness belongs at the pre-check too:
   one laptop run drew five HTTP 503 archive-challenge pages, so a 503 gets
   a ~15s backoff and exactly one retry, and subjects space ~4s apart.
7. **Degrade per subject, log every attempt.** Each subject resolves,
   pre-checks, and renders independently; failure degrades that subject to
   generated art, labeled. The run record lists every attempt (HTTP code,
   bytes, error string) so a future operator knows exactly what was tried.
   When the run log nears its size gate, keep per-subject lines on stdout
   and append a condensed outcome summary instead.
8. **Never-clobber binaries; refetch is explicit.** Stored screenshot files
   are source assets the builder copies into the build (byte-identical,
   like the stylesheet), so clean-state rebuilds stay deterministic.
   Re-rendering means deleting the file first.
9. **Additive-only front matter with a body hash post-condition.** When
   automation must add metadata to frozen editorial files, edit only the
   front-matter block, splice before the closing delimiter, and sha256 the
   body before/after as a hard assertion (the fetch mode returns non-zero
   on mismatch). This is the mechanical guarantee behind "post bodies stay
   frozen".
10. **Gate binaries explicitly.** A "no text file over N KB" gate will
    either falsely flag image binaries or silently skip them. Split it:
    text files over N KB fail; png/jpg under an assets path are allowed,
    individually size-reported, and any other binary anywhere fails.
11. **Test the untestable path without pretending.** Where the real archive
    is unreachable, the machinery is still testable: unit-test URL
    construction, payload guards, browser detection (restricted PATH /
    broken CHROME_BIN), and the additive front-matter editor offline;
    verify the build consistency with a synthetic PNG in a scratch tree;
    and, when any chromium exists locally, render a loopback page and a
    deliberately closed port through the real subprocess path. The
    environment-dependent tests skipUnless a browser exists, so the suite
    is green on machines without one.
12. **Environment divergence: a recipe proven on a clean box can hang on a
    daily-driver machine -- isolate the profile, filter the noise, and ship
    a self-probe.** A third operator laptop run lost every render to the
    wall guard with NOTHING but chrome/updater crash-handler noise on
    stderr. The shipped diagnosis said "no --user-data-dir, so the default
    profile is locked" -- but code inspection showed the invocation already
    passed a fresh temp profile per render, and the run's own error string
    ("75s wall guard") existed only in that code: the laptop had hung WITH
    the isolation in place. Lessons that generalize: (a) verify a diagnosis
    against the code and the evidence BEFORE shipping the fix narrative --
    environment failures attract confident wrong theories; (b) make the
    invocation maximally environment-independent anyway: fresh temp
    `--user-data-dir` per render (created and removed around the run, so no
    dependence on the user's browser state or its singleton locks),
    `--no-first-run --no-default-browser-check`, and the helper-suppression
    trio `--disable-crash-reporter --disable-component-update
    --disable-background-networking`; (c) filter chrome/updater noise lines
    out of captured stderr and keep BOTH head and tail -- an all-noise
    stderr with no output file is itself a diagnostic signature, so print
    an explicit hint for exactly that case; (d) ship an OFFLINE self-probe
    that runs the exact production invocation (data: URL, so no network)
    and validates magic/dimensions/a non-blank floor -- expose it as a CLI
    mode ("the first thing to run on any new machine") and auto-run it
    fail-fast at the start of the real batch, so a doomed 25-minute run
    becomes a 10-second diagnosis; (e) never claim the other machine is
    fixed from a clean box -- claim the recipe is environment-independent
    and self-verifying, and let the operator's probe be the truth. The
    profile-lifecycle contract (fresh per render, not pre-created, removed
    after, never reused) is provable offline with a recorder "browser"
    script that dumps its argv -- no real browser or network needed.

13. **The acquisition cascade: search -> license-clean repository -> render,
    each route with its own truthfulness contract** (from the image-search
    run, 2026-08-29, which landed real plates for 20/20 subjects from a
    network where the archive is unreachable). When one acquisition route is
    environment-blocked, order the alternatives by (a) reachability from the
    build box, (b) rights cleanliness, (c) fidelity -- here: Bing image
    search (live, varying rights, attribution required) -> Wikimedia Commons
    (license-clean, laptop-only from here) -> the archived-page render
    (highest fidelity, probe-gated, needs browser + archive egress). One
    CLI mode runs the cascade per subject; env toggles disable routes for a
    run; the first route that stores a binary wins the subject; never-
    clobber spans routes (a subject with any stored plate binary is skipped
    whole). What kept the truthfulness law intact on the search route:
    (a) a THIRD plate mode -- `sourced-image` -- distinct from `screenshot`
    (reserved for our own archive renders) and from `generated`; the front
    matter carries `image_source`, source page, image URL, retrieval date
    (license + author for the repository route), and the plate label says
    "historical image: Bing image search" / "via Wikimedia Commons, license"
    with the source-page host; (b) STRICT subject match before anything is
    fetched -- a word-boundary form of the subject name/alias/domain must
    appear in the candidate's RAW title or source page URL (near-miss
    spellings like "Geocites" reject; short aliases like "aim" match only on
    word boundaries so "claim" can never match; non-ASCII title runs count
    as separators -- ASCII-folding the title FIRST glued "GeoCities"+CJK
    into a non-match, so match on raw and fold only for storage);
    (c) guards shared by both routes -- magic bytes for four formats,
    parseable dimensions (jpeg SOF / png IHDR / gif LSD / webp VP8+VP8L+
    VP8X -- mind that a VP8L file under 30 bytes trips an outer length
    guard), width floor, size floor against spacers, and a hard cap;
    (d) fixture-test the parser against a sanitized real fetch (ASCII-fold
    the fixture or it fails the glyph gate; re-serialize candidate JSON with
    ensure_ascii + HTML-escape so the file shape matches the live m="..."
    attributes exactly); (e) a verify suite that asserts mode/binary/label
    agreement AND visible attribution (the source-page URL link, accepting
    the HTML-escaped form -- a URL with a query string renders as &amp; and
    a literal substring check fails otherwise). Two debugging traps worth
    remembering: a plain function saved on a TestCase class attribute comes
    back as a BOUND METHOD on instance access (the descriptor protocol --
    it silently poisons restore-after-patch test code; hold originals in
    locals + addCleanup), and real search-result image URLs contain raw
    spaces/control characters (percent-encode before http.client, or the
    batch dies mid-run with InvalidURL).

### Subpath mount robustness (from the same run)

User report: "style missing when I mount the site as a relative path like
localhost/site/". Reproduce before fixing -- the diagnosis was not what it
looked like:

1. **Page-relative refs are correct on conforming servers.** Serving the
   built site with stdlib `http.server` rooted at the repo root, browsing
   `/<deep>/<subpath>/site/` with a trailing slash resolved every internal
   reference (stylesheet, nav, all 40+ links) at HTTP 200; the no-slash
   form was 301-redirected to the slash form. The breakage instead
   reproduces with any *root-absolute* ref (`/styles.css` -> 404 under a
   subpath), which is what page-relative refs degrade into when a rewriting
   server serves `/site` without the slash redirect.
2. **Fix by config, not by switching modes.** Keep page-relative as the
   default (file:// safety) and add a `path_prefix` config (empty default;
   `/site/` when set) that routes *every* internal href/src through one
   resolver emitting prefix-absolute URLs from any depth. RSS links combine
   `base_url + prefix`. One resolver function is the audit surface: grep it
   to prove no emitter bypasses it.
3. **Mounted-subpath server test inside verify.** Start
   `ThreadingHTTPServer` on 127.0.0.1 port 0 rooted at the repo root (or a
   temp root), browse the index and a post page the way a browser would
   (follow redirects, urljoin every href/src, GET each), assert 200 for
   all, in BOTH modes -- the tracked default build at its real subpath, and
   a scratch prefix-mode build served at `/site/` with an added assertion
   that no non-prefixed internal ref remains. This turns "it mounts" from
   an assumption into a checked property and reproduces the user's exact
   failure mode on every verify run.

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
- Render-timeout fix: the operator's 20/20 no-file render failure reproduced
  on a loopback stalled-subresource page with the real chromium
  (vtb-only recipe: no exit, no file); with `--timeout` the browser
  self-captures at ~timeout+1s and always writes a PNG (also for unroutable
  hosts). Regression test added; full suite green; see the artifact
  RESULT.md entry for 2026-08-29 (blog-render-timeout-fix).
- Render-profile fix (environment divergence): the shipped "missing
  --user-data-dir" diagnosis was disproven by code inspection (the flag was
  already present, and the operator's error string only exists in that
  code); invocation hardened anyway (helper-suppression flags,
  noise-filtered head+tail stderr, explicit all-noise hint), offline
  self-probe added and wired fail-fast (PASS on this box's chromium,
  10990 bytes / ~1s), era-anchored /web/<YYYY>/ fallback with a
  deterministic peak>death>launch year rule (all 20 tracked sheets anchor
  inside the subject's life; scratch-tree rehearsal showed correct
  era-anchored URLs end to end), 55 unit tests green, --verify 393 checks
  ALL PASS; RESULT.md rotated to docs/result-log/archive-1.md. The laptop
  hang itself is NOT reproducible on this box (no running GUI Chrome) -- the
  operator's 10-second --probe-render run is the confirming step; see the
  artifact RESULT.md entry for 2026-08-29 (blog-render-profile-fix).
- Image-search route (2026-08-29): the cascade ran LIVE from the build box
  and stored strict-matched, attributed, guard-passing images for 20/20
  subjects (816969 bytes total, all under the 100KB cap; per-subject table
  in the artifact RESULT.md); post bodies proven byte-identical (sha256)
  across the additive front-matter stamps; 87 unit tests green (32 new, on
  the sanitized real-fetch fixture and a loopback search+image server);
  --verify 475 checks ALL PASS with the sourced-image mode/label/attribution
  assertions. The Wikimedia Commons route is implemented and fixture-tested
  but laptop-only from this network (SSL handshake timeout recorded).

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
- [ ] For image plates: declare mode in front matter, label it on the page,
      render the real page rather than trusting an image API, bound the
      capture with the browser's own --timeout (a wall kill alone produces
      no file on stalled pages), layer payload guards (http pre-check +
      playback-content check + magic bytes + exact dimensions + calibrated
      size floor), fall back to an ERA-ANCHORED nearest-capture form on
      index misses (year from the subject's own fact sheet; the bare
      most-recent form screenshots whatever parks on the domain today) and
      label unresolved timestamps as such, resolve the browser once and
      degrade once when absent, log every attempt with the browser's
      noise-filtered stderr (head and tail), and hash-check bodies when
      editing front matter of frozen files.
- [ ] For headless-browser stages on foreign machines: fresh temp
      --user-data-dir per render (created/removed around it), first-run and
      helper-suppression flags, an offline self-probe through the exact
      invocation exposed as a CLI mode AND auto-run fail-fast before the
      batch, and a README troubleshooting table keyed to observed stderr
      signatures.
- [ ] For image acquisition: order routes by reachability/rights/fidelity
      behind one cascade CLI with per-route env toggles; give each route
      its own honest plate mode and label; strict-match candidates against
      the subject (raw title, word boundaries, alias and domain) before
      fetching; guard binaries (magic, dimensions, width floor, size floor,
      cap); store source-page attribution with the binary and render it as
      a visible link; fixture-test parsers against sanitized real fetches;
      percent-encode fetched URLs before the request and ASCII-validate
      them before storage.
- [ ] For mounts: one URL resolver for all internal refs; page-relative
      default + config-driven prefix mode; a mounted-subpath HTTP browse
      test in verify for both modes.

## Related

- Upstream knowledge: `[[writing/dead-web-source-catalog]]`
- Downstream application: `[[internet-archaeology-blog]]`

## Change history

| Date       | Change                                       | Triggered by (Task / Goal) |
| ---------- | -------------------------------------------- | -------------------------- |
| 2026-08-29 | Initial version from v0 blog build           | tasks/blog-v0-pipeline.md  |
| 2026-08-29 | Merged presentation-layer section (design brief workflow, stylesheet-as-build-product, falsy-list parser trap, render-regression guards) | tasks/blog-design-overhaul.md |
| 2026-08-29 | Merged editorial-batch-at-scale section (number auditing, thin-sheet honesty, evidence re-probe, lead-plus-register index, ledger-drift diagnosis, scaffold retirement) | tasks/blog-publish-all.md |
| 2026-08-29 | Merged truthful-images section (two-mode labeling, magic-byte sniffing, per-subject degradation, additive front matter with body-hash post-condition, binary gate split) and subpath-mount section (reproduce-first diagnosis, single URL resolver with path_prefix, mounted-subpath HTTP test in verify) | tasks/blog-screenshots-and-paths.md |
| 2026-08-29 | Truthful-images section rewritten for the render-don't-fetch strategy: dead-endpoint evidence from a reachable network, subprocess browser invocation with process-group timeout, hang-vs-fast-fail forgery asymmetry and the layered payload guards with locally calibrated size floor, resolve-browser-once degradation, CDX latency budget with circuit breaker, and testing the untestable path without pretending | tasks/blog-screenshot-renderer.md |
| 2026-08-29 | Render-timeout lesson merged: virtual-time-budget alone never captures while a load is pending (the 20/20 dead-render laptop run), chrome's own --timeout is the capture mechanism (blank-frame caveat on new headless), stderr tails for self-diagnosis, the nearest-capture /web/2/ fallback with timestamp recovery and honest labeling, and 503 backoff at the pre-check | tasks/blog-render-timeout-fix.md |
| 2026-08-29 | Environment-divergence lesson merged (item 12: verify the diagnosis against the code before shipping the fix narrative; fresh temp profile per render; helper-suppression flags; noise-filtered head+tail stderr with an all-noise hint; offline self-probe as CLI mode + fail-fast pre-flight; recorder-browser profile-lifecycle proof), fallback rewritten to era-anchored /web/<YYYY>/ with the peak>death>launch year rule and the parked-domain hazard of /web/2/ | tasks/blog-render-profile-fix.md |
| 2026-08-29 | Acquisition-cascade lesson merged (item 13: route ordering by reachability/rights/fidelity; the third sourced-image plate mode with visible attribution; strict raw-title word-boundary matching; shared binary guards incl. four-format dimension parsing; sanitized real-fetch fixtures; escaped-URL-aware attribution checks; descriptor-protocol and raw-space-URL debugging traps) | tasks/blog-image-search-route.md |
