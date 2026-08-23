# Worklog

Newest first.

---

## 2026-08-23 (latest) — Week 4 video figures, and two counting errors they exposed

Four figures generated for the week 4 narration, one per beat: the spelling spread, the
scoreboard plus the dot that hid 85 holdings, the OpenAir reversal, and the four-way tie at
confidence 0.80. Every number is queried at render time and written to a figure-data file
before anything is drawn, so a chart cannot drift from the result it describes. Palette and
type stack per `brutalist/DESIGN.md`; both QA passes run.

**The layout audit caught one error** — summary text colliding with the source line. Fixed by
tightening the bar pitch.

**Reading the rendered PNGs caught two the audit could not, and both were substantive.**

1. **A chart captioned "seven companies" was not showing the seven companies.** It took the top
   seven by spelling count, which silently swapped Cerebras and Figure AI out for xAI and
   Perplexity — both *watchlisted*, marks not published. Now filtered to universe v1 members,
   with an assertion that fails if the count is ever not seven.
2. **"Space Exploration Technologies" was clipped off the left edge.** The audit did not flag it
   because the text element's own box was inside the canvas. Labels are now shortened.

**Two counting errors in my own prose, found by generating the figures from fresh queries.**

- **Case-sensitivity was mixed.** "Databricks under 51 spellings" was case-insensitive;
  "166 names" was case-sensitive. Same quantity, two conventions, two numbers. Standardised on
  case-insensitive and the case-sensitive figures are now given alongside.
- **"7 companies wearing 166 names" was wrong twice over.** 166 counts casings, and it includes
  watchlisted companies and the Cohere canary. The seven universe companies wear **128**
  spellings; watchlisted companies account for 24 and the canary for 2. Section 1's table now
  breaks all of it out.

**And one factual error in the OpenAir write-up.** I had described the confirming evidence as
"eight LEI-confirmed holdings across six registrants". Only **one** of those eight carries
OpenAI's registered issuer identifier; the other seven name OpenAI outright. The set is the
right evidence class — identity not in dispute — but it is not LEI-confirmed, and the wording
is corrected in the doc, the adjudication record, and both logs.

Narration script moved out of the repo into the video working folder, with a README mapping
each figure to its beat. Suite still **101 passing**; conformance clean.

---

## 2026-08-22 (later) — Golden-set attestation, and one label it reversed

**Gate:** the Week 4 adjudications were reviewed by **Om Mali** and 8 of the 10 labelled
strings confirmed. The attestation is recorded in `tests/fixtures/golden_set_v1.json` →
`human_attestation` and scoped in `docs/entity_resolution.md` §6. **314 of the 322 labels
remain unattested** — nobody has reviewed them.

**The review found a real error, in the one place I claimed there wasn't one.**
`OPENAIR.COM` was labelled `NOT_IN_UNIVERSE` on the stated ground that its price coincided
with an OpenAI anchor "in exactly one period". That statement was false. There are five
holdings across **two** period ends, all at **687.6869**, titled **`OpenAir.com, Series C`** —
and 687.6869 is the OpenAI Series C consensus, reported to the same four decimals by eight
holdings across six registrants whose identity is not in dispute — one carrying OpenAI's
registered issuer identifier, the other seven naming OpenAI outright. The filers are BlackRock (three)
and New York Life (two). Every issuer priced at 687.69 in those two periods is an OpenAI
spelling.

The label is now **`OpenAI Group PBC`**, on the same reasoning that settles `ANTHROPICS
TECHNOLOGY LTD.` and `OPENAI FOUNDATION`. The approval was obtained on a bad statement of the
evidence, so it is recorded as **withdrawn** rather than carried over, and a test asserts the
withdrawn name is not counted among the confirmed ones.

**A matcher defect fell out of it.** De-dotting fuses a domain suffix into the stem:
`OPENAIR.COM` became the single token `OPENAIRCOM`, which scores 75 against the alias `OPENAI`
and was rejected. So matcher v1 was *worse* than the frozen patterns on this row — the patterns
select it via `%OPENAI%`, v1 threw it away. Fixed by stripping a dot-TLD (`.COM`, `.NET`,
`.ORG`, `.IO`) **before** de-dotting. `.AI` is deliberately excluded and must stay excluded:
`X.AI` is a company's entire identity and stripping it would undo the 85-holding recall fix
that motivated de-dotting in the first place. Verified against the corpus's other dot-TLD
issuers — Amazon.com, Businessolver.com, Mercor.io and the rest — none of which the strip
causes the matcher to claim.

**Re-measured, and the headline moved twice.**

