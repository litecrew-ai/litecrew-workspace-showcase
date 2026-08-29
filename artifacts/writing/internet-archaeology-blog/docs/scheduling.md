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
- The `--fetch-screenshots` line needs egress to `web.archive.org`. From a
  network where the archive is unreachable it simply records one failed
  attempt per subject and leaves every post on the honestly labeled
  generated plate; where it works, fetched screenshots are stored under
  `assets/screenshots/` (never clobbered) and the next rebuild mounts them
  with a provenance label. Delete `assets/screenshots/<slug>.<ext>` to
  force a refetch of one subject.
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

      - name: Fetch real screenshots (best effort)
        working-directory: artifacts/writing/internet-archaeology-blog
        run: python3 run.py --fetch-screenshots || true
        # GitHub-hosted runners have egress to web.archive.org, so this is
        # where real screenshot plates come from. It never fails the
        # workflow: per-subject failures degrade to the labeled generated
        # plate and are recorded in RESULT.md. Every stored binary is
        # size-reported there and by --verify; binaries are exempt from the
        # 100KB text-file gate by design (png/jpg under
        # assets/screenshots/ and site/assets/ only).

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
