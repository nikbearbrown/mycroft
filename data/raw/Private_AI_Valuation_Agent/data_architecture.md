# Data architecture

Fifteen project tables plus four LangGraph checkpoint tables. What each holds, what may edit
it, and — the part that matters — how any published number is traced back to the filing that
produced it.

## The two-layer contract

Nothing enters the resolved layer without passing validation, and tools read only the resolved
layer. The raw layer is the SEC's bytes, rearranged but never corrected.

```
  SEC bytes  ─►  raw / filed layer  ─►  judgment layer  ─►  resolved layer  ─►  published
  (zips)         immutable              append-only          rebuildable        regenerated
```

**A matcher bug is always recoverable.** Resolution writes to `match_decisions`, never into
`raw_holdings`. Drop `securities` and `marks`, re-run the build, and the panel comes back from
the raw layer and the recorded judgments — with no re-download and no lost human decision.

## Inventory

### Raw / filed layer — immutable

| Table | Rows | Cols | Holds |
|---|---|---|---|
| `funds` | 183 | 7 | one row per (CIK, series); 30 fund families |
| `filings` | 1,512 | 8 | one row per accession, with period end and net assets |
| `raw_holdings` | 5,806 | 21 | one disclosed private position per row, Level 3, universe-matched |
| `form_d_filings` | 706 | 32 | Form D issuer rows whose name matches a universe pattern — a **candidate pool**, not a join |
| `public_observations` | 10,566 | 17 | universe-company holdings at any fair-value level *other* than 3 |
| `restricted_lots` | 249 | 21 | Reg S-X 12-12 footnote lots: acquisition date, cost where filed |
| `ncsr_filings` | 60 | 13 | what was fetched and what came back, so "found nothing" ≠ "never looked" |
| `runs` | 2 | 12 | one row per ingest; `complete = false` excludes a period from re-mark baselines |

Two deliberate separations in this layer:

- **`public_observations` is not a widened `raw_holdings`.** Loosening `PRIVATE_FILTER` in
  place would have silently redefined the re-mark rate, the dispersion and the panel, because
  5,806 rows reconcile against `raw_holdings` as a Level 3 layer. Nothing downstream reads it.
- **`restricted_lots` is a *parse*, not a copy.** Its unique key contains parsed fields, so
  improving the parser changes the key. Re-ingest therefore **deletes and rewrites a filing's
  lots as a unit** — three runs once left 715 rows where 252 were parsed. The filing is
  immutable; its parse is not.

### Judgment layer — append-only, every row carries a name

| Table | Rows | Cols | Holds |
|---|---|---|---|
| `companies` | 11 | 6 | the canonical layer, seeded from frozen `universe_v1.json` |
| `review_decisions` | 45 | 12 | **one row per ambiguity**, not per holding; `reviewer` is a name — "auto" is not |
| `match_decisions` | 5,806 | 13 | **one row per resolved holding** — the per-holding audit trail |
| `company_identity` | 46 | 8 | which EDGAR CIK *is* a company; the only thing Form D joins on |

`review_decisions` and `match_decisions` look redundant and are not. The plan asked for both
`unique (raw_id)` *and* "keyed so the same ambiguity is never presented twice", which cannot
both hold in one table: 5,806 holdings are only 231 distinct (issuer, title) pairs, so a queue
keyed by `raw_id` would ask the Databricks question 85 times. One human answer fans out to
every holding sharing its key.

How the 5,806 were resolved:

| Method | Count |
|---|---|
| `alias` | 2,760 |
| `lei` | 1,681 |
| `human` | 1,269 |
| `fuzzy` | 57 |
| `spv` | 39 |

### Resolved layer — rebuildable

| Table | Rows | Cols | Holds |
|---|---|---|---|
| `securities` | 232 | 12 | company × share class, with price basis and SPV flags |
| `security_map` | 235 | 4 | how a filed line finds its security, carrying asset category |
| `marks` | 5,479 | 32 | one row per (security, fund, period end) — the panel |

`marks` carries six columns the plan did not specify and the data forced, each logged as a
deviation:

- `asset_category` — part of the line-group identity. SpaceX common and preferred arrive under
  the *same* issuer name and title, ten times apart; EC/EP is the only thing separating them.