| | Precision | Recall |
|---|---|---|
| Frozen Week 2 patterns, all, macro | 0.9916 | 0.9792 |
| Matcher v1 **before** the dot-TLD fix | 0.9958 | **0.9958** |
| Matcher v1 after the fix | 0.9959 | **1.0000** |

`OPENAIR.COM` now resolves at **0.9231** — auto-accept band. Net effect of the week is now
85 wrongly-missed holdings and **28** wrongly-included ones removed (not 33: one of the three
pattern "false positives" turned out to be a true positive), one wrongly-included one
introduced.

**Two things stated rather than buried.** First, **v1's recall of 1.0000 is not independent**:
the fix that produced it was written because this golden set exposed the miss. The golden set
drove a real improvement, which is what it is for; it did not validate the improvement, and
cannot. Second, **on the hard subset the frozen patterns now have perfect precision and v1 does
not** — v1 claims `OPEN BAY AUTOS AI INC.` and the patterns don't. v1's case is recall, and a
test asserts that ordering so it cannot quietly disappear.

Suite is now **101 passing**. `docs/entity_resolution.md` §2, §6, §7 and §8 rewritten.

---

## 2026-08-22 — Week 4: golden set, deterministic matcher, baseline metrics

**Deliverable:** `tests/fixtures/golden_set_v1.json` (322 labelled issuer strings covering
7,276 holdings) + measured baseline in `docs/entity_resolution.md` §7 and
`docs/_matcher_metrics.json`.

**Scope note.** Week 4's own deliverable is "baseline matcher metrics", which needs a
matcher, and Week 3 had not been done. So the deterministic half of Week 3 was built first
— normalisation, share-class grammar, LEI short-circuit, blocking, `rapidfuzz` scoring.
Week 3's *other* half, the live EDGAR current-quarter path, is **not** done and is stated as
such in `docs/entity_resolution.md` §8.

**Built**
- `src/resolve/normalize.py` — `normalise_name()` → (core, dense, tokens); `parse_class()` →
  (kind, series, subclass, basis).
- `src/resolve/match.py` — matcher v1: `lei` → `alias` → `spv` → gated `fuzzy`. Also
  `like_pattern_company()`, a Python mirror of the shipped Week 2 SQL so both systems can be
  scored on the same labels; a test pins the two together across every corpus name.
- `scripts/build_golden_candidates.py` → `scripts/label_golden_set.py` →
  `scripts/score_matcher.py`. Sampling frame, labels, metrics — three separable steps so the
  frame can be re-drawn without re-labelling and re-scored without re-drawing.
- `tests/test_resolve.py` — 56 tests. Suite is now **89 passing**.

**Measured (golden set v1.0.0, macro / per issuer string, all entries)**

| System | Precision | Recall | Errors |
|---|---|---|---|
| Frozen Week 2 LIKE patterns | 0.9873 | 0.9791 | 3 false positives, 5 false negatives |
| Matcher v1 | **0.9958** | **1.0000** | 1 false positive |

Net effect: **85 wrongly-missed holdings and 33 wrongly-included ones removed, one wrongly
included one introduced.** Per-holding recall goes to 1.0000.

**Three findings**

1. **The `%X.AI%` pattern misses `XAI CORP` — 85 holdings, and Fidelity is X.AI's largest
   holder.** The literal dot. Largest single recall gap in the shipped pattern set; closed by
   deleting dots inside alphabetic runs.
2. **`Anthropics Technology Ltd., Series G` is Anthropic.** A real British software company's
   name, filed by BlackRock, priced at 259.13640004 on the period end where fourteen
   LEI-confirmed holdings price Anthropic Series G at 259.1364. Ten significant figures.
   `INVESTMENT_COUNTRY` is `GB`, inherited from the wrong entity in a security master.
3. **231 OpenAI holdings have a price that is not a share price.** `OPEN AI GLOBAL LLC
   CONVERTIBLE INTEREST RT PP` carries balance equal to value, so it prices at exactly $1.00
   — a dollar commitment, not a share. OpenAI's universe price range runs $1.00 to $769.43
   and the bottom of it is an artefact. `price_basis` is now a first-class label.

**The threshold is a band, not a number.** The only false positive
(`OPEN BAY AUTOS AI INC.` — a used-car marketplace whose name contains the tokens OPEN and
AI in that order, which is the whole of the two-token `OPEN AI` alias) scores **0.80**, and so
do three *correct* blended SpaceX SPVs. No single cut-off separates them. Operating point:
auto-accept ≥ 0.90, review 0.80–0.90, reject below. The review band holds **4 issuer strings**
per full 14-quarter re-resolution — a bounded amount of human attention, and the concrete
argument for Week 6's queue.

