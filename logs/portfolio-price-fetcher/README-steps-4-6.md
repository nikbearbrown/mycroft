# Portfolio Price Fetcher: steps 4 and 6 (quality check and human report), sample mode

Adds the two scripts the recipe names for step 4 (`scripts/gigo/portfolio-price-fetcher-transform-quality-check.py`) and step 6
(`scripts/tools/portfolio-price-fetcher-produce-human-report.py`), with their fixtures, outputs and a self-test. Python 3.9+
standard library only; no network, no keys. Run every command from the repository root. **Nothing that was already in the
repository was edited:** the recipe, the earlier scripts, `README.md` here, `logs/RUN_LOG.md` and every earlier output are
byte-identical; this change is new files only.

## Run it

```bash
python3 scripts/gigo/portfolio-price-fetcher-validate-data-shape.py --fixture-set quality-duplicate   # step 3 first, per set
python3 scripts/gigo/portfolio-price-fetcher-transform-quality-check.py                               # step 4 (clean set)
python3 scripts/gigo/portfolio-price-fetcher-transform-quality-check.py --fixture-set quality-duplicate   # exits 1 by design
python3 scripts/tools/portfolio-price-fetcher-produce-human-report.py --now 2026-11-17T12:00:00+00:00    # step 6 (clean set)
python3 scripts/tools/portfolio-price-fetcher-quality-report-self-test.py                              # every check, recorded
```

## What step 4 adds to steps 3 and 5

Step 3 judges each response file on its own, and step 5 prices whatever step 3 promoted. Step 4 looks across the set:

| Check | Result | Notes |
|---|---|---|
| Two records for one ticker | identical: collapsed; conflicting: **both** rejected (exit 1) | nothing in the files says which price is right, so a person decides |
| A holding with no price | `HOLDING_MISSING` (high), with the cost basis the summary would leave out | |
| Price taken from `previousClose` | `PRICE_FELL_BACK` (medium) | the original workflow's `\|\|` fallback, now visible as a flag |
| Price more than 15% from the previous close | `DAY_MOVE_LARGE` (medium) | |
| Price over 3x or under one third of the buy price | `FAR_FROM_BUY_PRICE` (medium) | |

The three numeric lines are **ours, a judgment**, written into every output. A flag asks a person to look; it is not a verdict.
On the sample, step 5 prices a duplicated ticker with one of the two responses and says nothing (self-test section E); step 4 is where the pair is seen.

## What step 6 writes

`reports/generated/portfolio-price-fetcher-<date>[-<set>].md` (the recipe's fifteen sections in order, reader and decision enabled)
and `logs/portfolio-price-fetcher-<date>[-<set>].json` (the contract's sixteen fields). It judges the four stop conditions from
evidence, reports the six gates as what the files show (none is cleared; a named person clears a gate), cross-checks step 4
against step 3 and step 5's totals against its own stocks, and refuses (exit 2, nothing written) on a live-call envelope, an
approval record, a missing or inconsistent input. Its recommendation only ever approves a sample-mode next phase.

## The sample corpus added

`data/raw/portfolio-price-fetcher/sample/` gains four sets next to `clean/` and `defective/`, frozen in their own
`quality-manifest.json` (the existing `manifest.json` is untouched): `quality-duplicate` (two valid NVDA responses that disagree),
`quality-missing` (no AMD), `quality-move` (AMD 40% under its previous close), `quality-far` (META at 3.44x its buy price).
**Every price is invented** and says so in its file. Outputs for each set sit under `data/verified/portfolio-price-fetcher/<set>/`.

## Seams left for the maintainers

- **Recipe text:** the recipe still marks steps 2, 4 and 6 `[TODO: DEV]` and `todos_open: 3`, because the recipe was not edited.
  The step 6 report lists them as typed TODOs and says so. Closing steps 4 and 6 and updating the status fields is a small
  follow-up edit to that one file.
- **`snickerdoodle check` lists 10 `built-not-documented` flags** for the two new scripts (the recipe's step table lists only
  `--sample` and `--no-write`). Rows to add to the recipe's step-command table when it is next edited:
  step 4 `--sample` `--fixture-set` `--verified-dir` `--workflow`; step 6 `--sample` `--no-write` `--fixture-set` `--now` `--repo`
  `--verified-dir` `--raw-dir` `--log-dir` `--report-dir`. The step 2 script (ingest) does not exist yet, as before.
- **Step 5 still reads step 3's output**, not step 4's; step 6 cross-checks the two.
- **Not covered:** step 2, any live call (there is no approval record), the dashboard recipe, and whether the three quality lines suit a real portfolio.
