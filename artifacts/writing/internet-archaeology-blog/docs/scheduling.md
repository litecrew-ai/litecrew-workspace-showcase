# Recurring-run recipes

The pipeline is idempotent and single-command, so scheduling it is just
running `python3 run.py` on a clock. The dedup ledger
(`data/ledger.json`) makes each run cover only new subjects.

## Local cron

Run the gazette twice a week, off the top of the hour, logging to a file:

    23 7 * * tue,fri  cd /path/to/internet-archaeology-blog && /usr/bin/python3 run.py >> cron.log 2>&1
    41 7 * * tue,fri  cd /path/to/internet-archaeology-blog && /usr/bin/python3 run.py --fetch-screenshots >> cron.log 2>&1

Notes:

- Use an absolute python3 path (cron's PATH is minimal).
- `run.py` never fails hard on API outages; it degrades to the seed corpus
  and records the mode in `RESULT.md`. Non-zero exit only means the
  `--verify`-style checks found a real problem; cron mail will tell you.
- The `--fetch-screenshots` line needs two things on the host: egress to
  `web.archive.org` and a Chrome/Chromium-class browser binary (located via
  `$CHROME_BIN`, else a PATH probe of the common names, else the macOS app
  bundles -- see the artifact README). It renders each subject's archived
  page (`https://web.archive.org/web/<ts>/<url>`) with that browser; the
  former `web.archive.org/screenshot/` endpoint is dead and no longer
  called. From a network where the archive is unreachable it records the
  failure per subject and leaves every post on the honestly labeled
  generated plate; where it works, the rendered PNGs are stored under
  `assets/screenshots/` (never clobbered) and the next rebuild mounts them
  with a provenance label. Delete `assets/screenshots/<slug>.<ext>` to
  force a refetch of one subject. Budget ~20-50 minutes for 20 subjects:
  the CDX lookup is allowed 25s plus one retry per subject (a miss of any
  kind falls back to Wayback's nearest-capture `/web/2/` form), the
  archived-page pre-check is allowed 20s with one 15s-backed-off retry on
  an HTTP 503 challenge, the render is bounded by Chrome's own 30s
  `--timeout` (the wall guard at 75s only exists for a browser that
  ignores the flag), and subjects pause 4s apart.
- Steady state: draft one subject per run (the default). Bump with
  `--posts N` only when you plan editorial passes for N posts.

## CI sample (GitHub Actions)

Commit this as `.github/workflows/gazette.yml` when the operator approves a
CI setup. It is provided here as documentation only; nothing under
`.github/` was created or modified by the v0 Task.

```yaml
name: gazette
on:
  schedule:
    - cron: "37 6 * * tue,fri"   # twice weekly, off the top of the hour
  workflow_dispatch: {}          # allow manual runs

permissions:
  contents: write

jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Run the pipeline
        working-directory: artifacts/writing/internet-archaeology-blog
        run: python3 run.py --posts 1

      - name: Fetch real screenshots (render archived pages, best effort)
        working-directory: artifacts/writing/internet-archaeology-blog
        env:
          # ubuntu-latest runners ship google-chrome preinstalled at
          # /usr/bin/google-chrome (also on PATH, so the probe would find
          # it; CHROME_BIN pins it explicitly and documents the dependency).
          CHROME_BIN: /usr/bin/google-chrome
        run: python3 run.py --fetch-screenshots || true
        # GitHub-hosted runners have egress to web.archive.org, so this is
        # where real screenshot plates come from: a fail-fast offline render
        # probe runs first (data: page through the exact invocation, fresh
        # temp profile included -- a browser that cannot run the recipe
        # headlessly stops the step before any subject time is spent), then
        # the step resolves each subject's snapshot via the Wayback CDX API
        # (25s timeout + retry; a miss falls back to the era-anchored
        # /web/<YYYY>/ form using the fact sheet's peak/death/launch year --
        # /web/2/, which resolves to the MOST RECENT capture, only when the
        # sheet has no year) and renders
        # https://web.archive.org/web/<ts>/<url> with the runner's Chrome in
        # headless mode -- no packages installed, the browser is invoked as a
        # subprocess. Chrome's own --timeout (30s) is the capture bound; the
        # 75s wall guard is only the outer limit. It never fails the
        # workflow: per-subject failures degrade to the labeled generated
        # plate and are recorded in RESULT.md, with the browser's stderr
        # tail. Budget ~20-50 min for 20 subjects; the
        # default job timeout (360 min) covers it. Every stored binary is
        # size-reported there and by --verify; binaries are exempt from the
        # 100KB text-file gate by design (png/jpg under
        # assets/screenshots/ and site/assets/ only).

      - name: Offline unit tests (screenshot stage)
        working-directory: artifacts/writing/internet-archaeology-blog
        run: python3 -m unittest discover -s tests -v
        # URL construction, payload guards, browser detection, front-matter
        # editor, scratch-build consistency, plus local loopback renders
        # when a browser is present (CHROME_BIN carries over from above).

      - name: Verify the built site
        working-directory: artifacts/writing/internet-archaeology-blog
        run: python3 run.py --verify

      - name: Commit new drafts and site output
        run: |
          git config user.name "gazette-bot"
          git config user.email "gazette-bot@users.noreply.github.com"
          git add artifacts/writing/internet-archaeology-blog
          git diff --cached --quiet || git commit -m "gazette: scheduled run"
          git push
```

Caveats for CI use:

- The commit step commits machine drafts and rebuilt pages, not editorial
  passes. Posts publish only after a human moves a draft to
  `content/posts/`.
- Keyless APIs only, so no secrets are needed; if an API is rate-limited or
  blocked from the runner, the run records the fallback mode and continues.
- If the repository policy is "agents never touch git" (as in the exhibit
  repo this artifact lives in), drop the commit step and let the scheduled
  run be verification-only, or trigger it as a human-invoked flow.