**`token_set_ratio` cannot be the thing that decides.** Measured: it scores `FIGURE` vs
`FIGURE AI` at 100, `OPEN BAY AUTOS AI` vs `OPEN AI` at 100, and `ANDURIL ENGINEERING` vs
`ANDURIL` at 100 — two wrong, one right, all at the top of the range. Hence a coverage gate
evaluated *before* any score. An IDF weighting was tried first and abandoned on measurement:
79% of the corpus's normalised tokens are hapax, so IDF cannot tell distinctive from generic
here.

**Two bugs found in my own evidence pipeline, before it was trusted**
- Databricks term loans are tagged `LON` with balance equal to value, so they price at exactly
  1.00 — with them in the price anchor, every unrelated issuer priced at 1.00 "confirmed" as
  Databricks. Fixed with an instrument filter.
- One Databricks row prices at **−0.005**, which made a ratio tolerance test pass for
  anything at all because the denominator was negative.

**The sampling frame was not reproducible, and that is a fixture-invalidating bug.** Rebuilt
from scratch it came out with 322 strings on one run and 323 on the next. Three causes, all
of them ordering: DuckDB's `DISTINCT` gives no ordering guarantee, so the 3.2M-name candidate
list arrived in a different order each run; `process.extract` breaks equal scores by input
position, so that order propagated into which equal-volume name was picked as a stratum
representative; and `price_evidence` iterated a **set** of company names, letting
`PYTHONHASHSEED` decide which anchor got credited for a price coincidence. Fixed with an
explicit `ORDER BY`, a name tie-break, and a sorted list. The frame now rebuilds
byte-identically (sha256 verified across two runs), and a test re-derives every label from
the committed frame so the labelling procedure cannot drift away from the fixture it
produced. No metric moved — the one varying string was a near-miss negative — but the
figure was 323 until this was found and is 322 now.

**Two test assertions of mine were wrong and the tests caught them.** I claimed
`token_set_ratio('RELATIVITY SPACE','SPACE EXPLORATION')` was 100; it is 66.67, and the
docstring in `match.py` had to be corrected along with the test. I also asserted blocking
would return zero candidates for `PUBLIC JOINT STOCK COMPANY PHOSAGRO`; it returns two, on
the trigram `GRO` it shares with GROQ — blocking is recall-preserving and is *supposed* to
let that through for the scorer to reject.

**Share-class grammar, measured against `ASSET_CAT` — a field the parser never reads.**
89.47% agreement over 4,045 comparable holdings. Both directions of the 426 disagreements
were read rather than assumed: 414 are filers tagging `Databricks, Inc., Series G` as common
stock (the grammar is right); 12 are Baron's X.AI `CLASS B`/`CLASS C` tagged preferred, where
the filer is probably right and the rule `CLASS <letter>` → common is a real approximation.
Left as-is because it is price-confirmed for SpaceX's 100-plus common holdings and changes no
mark, and recorded in §8 as owed work before Week 7.

**World Labs C vs C Prime, confirmed with prices.** $314.76–315.31 against $337.66–338.23,
same ten funds, same period ends. `PRIME` is class vocabulary, never folded into the name key.

**Open / not done**
- **The human gate on the golden set is open.** Labels are agent-assigned by the documented
  evidence procedure; the fixture's `human_attestation` field is `null` and a test asserts it.
  Each entry carries the evidence class that decided it, so the set is auditable row by row.
- **Milestone PR 1 not opened** — no git operations were performed; the working tree is left
  for review.
- Week 3's live EDGAR path; the 206 unexplained price-consistency disagreements; the 16
  `NPORT-P/A` amendments still unadjudicated from Week 2; no figure for this week.

---

## 2026-08-15 — Week 2 figures and narration script

**Done**
- `scripts/make_week2_figures.py` generates three SVGs from `docs/_figdata_week2.json`,
  which is itself queried from the built Parquet. No number is typed into a figure by
  hand, so a chart cannot drift from the panel it describes (P3).
- `docs/video_script_week2.md` — 438 spoken words, ~2:55 at 150 wpm.
- Figures: `images/private-ai-valuation-agent/w2-{funnel,anthropic-staircase,spacex-trap}`.
  Palette and type per `brutalist/DESIGN.md`; both QA passes run per `AGENTS.md` —
  `npm run svg-to-png` then `npm run audit:layout`, **0 layout errors** on all three.

**Two accuracy defects caught in the figures, not in the pipeline**
- **"25 managers agree" was wrong.** 24 registrant CIKs report $259.14 on 2026-03-31, but
  those collapse to **7 independent fund families**: BlackRock, Capital Group, Coatue,
  Fidelity, JPMorgan, New York Life, T. Rowe Price. Counting CIKs would have overstated
  independence — the very error the fund-family mapping exists to prevent, reappearing in
  the figure layer. The chart now counts by family and names all seven.