- `lines` — how many filed lots were summed. A fund reporting one security across several lots
  is normal and must be summed, not deduplicated.
- `is_blended` + `price_min`/`price_max` — the lots disagreed beyond rounding, so **no price is
  published**; a price spanning two classes belongs to neither. The exception stays auditable
  rather than merely suppressed.
- `currency` — all 5,806 are USD. Recorded so the guard is visible rather than assumed.
- `change_blocked` — the quarantine, stated rather than implied by two other columns.

`security_map` exists because three Databricks titles say "Series F" and are filed as `EC` by
some managers and `EP` by others: one security, two category tags. Keying `securities` on the
category would split it in two; ignoring the category would merge SpaceX common with SpaceX
preferred. Identity stays on (company, title, class); the category lives in the lookup.

## Provenance: tracing one number

Take the headline *"25.0% of consecutive observations are unchanged."*

```
docs/findings.md  §1
  └─ docs/_findings.json              generated artifact, the figure as computed
      └─ src/signal/findings.py       remark_frequency(), with the guards applied
          └─ marks                    WHERE NOT change_blocked AND price_per_share IS NOT NULL
              └─ match_decisions      which company each holding resolved to, and by what method
                  └─ review_decisions a named human, where method = 'human'
                      └─ raw_holdings the filed position: balance, value_usd
                          └─ filings  accession, period end
                              └─ data/<qtr>_nport.zip   the SEC's bytes
```

Break any link and you have an output, not evidence. `logs/RUN_LOG.md` records the run that
produced each artifact, so the chain is datable as well as traceable.

## The guards, and what they cost

Every published figure sits behind these. They are reported, never silently applied:

| Guard | Count | Effect |
|---|---|---|
| unpriced marks | 294 | no balance, or zero — a missing share count is not a zero price |
| `change_blocked` | 301 | the step crosses an unadjudicated split |
| confirmed splits | 7 | adjudicated by a named human; the factor is recorded, not applied |
| unadjudicated splits | 0 | none outstanding |
| incomplete runs | 0 | a partial period never serves as a re-mark baseline |
| unresolved reviews | 0 | every ambiguity has a recorded answer |

5,479 marks, of which 5,178 are published.

## Null rules, stated once

- **`price_per_share` is stored, not derived on read.** The arithmetic happens once, at ingest,
  under one rule: `NULL` where balance is zero or absent.
- **A missing share count is not a zero price.** The row is retained, counted, and excluded.
- **`company_provisional` is a label, not a decision.** It comes from the frozen patterns in
  `src/ingest/universe.py`; `match_decisions` supersedes it.
- **`period_end` is DERA's `REPORT_DATE`**, the as-of date of the holdings — *not*
  `REPORT_ENDING_PERIOD`, which is the fund's fiscal year end. Verified on 2026Q2: BlackRock
  files with a fiscal year end of 31-MAY-2026 carrying holdings as of 27-FEB-2026. Using the
  wrong one would scramble every propagation-lag measurement.

## Volume, and why Parquet

~442 MB compressed per quarter, ~4 GB uncompressed, 10–15M holding rows. Fourteen quarters.
The full private layer measures ~694,000 rows a quarter — 9.7M over the archive, past what a
free-tier Postgres holds — so it lives in `data/parquet/<qtr>/private_holdings.parquet`,
queryable with DuckDB and re-runnable, while Postgres carries the universe-matched subset
(~1,000/quarter) that resolution and marks consume. The append-only invariant applies to both.

An earlier draft of the plan chose pandas in memory. The measured file sizes overturned it.

## Coverage, and the hole that cannot be measured

Three SPV patterns, one of them permanent:

- **Transparent** (ARK): `U First Capital Fund III LLC (SpaceX)` — underlying named in
  parentheses. Parseable.
- **Hybrid** (T. Rowe): `AESTAS LLC dba OPENAI LLC EV UNITS Class A` — the SPV is the linked
  entity.
- **Opaque** (Fidelity): `FSOIFD TC HOLDINGS LLC` — no LEI, no CUSIP, underlying undisclosed.
  **These cannot be seen through.** 27 such positions are counted and reported rather than
  pretended away; the size of what they hide is not knowable from filings.