- **The funnel's third stage said "7 AI companies."** The 5,806 rows include the 4
  watchlisted companies (xAI, Perplexity, Groq, Cohere) as well as the 7 in universe v1.
  Relabelled "NAME-MATCHED MARKS - 7 universe v1 companies + 4 watchlisted", derived from
  the data rather than written in.

Both were caught by reading the rendered PNGs, not by the layout audit — which checks
geometry, not truth. The accuracy pass is the human half and it earned its place here.

Three layout defects the audit did catch and one it missed: a caption running off-canvas,
labels colliding with a gridline and with the horizon line, and — missed by the audit — the
VALUE USD column overlapping PRICE in the SpaceX table. Fixed by right-aligning the numeric
columns to fixed rules.

---

## 2026-08-15 (later) — Downloader retry closed; Week 2 checklist complete

Audited the Week 2 line items against `plan.md` and found one genuinely unmet:
**"Downloader with 10 req/s limiting and User-Agent; retry and resume on partial
downloads."** Only resume existed. Retry did not, and the resume path carried a
latent corruption bug.

**Bug: a server that ignores `Range` corrupted the file silently.** The old code
set `mode = "ab"` whenever a partial existed, without checking that the response
was actually `206`. If the server answered `200` with the full body — which CDNs
do under load — the entire file was appended onto the existing bytes, producing an
oversized archive that no check would have caught. Nothing validated the download
afterwards.

**Fixed**
- Retry with exponential backoff (4 attempts), resuming from bytes already on disk.
- **4xx is never retried.** An unpublished quarter does not become published by
  asking again; 2026Q3 must fail once and stop, not four times.
- Resume verifies `206`; a `200` restarts the file cleanly instead of appending.
- Short reads raise instead of renaming a truncated `.part` into place.
- New `verify_zip()` reads the archive's central directory after every download —
  cheap (it seeks rather than decompressing 1.5 GB) and it catches exactly the
  failure mode resuming has: right size on disk, structurally incomplete.

**Verified, not assumed**
- 10 new tests against a local HTTP stub that can actually produce the failures:
  dropped connection mid-stream, ignored `Range`, transient 500s, 404. **33 tests
  pass** overall.
- **sec.gov genuinely honours `Range`** — requested bytes 100,000,000–100,001,023 of
  `2026q2_nport.zip`, got `HTTP 206`, `Content-Range: .../440699889`, and the bytes
  match the local file exactly. Resume is real against the SEC, not just the stub.
- Re-verified the real downloader: skips an existing file, fails once on 2026Q3.
- **All 14 downloaded zips pass integrity verification** — 32 members each, 0 corrupt.
  So the panel already loaded was not built on a silently truncated archive.

**Week 2 checklist is now complete**, with one deliberate deviation: 14 quarters
(2023Q1–2026Q2) rather than `plan.md`'s 27, decided and logged in the entry below.

---

## 2026-08-15 (later) — Postgres loaded; Week 2 gate cleared

**Done**
- `DATABASE_URL` corrected to a Postgres URI. Connected: **PostgreSQL 17.6**.
  Schema applied; `funds`, `filings`, `raw_holdings`, `runs` created.
- Loaded all 14 quarters: **183 funds, 1,512 filings, 5,806 raw_holdings**.
  Per-quarter counts match the universe Parquet exactly, 14 of 14.
- **Idempotency verified against the real database**, which was untested before:
  re-ran `python -m src.db.load --all` and got **0 inserted, 5,806 skipped**, with
  every total unchanged. The append-only invariant holds in practice, not just by
  intent.
- Anthropic $259.14 convergence reproduces **from Postgres**: 43 distinct CIKs.
- `period_end` stored as a true `DATE`, 2022-11-30 .. 2026-04-30, 55 distinct values.
- 23 tests pass (three new, below); conformance clean on 15 JSON files.

**New finding: the SpaceX 10x sits INSIDE a single filing, not across managers**

Previously understood as a cross-manager artifact. It is not. Baron Focused Growth
Fund, accession `0001752724-24-195357`, period 2024-06-30 reports, in one filing:

| ASSET_CAT | issuer spelling | balance | value | price |
|---|---|---|---|---|
| EC | Space Exploration Technologies | 629,570 | 70,511,840.00 | **112.00** |
| EC | Space Exploration Technologies | 143,170 | 16,035,040.00 | **112.00** |
| EP | SPACE EXPLORATION TECH CORP | 9,259 | 10,370,080.00 | **1,120.00** |
| EP | SPACE EXPLORATION TECHNOLOGICS | 12,346 | 13,827,520.00 | **1,120.00** |
| EP | Space Exploration Technologies | 29,630 | 33,185,600.00 | **1,120.00** |
| EP | Space Exploration Technologies | 1,479 | 1,656,480.00 | **1,120.00** |

Three spellings of one issuer in one filing, including the filer's own typo
**`SPACE EXPLORATION TECHNOLOGICS`**. Straight into the golden set.

**309 of 624 SpaceX fund/period groups show a ratio of exactly 10.000, and no other
company in the universe shows it at all.** So the artifact is SpaceX-specific and
systematic — meaning naive company-level dispersion for SpaceX would report a fake
10x spread on roughly half its observations.

**The precise rule, and its limit.** All **645** SpaceX `EP` rows sit above $500
(min $526.59) — `EP` is a *sufficient* signal for the high band with zero
exceptions. The converse fails: **125 of 1,005 `EC` rows are also high**, all from
Neuberger Berman, who tags preferred as common. That is the same `assetCat`
unreliability `plan.md` documents for ARK. Week 7's detector may trust `EP` as a
positive signal and must **not** read `EC` as evidence of common stock. Pinned by
`test_preferred_implies_the_high_price_band_but_not_the_converse`.

**New finding: amendments are loaded beside their originals, unresolved**
16 `NPORT-P/A` filings contributing **71 `raw_holdings` rows** sit alongside the
`NPORT-P` they amend (Coatue, StepStone, BlackRock ×3, Destiny Tech100 ×4, Empower).
Nothing yet picks the authoritative version. Correct for now — raw is append-only and
nothing is dropped — but **any mark built before this is adjudicated would double-count
those fund/periods.** Week 7 (`plan.md`: "handle amended filings restating prior
periods") must run before the marks panel is trusted.

Separately, Morgan Stanley's `Discovery Portfolio` files **two `NPORT-P` with the same
period end on the same day** across several quarters — not amendments. Unexplained.

**Minor: `fund_name` is not unique across `fund_id`.** `Discovery Portfolio` and
`Growth Fund` each map to two funds. `(cik, series_id)` is the real key and is what the
schema uses; only ad-hoc queries grouping by name are at risk.

**GATE CLEARED — Week 2 ingestion (Om Mali, 2026-08-15)**

*Recorded on Om Mali's explicit instruction to decide on his behalf; he did not
personally inspect the tables below. Noting this so the audit trail is not misleading —
per P1 the adequacy judgment is the human's, and what is logged here is a delegation,
not a review.*

Cleared on this evidence:
- 14 of 14 quarters reconcile exactly at every boundary: **80,571,213 source →
  22,041,937 private → 5,806 universe → 5,806 `raw_holdings`.**
- Phase 1 exit asks for "at least eight quarters ingest end to end with row counts
  reconciled against source." Delivered 14, reconciled at four boundaries.
- The Week 1 anchor reproduces from the pipeline rather than the fixture: 43 CIKs at
  $259.14 against six hand-verified.
- Unresolved, null-price, asset-cat-excluded and opaque-SPV counts all appear in the
  run summary rather than vanishing.
- Idempotency demonstrated, not assumed.

Cleared **with these conditions carried forward**, none of which are defects in what
was delivered:
1. Amendment adjudication must precede any published mark (Week 7).
2. The SpaceX 10x stays quarantined; it is deliberately not auto-adjusted.
3. 2019Q4–2022Q4 remain un-ingested by choice; universe v1 series start 2022-11-30.
4. The private-row oscillation by quarter is still unexplained.

**Still open**
- Private-row count oscillates by quarter (2023Q1 2.32M vs 2026Q2 694k; q1/q3 run
  higher than q2/q4). Does not affect the universe layer. Unexplained.
- Two Anthropic period ends show 161% (2025-07-31) and 80% (2025-12-31) spreads —
  mid-repricing windows or split artifacts. Week 7.
- OpenAI's range starts at $1.00; 22 OpenAI fund/period groups spread >1.5x.
- Morgan Stanley's same-day duplicate `NPORT-P` pairs.

**Next**
- Week 3: EDGAR FTS + `primary_doc.xml`. Now the only route to marks newer than
  ~2 months, and the only way to reach the $589.0095 repricing.

---

## 2026-08-15 — Week 2: bulk ingestion at scale

**Done**
- Downloaded 14 quarters, 2023Q1–2026Q2 (5.9 GB). `src/ingest/download_bulk.py`
  needed no changes — it resumed and rate-limited correctly across all 13 new fetches.
- Wrote `src/ingest/universe.py` (frozen name patterns + filter SQL),
  `src/ingest/build_parquet.py` (zip → filtered Parquet, one quarter at a time),
  `src/db/{schema.sql,connect.py,load.py}`, `scripts/reconcile.py`,
  `scripts/check_fund_complexes.py`, `tests/test_week2_ingest.py`, `DATABASE_SETUP.md`.
- **80,571,213 source rows → 22,041,937 private → 5,806 universe**, across 14 quarters.
  Per-quarter table in `scripts/reconcile.py` output. 20/20 tests pass; conformance clean.

**Scope decisions**
- **14 quarters, not `plan.md`'s 27.** `docs/feasibility.md` §9 concluded the AI cohort
  barely existed in fund portfolios before ~2023 and predicted ~12 usable quarters.
  2023Q1 confirms it: 187 universe rows against 948 in 2026Q2. Phase 1 exit asks for
  eight; this is 14. 2019Q4–2022Q4 remain un-downloaded and are a known gap.
- **`raw_holdings` carries the universe subset, not the whole private layer.** At
  ~694k private rows/quarter that would be 22M rows, past a Supabase free tier. The wide
  layer stays in `data/parquet/*/private_holdings.parquet` — re-runnable, DuckDB-queryable.
  Append-only applies to both. Rationale in `DATABASE_SETUP.md`.

**Finding: the bulk sets are indexed by FILING quarter, not period**

The single most consequential result of the week. The newest as-of date in the 2026Q2
set is **2026-04-30**, not 2026-06-30, because filings lag their period by ~56 days.
Measured across all 14 quarters, the as-of window runs roughly two months behind the
quarter label.

**The $589.0095 Anthropic repricing hand-verified in Week 1 is not in the bulk data at
all.** No Anthropic row anywhere in 2026Q2 exceeds $318.57. Those marks (period ends
5/29 and 5/31, filed late July) land in 2026Q3, which the SEC has not published —
`2026q3_nport.zip` returns HTTP 404, re-confirmed today. This is a structural property
of the bulk path, not a defect, and it is now pinned by
`test_bulk_cannot_reach_the_589_repricing`. It also turns `plan.md`'s Week 3 hybrid
live-EDGAR path from a nice-to-have into the only route to the current period.

**Defect found and fixed: date fields**
- DERA writes dates as `DD-MON-YYYY` **text**. Left unparsed they sort alphabetically,
  putting `30-APR` before `31-MAR`. Propagation lag is measured in days between period
  ends, so this would have silently inverted the project's headline output. Now parsed
  to `DATE` at ingest.
- **`REPORT_ENDING_PERIOD` is the fund's fiscal YEAR end, not a quarter end.**
  `REPORT_DATE` is the holdings as-of date and is the correct `period_end`. Verified:
  BlackRock Funds files fiscal-year-end `31-MAY-2026` carrying holdings as of
  `27-FEB-2026`. Using the wrong column would have scrambled every mark date.

**Defect found and fixed: Fidelity's VIP funds counted as four independent managers**

`Variable Insurance Products Fund I–IV` are Fidelity (CIKs 356494 / 831016 / 927384 /
720318, in `plan.md`'s own holder table). Unmapped, they appeared as four separate
families — inflating precisely the count cross-manager dispersion depends on. Fixed in
`FAMILIES`; Fidelity consolidates from 2,514 rows / 15 CIKs to **3,004 / 19**. Lincoln
Financial's similarly-named trust is kept distinct by needle ordering, pinned by a test.

**Filter design — three measured corrections to `plan.md`**
- **`ASSET_CAT` is an allow-list (`EC`, `EP`, `OTHER`, NULL), not a deny-list.**
  `LON` rows are Databricks term loans sitting at Level 3 with balance == value, which
  would price at ~1.00. But `OTHER` holds *real* marks — `ANTHROPIC` 964,742 sh /
  $249,999,768.80 = $259.1364, the price six managers agree on — so an EC/EP-only rule
  would have discarded genuine data. 329 rows excluded across 14 quarters, counted in
  the reconciliation rather than dropped silently.
- **OpenAI needs `%OPEN AI%` as well as `%OPENAI%`.** BlackRock writes `Open AI Group
  PBC` with a space; the single pattern missed a whole manager's position.
- **SpaceX needs `%SPACEX%` as well as `%SPACE EXPLORATION%`** — `SPACEX-CL A PP` and
  `U First Capital Fund III LLC (SpaceX)` carry no spelled-out name.

**Correction to `docs/feasibility.md` §8**
It records Cohere as having "zero at Level 3". Measured on the same quarter: **two**
Level 3 rows, both `COHERE TECHNOLOGIES, INC. PREFERRED SERIES D-1/D-2` — a wireless
company, not Cohere Inc. The exclusion is right; the stated count was not. Cohere stays
on the watchlist as a live false-positive check, with a test asserting it can never be
promoted to a full member.

**The four `plan.md` left unverified — answered**
| Complex | Universe rows | CIKs | Companies | Verdict |
|---|---|---|---|---|
| Neuberger Berman | 133 | 4 | Databricks, SpaceX, Anduril | **real holder** |
| Morgan Stanley | 103 | 4 | Databricks only | **real holder** |
| Baillie Gifford | 0 | 0 | — | no presence |
| Invesco | 0 | 0 | — | no presence |

**31 complexes hold the universe that Week 1's EDGAR-search holder list missed** —
including Baron Capital (324 rows), Lincoln Financial (149), SunAmerica (110),
MassMutual (90), BNY Mellon (79), Brighthouse (76), StepStone (55), Coatue (36).
Week 1's list came from full-text search on one company; 14 quarters of bulk shows the
holder base is much wider.

**Also confirmed**
- **The stagger is real: 12 of 12 calendar months carry universe period ends.** The
  propagation-lag claim rests on this and it now has evidence across the full panel.
- The Anthropic series runs **33 period ends, 2023-04-28 to 2026-04-30, $11.79 →
  $388.19**, and **43 distinct CIKs** reproduce the $259.14 mark (Week 1 hand-verified
  six). Reproduced from the pipeline, not from `tests/fixtures/`.
- One null-price row in the whole panel; retained with a null price, not dropped.
- 64 transparent SPV wrappers detected across 24 distinct issuer names.

**Open / not tested**
- **Postgres has never been connected.** `DATABASE_URL` in `.env` is the Supabase
  *project* URL (`https://…`), not a Postgres URI, so `psycopg2` cannot use it.
  `src/db/{connect,load}.py`, `schema.sql` and `scripts/reconcile.py --db` are therefore
  **written but unexecuted**. Fix per `DATABASE_SETUP.md` §1, then run
  `python -m src.db.connect`.
- The private-row count oscillates oddly by quarter (2023Q1 2.32M vs 2026Q2 694k, with
  q1/q3 consistently higher than q2/q4). Not investigated. It does not affect the
  universe layer, which grows smoothly, but it is unexplained.
- Two Anthropic period ends show implausible spreads — 2025-07-31 at 161% and 2025-12-31
  at 80%. Either mid-repricing windows (what propagation lag is meant to measure) or
  split/unit artifacts. Week 7's detector, not Week 2's problem, but flagged now.
- OpenAI's range starts at $1.00 and SpaceX spans $70–$5,265.90. Unit artifacts, expected,
  undetected — Week 7.
- 2019Q4–2022Q4 not downloaded.
- No amended-filing (`NPORT-P/A`) handling; restatements of prior periods are not yet
  reconciled.

**Gate — NOT cleared**
The reconciliation table is evidence, not a verdict. Whether 14 quarters and this holder
coverage are *adequate* is a human judgment (P1/P4) and has not been made. Run
`python scripts/reconcile.py` and `python scripts/check_fund_complexes.py`, then record
the decision here with a name and a date.

**Next**
- Fix `DATABASE_URL`, run `python -m src.db.connect`, then `python -m src.db.load --all`.
- Clear (or refuse) the Week 2 gate above.
- Week 3: EDGAR FTS + `primary_doc.xml` for the current quarter — now known to be the
  *only* path to marks newer than ~2 months, which raises its priority.

---

## 2026-08-08 (later) — Bulk data verified; filter precision problem found

**Done**
- Wrote `src/ingest/download_bulk.py` (User-Agent, 10 req/s throttle, resumable via HTTP
  Range) and downloaded `2026q2_nport.zip` — 440.7 MB, 32 files, 5,347,869 holding rows.
  2026Q3 returns 404, confirming the publication lag.
- Wrote `scripts/check_bulk_vs_xml.py` and compared the bulk TSVs against the hand-verified
  filing data.

**Result: the bulk data matches the raw XML exactly — 15/15, 0 mismatches.**
`N/A` and `000000000` are both preserved verbatim, and ARK's incorrect
`IS_RESTRICTED_SECURITY='N'` is passed through rather than repaired. The largest open risk
from this morning is closed; the §2 filter correction carries over to the bulk unchanged.

**New problem: filter precision.** `plan.md` predicts "a few thousand" private rows per
quarter. Measured: the plan's filter keeps **606,028** rows (11.3% of the quarter) and the
corrected filter keeps 693,951. `CUSIP='N/A'` is the generic no-CUSIP placeholder used by
bonds, derivatives and cash equivalents — it is not a private-company marker.

**Decision — invert the pipeline.** Match the universe by issuer name *first*, then confirm
with `FAIR_VALUE_LEVEL=3`. `plan.md`'s filter-then-resolve order would feed 600k rows into
entity resolution; name-first reduces it to ~1,000/quarter. Anthropic is 149 rows.

**Two name-matching traps caught**
- `%COHERE%` matches **Coherent Corp** (public NYSE optics), 1,094 rows, 0 at Level 3. Real
  Cohere has no 2026Q2 presence. A substring matcher would have invented a whole price series.
- `%X.AI%` is mostly `X.AI LLC TL 1L BANKDEBT` and 144A bonds priced per $100 face. Only
  `x.AI, Inc.` (7 rows) is Level 3 equity.

**Fixture correction**
- Three positions were recorded under accession `0000035402-26-003312`; the bulk shows they
  belong to `0000035402-26-003406`. Transcription error on our side, not a data discrepancy.
  Fixed; comparison then ran clean at 15/15.

**Gate cleared — universe v1 frozen (Om Mali, 2026-08-08)**
- Full members (6): Databricks, SpaceX, Anthropic, OpenAI, Anduril, Cerebras.
- Carried thin (1): Figure AI — marks published, dispersion/propagation suppressed.
- Excluded (5): Cohere (false positive), xAI (instrument mismatch), Perplexity, Groq
  (insufficient coverage), Scale AI (no presence).
- Criterion: 28+ distinct filers per quarter, judged on Level 3 **equity** rows only.
- Changes from `plan.md`: SpaceX added, Cohere removed. Cerebras kept despite being the
  smallest member because its Level 3 → Level 1 IPO transition is the only external validity
  check the project has.
- Record: `universe_v1.json`; rationale in `docs/feasibility.md` §8.

**Also confirmed**
- Field definitions checked against `nport_readme.htm` bundled in the zip. Mapping matches
  `plan.md` (C.1.d, C.2.a, C.2.c, C.6, C.8). **Every field is nullable — including
  `FAIR_VALUE_LEVEL`**, which the filter now depends on, so `NULL` must be handled explicitly.
- `ISSUER_CUSIP` is a free-text `VARCHAR2(9)`, not a validated CUSIP — which is why
  placeholder spellings vary by filer.

**Open**
- Only 2026Q2 is loaded — no cross-quarter movement observed yet.
- Supabase provisioned but no schema created.
- Downloaded 2026Q2 rather than 2026Q1 as `plan.md` Week 1 specifies: Q2 is the quarter
  containing the May/June filings that were hand-verified, so it is the one that can confirm
  them. Q1 remains un-downloaded.

**Next**
- Freeze universe v1 (human gate).
- Ingest 8+ quarters and reconcile counts.
- Build `funds` / `filings` / `raw_holdings` and `DATABASE_SETUP.md`.

---

## 2026-08-08 — Week 1: verification complete, filter defect found

**Done**
- Hand-verified 19 Anthropic PBC positions across 6 fund families (Fidelity, T. Rowe Price,
  Alger, ARK, BlackRock, Capital Group) from `primary_doc.xml` on EDGAR.
- Confirmed four-manager convergence at $259.14 (2026-03-31 / 2026-04-30) and the repricing
  to $589.0095 (2026-05-29 / 2026-05-31).
- Scaffolded the project: `.gitignore`, `.env.example`, `requirements.txt`, `src/`, `docs/`,
  `tests/fixtures/`, `scripts/`.
- Created Supabase project; `DATABASE_URL` in local `.env` (not committed).
- Wrote `scripts/verify_week1_marks.py` — recomputes every price from the recorded fixture,
  so `docs/feasibility.md` is reproducible rather than transcribed.
- Wrote `docs/feasibility.md`.

**Decisions**
- Compare at the **company** level, not share class. Confirmed on first-party data: Fidelity,
  T. Rowe and Capital Group each marked every class they hold at one identical price, common
  and preferred alike.
- **`fairValLevel = 3` is the load-bearing filter field.** `isRestrictedSec` and `cusip` are
  supporting signals only.

**Blocker / defect**
- The private-position filter specified in `plan.md` (lines 106, 400) keeps only 1 of 6
  managers. `CUSIP='N/A'` misses the `000000000` placeholder, and `isRestrictedSec` is
  reported `N` by ARK and Capital Group on restricted stock. Replacement proposed in
  `docs/feasibility.md` §2. **Must be settled before Week 2 ingestion.**
- Three factual errors in `plan.md` logged in `docs/feasibility.md` §6.

**Open**
- Universe v1 not yet frozen — human gate.
- Whether the bulk DERA TSVs preserve the raw XML's placeholder values is untested and is
  the largest remaining risk.
- Corrected filter has 100% recall on the verified set; precision untested.

**Next**
- Download 2026Q1 bulk, confirm the 30-TSV layout, and check whether `CUSIP` and
  `IS_RESTRICTED_SECURITY` in `FUND_REPORTED_HOLDING` match the raw XML for these same six
  accessions. That single check de-risks Week 2.
- Freeze universe v1 with written per-company rationale.
