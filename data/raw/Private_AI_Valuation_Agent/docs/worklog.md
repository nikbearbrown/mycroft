# Worklog

Newest first.

---

## 2026-09-18 (latest) — Week 8 figures and the video deliverable

Five figures built from `docs/_figdata_week8.json`, plus a 3:00 narration script and a README,
delivered to the week's video folder. Both QA passes run: layout audit **0/15 flagged**, and
every PNG read for substance.

**Four defects the accuracy pass caught in the drawing code** — each one a hand-typed value
standing in for a measured one:
- a subtitle hard-coded "Nine managers" when the Anthropic window holds **8 managers, 11 marks**;
- the red/grey split in that window hard-coded at `price > 220`, now the same single-linkage
  level clustering `src/signal/findings.py` uses;
- the dispersion highlight hard-coded at `spread >= 0.4`, now the measured p90;
- the propagation figure claimed **"the biggest events are the fastest"**, which the data does
  not support — events with 10+ managers have a median 27 days to half against 30 for the rest,
  and 12 of 28 smaller events land at zero days against 3 of 9 large ones. Replaced with counts
  that hold: 15 of 37 at zero days, slowest 92.

**Open**
- **Milestone PR 1 and PR 2 still not opened** — git is the user's.

---

## 2026-09-18 (earlier) — The Cerebras harness: everything except the data

**Chosen route:** wait for the SEC to publish 2026Q3 rather than fetching the filings from
EDGAR. So the work was to build every other step now, and make the study run itself the day
the archive catches up.

**Done**
- `public_observations` — a separate table for universe-company holdings at any fair value
  level other than 3. **Not** a widening of `PRIVATE_FILTER`: 5,806 rows reconcile against
  `raw_holdings` as a Level 3 layer, and loosening it in place would have silently redefined
  the re-mark rate, the dispersion and the panel.
- `src/ingest/public_marks.py` — scans the raw zips directly, because the Parquet layer was
  itself built with the Level 3 filter and a Level 1 row cannot be recovered from it.
- `src/signal/event_study.py` — derives the Level 3 → Level 1 crossing from the data,
  computes the discount path, and reports *why* it cannot run when it cannot.
- `tests/test_event_study.py` — 8 tests that inject a synthetic Level 1 observation and
  assert the arithmetic the report will print. A harness nobody will exercise for two months
  has to be proven now, or the silence in November is ambiguous.
- Findings §5 rewritten from the scan. Suite: **197 passed**.

**The scan changed what I thought I knew, twice**
- Week 8 concluded "no Level 1 rows exist" from probing Cerebras in two quarters. Scanning
  **all fourteen** at every level returned **10,566 non-Level-3 rows**, which looked like a
  contradiction.
- It was not. **10,126 of them are false positives** — every one of the 7,175 Level 1 rows is
  **Coherent Corp**, ticker COHR, caught by the deliberate `%COHERE%` canary planted in Week
  4. 186 more are the right company and the wrong instrument (`X.AI LLC TL 1L BANKDEBT`,
  `X.AI LLC/X.AI CO ISSUER 144A`, priced near $1.00 because they price per $100 of face).
  **254 are genuine, and none is Level 1.**
- So the conclusion survives, and is now measured across fourteen quarters instead of
  inferred from two.

**The finding I did not expect**
- **The Level 3 filter was doing double duty as a precision filter.** Remove it and the frozen
  Week 2 name patterns match the entire public market: one public company alone produced 7,175
  rows. Any future use of the public lane must route through the matcher and the review queue,
  not the patterns. The canary earned its keep a second time.

**Open**
- The study unblocks when `2026q3_nport.zip` is published — roughly November 2026 on this
  route — then `python -m src.ingest.public_marks 2026q3` and the report fills itself in.
- The three-pile classifier in `scan_quality` is approximate: a few Level 2 LLC co-issuer
  notes still land in the candidate pile. The conclusion does not depend on it, because no
  candidate is Level 1 under any classification.
- **Milestone PR 2 still not opened** — git is the user's.

---

## 2026-09-17 (earlier) — Week 8: dispersion, propagation, and a study that cannot be run

**Deliverable:** `docs/findings.md` with re-mark frequency, dispersion, propagation lag and the
Cerebras result — `src/signal/findings.py`, `scripts/analyze.py`, `tests/test_findings.py`.

**The four measurements**
- **Re-mark frequency: 25.0% of 4,079 consecutive observations are unchanged**, against
  `plan.md`'s expected 30–40%. Marks move *more* often than the thesis assumed. Robust: the
  share only reaches 29.6% if any move under 1% is treated as flat. Enormous variation by
  company — Anthropic 2.2% unchanged, OpenAI 1.1%, Groq 0%, against X.AI 48.5% and SpaceX
  37.4%. A single headline rate for "private marks" would hide that.
- **Same-date dispersion: 130 groups of 3+ managers, median spread 10.8%**, p90 40.5%, widest
  111.9%. 35 of 130 agree within 1%. But **92 of 130 contain more than one price level**, so
  the disagreement is mostly about which round is reflected.
- **Propagation: 37 events, median 30 days from the first manager to half the adopters**, 90
  days to all. The biggest events propagate fastest: Databricks at 190.00 across 20 managers
  and OpenAI at 687.6869 across 12 both reach half their holders in **0 days** — the same
  period end. Anthropic's 259.14 takes 27 days to half and 89 to all.
- **Cerebras: the event study cannot be run.** Two structural reasons, not an oversight.

**The Cerebras finding, which is a negative result about the data**
- `plan.md` calls it "a free, clean, private-mark-to-public-price event study with no
  additional data collection". It is not free. (1) The private layer is filtered to
  `FAIR_VALUE_LEVEL = '3'`, so Level 1 rows never entered Postgres — all 5,806 `raw_holdings`
  rows are Level 3. (2) The Level 1 observation's period end is 2026-05-29, which is in
  unpublished 2026Q3; the archive ends 2026-04-30.
- Probed the raw zips directly with no fair-value filter: **22 Cerebras row groups in 2026Q2
  and 10 in 2026Q1, all Level 3.** So the earliest possible Level 1 period end is after the
  archive ends.
- Reported instead: the Level 3 run-up, $21.46 → $100.26 across 19 period ends, +367%, with
  the last step 89.02 → 100.26. The report explicitly **declines** to compare against
  `plan.md`'s $236.99, because that number is in a plan document and not in any filing this
  project has ingested.

**Four defects found in my own measurements, each caught by reading the output**
- **Dispersion compared different securities.** The first version reported spreads of 31,983%
  and 1,098%. Those were SpaceX preferred against SpaceX common (a 10x filing convention) and
  one Coatue mark of `OPENAI GLOBAL, LLC` carrying **150,000,000 units at $1.5072** — an LLC
  interest priced per dollar of commitment, not a share. Now computed within (company, class
  kind) with scale outliers set aside and named. The Coatue row also pins the long-standing
  "$1.00 OpenAI" open issue to a single holding.
- **The window was a radius, not a span.** ±45 days is a 90-day span, and over 90 days
  Databricks genuinely moved 28.32 → 60.00. Calling that manager disagreement is nonsense. Now
  a 31-day forward span, matching `plan.md`'s own 4/30-to-5/31 example.
- **Propagation conflated staleness with slow propagation.** First-to-last gave lags of 427 and
  396 days on Databricks levels — managers still carrying a 2023 level in late 2024. The
  headline is now first-to-half, with first-to-last kept beside it and labelled.
- **A division by zero on an empty panel**, found by a test with no prior prices. A first run
  is a legitimate state.

**Also: a bare `%` inside an SQL comment** broke a parameterised query — psycopg2 scans
comments for placeholders too.

**Not claimed**
- Within-level agreement is **not** reported as a finding anywhere: it is bounded by the 2%
  clustering threshold by construction, so quoting it would restate a definition.
- Same-date dispersion still mixes disagreement with update timing; the level decomposition
  narrows that but does not remove it.

**Open**
- **Milestone PR 2 is not opened** — git is the user's.
- The `$1.00` OpenAI row is now identified but still priced in the panel; excluding it is a
  universe/parser change, not a findings change.
- Carried: Week 3's live EDGAR path (which is what the Cerebras study needs), non-USD currency
  guarded but unexercised, 314 of 322 golden-set labels unattested, the 28 `%COHERE%` holdings
  still inside the shipped universe layer, **milestone PR 1 still not opened**.

---

## 2026-09-11 (earlier) — Week 7 figures and narration, and four corrections they forced

**Done**
- `scripts/make_week7_figures.py` and five SVG/PNG figures, one per visual beat: the panel and
  its reconciliation, the tolerance window that missed its own test case, the share counts that
  separate a split from a repricing, ratio against factor, and `plan.md`'s seven checks. Every
  number is queried from the panel at build time into `docs/_figdata_week7.json`.
- Both QA passes: `npm run audit:layout` **0 errors on all five**, and each PNG read for
  substance. 3:00 narration script (458 spoken words, measured) and a README written to
  `D:\study_other
ew_humanitarians\humanitarians-youtubeellows\om-mali6-09-11-Building-the-marks-panel-and-the-split-detector`.

**Four things the figures caught**
- **A verification check failed because a human answered it.** `perplexity_split_blocked`
  required `NOT split_adjudicated`, so the Week 7 adjudication made it fail — it was asserting
  the pre-review state rather than the rule `plan.md` states. Corrected to require flagged and
  blocked, and to report the adjudication state. The figure's title also hardcoded "0 fail"
  while its own table showed one, so it now counts.
- **The evidence figure quoted a different fund than the RUN_LOG.** It ordered by position size
  ascending and picked the smallest SpaceX holding; the log cites the largest. Now deterministic
  and largest-first, so the figure and the written record quote the same row.
- **A rounding was doing part of an argument.** $4,228,993.75 rendered as $4,228,994 beside the
  words "the same dollars". Values now carry two decimals.
- **Red was used as a warning colour**, which `brutalist/DESIGN.md` forbids — red is the primary
  series, never danger. The two wrong choices in the factor figure are now secondary and red
  marks the answer the figure is about.

**Open**
- Unchanged from Week 7's close: non-USD currency guarded but unexercised; Week 3's live EDGAR
  path; 314 of 322 golden-set labels unattested; the 28 `%COHERE%` holdings still inside the
  shipped universe layer; **milestone PR 1 still not opened**.

---

## 2026-09-11 (later) — Week 7 closed: the split factor is recorded

**Done**
- The Perplexity adjudication was re-run with `--factor 10`. All **7** split marks now carry
  `split_factor = 10.00` and stay blocked awaiting the Week 8 adjustment; the 4 `not_a_split`
  marks carry no factor, correctly, and are back in the change series.
- `docs/marks_panel.md` regenerated. The quarantine table now shows the distinction the week
  turned on, in one row: ratio **11.9300**, factor **10.0000**. A reader can see that the
  number to divide by is not the number the detector measured.

**Week 7 is complete.** 5,479 marks, coverage reconciling exactly, the detector's three
questions answered by a named human, 176 tests, and no open items of its own.

**Open (carried, none from Week 7)**
- Non-USD currency is guarded but unexercised: all 5,806 holdings are USD.
- Week 3's live EDGAR path; 314 of 322 golden-set labels unattested; the 28 `%COHERE%`
  holdings still inside the shipped universe layer; **milestone PR 1 still not opened**.

---

## 2026-09-11 (earlier) — Week 7 splits adjudicated, and a defect that cost a re-run

**Done**
- Om Mali adjudicated all three suspected-split questions, covering 11 marks. Blocks lifted
  for Anthropic and SpaceX; Perplexity's 7 marks stay blocked awaiting the Week 8 adjustment.
  `series_flagged` is now 0 — nothing is left open.
- `adjudicate()` moved out of the CLI into `src/marks/splits.py` so it can be tested, with
  three new tests. Suite: **176 passed**.
- `docs/marks_panel.md` regenerated: the quarantine table now shows the verdict, the factor
  and how many marks remain blocked.

**The evidence, and the share count settled all three**
- **Perplexity — a real 10:1 split.** Five T. Rowe Price funds across PFD:D-1 and PFD:E-1
  show the share count multiplied by exactly ten with the dollar value **unchanged to the
  cent**: 19,395 → 193,950 at $13,488,132.50; 40,949 → 409,490 at $28,477,728.17; 10,496 →
  104,960; 6,081 → 60,810; 1,346 → 13,460; 98 → 980.
- **And the 11.93 case is a composite.** ARK's Perplexity common went 6,081 → 60,810 shares
  (×10) while the value fell $4,226,522.43 → $3,542,758.43. So 11.93 = a 10:1 split **and** a
  16% markdown in one period. Week 8 divides by 10; adjusting by 11.93 would erase a real
  price move, which is the mirror image of the mistake the detector exists to prevent.
- **Anthropic — not a split.** ARK holds **89,078 shares in every one of thirteen periods**;
  only the value moves. The 4.02 rise to $48.94 **reverses to $30.00** the next quarter, and
  a split never reverses.
- **SpaceX — not a split.** Neuberger Berman's share counts are constant at 22,368 and 3,428
  while value doubles exactly ($4,742,016 → $9,484,032 and $7,267,360 → $14,534,720). A 2x
  repricing that continues to $526.59 the following quarter.

**Defect — mine, and it cost the reviewer a repeat**
- `--factor` was accepted on the command line and **never written to the database**. Two
  edits I believed were saved were lost when a patch script asserted and exited before its
  write, so the `split_factor = %(factor)s` assignment and the guard that requires a factor
  both went missing. psycopg2 ignores an unused named parameter without complaint, so the
  command succeeded, printed a confirmation, and recorded a null factor.
- The verdicts, reviewers and rationales all landed correctly; only the factor is missing.
  One re-run of the Perplexity command fills it.
- **Fixed at the cause, not the symptom.** The logic now lives in
  `src/marks/splits.py::adjudicate()` rather than in the CLI, and
  `test_a_split_verdict_must_carry_a_factor` and
  `test_a_confirmed_split_records_its_factor_and_stays_blocked` would both have failed on the
  broken version. A guard that only exists in a script is a guard nothing tests.

**Open**
- **`split_factor` is null on Perplexity's 7 marks** pending one re-run. Week 8 needs that
  number and must not fall back to the detected ratio.
- Non-USD currency remains guarded but unexercised: all 5,806 holdings are USD.
- Carried: Week 3's live EDGAR path, 314 of 322 golden-set labels unattested, the 28
  `%COHERE%` holdings still inside the shipped universe layer, **milestone PR 1 still open**.

---

## 2026-09-10 (earlier) — Week 7: the marks panel and the split detector

**Deliverable:** the per-company/manager/period mark panel with splits caught and
quarantined — `src/marks/{build,splits,verify}.py`, `scripts/build_marks.py`,
`docs/marks_panel.md`, and the `marks` / `security_map` tables.

**Done**
- **5,479 marks** over 232 securities, 55 period ends, 861 company/manager/period rows.
  5,185 priced; 294 unpriced on purpose; 305 blocked from change series.
- **Coverage reconciles exactly**: 5,806 holdings = 28 rejected in Week 6 + 72 superseded by
  amendments + 5,706 aggregated into marks. A test asserts it.
- Split detector, two tiers: 11 marks `split_suspected` and blocked; 124 large moves routed
  for a look and deliberately **not** blocked; 101 marks flagged as sitting in a series that
  breaks somewhere.
- Re-mark against carry-forward, which Week 8 needs: **3,067 re-marked, 1,019 carried
  forward, 1,099 first observations.** A carry-forward and a zero delta are recorded as
  different facts.
- `--adjudicate` records a human verdict on a suspected split. `not_a_split` lifts the block;
  `split` **keeps** it, because applying a factor is Week 8's work under its own gate.
- `tests/test_marks.py` — 19 tests, one synthetic hazard per real defect. Suite: **173 passed**.

**The correction that matters**
- **The split rule missed `plan.md`'s own verification case.** Week 6 used an absolute ±0.02
  window; Perplexity's 695 → 58 is a ratio of **11.93**, which that window misses by a factor
  of three. It looked right only because the other Perplexity step lands on exactly 10.000.
  The rule is now a **relative 1% window under the same cap of 20**, defined once in
  `src/marks/splits.py` and imported by the Week 6 queue trigger so the two can never
  disagree. It still excludes X.AI's 2.064x repricing (44 occurrences) and still excludes the
  348x `$1.00` placeholder artifact — by the cap, which was always the part that mattered.

**Three things the data forced, all logged as deviations**
- **Amendments supersede.** All 16 `NPORT-P/A` filings restate a (fund, period) that already
  had an original, so the panel's own uniqueness constraint would otherwise have rejected the
  second and the survivor would have been an accident of insert order. The amendment wins;
  72 original holdings never become marks.
- **One security arrives on several lines, and sometimes those lines are not one security.**
  189 line groups inside a single filing share an issuer name and title; 464 rows. Summing is
  right for 151 of them. For the rest the lines disagree on price — SpaceX common and
  preferred filed under an identical title, ten times apart — so the mark is recorded
  **blended with no price**, keeping what the lines said. 6 marks.
- **`asset_category` is part of a security's identity**, not decoration: it is the only thing
  separating SpaceX common from preferred inside one filing. But three Databricks titles say
  "Series I" and are filed EC by one manager and EP by another — one security, two tags — so
  the category lives in `security_map` rather than in the security's key.

**A rule I wrote too strong, then narrowed**
- The first detector blocked every mark of a security whose series broke anywhere. That cost
  90 further marks, including all of ARK's Anthropic series, for a break that a change between
  two other periods never crosses. `plan.md`'s invariant is per mark. Now the series is
  *flagged* and only the step is *blocked* — different claims, different columns.

**Open**
- **3 split questions need a human**: Perplexity (a real 10:1 split by the Week 6 evidence),
  Anthropic 4.0181 (a repricing by the same evidence), SpaceX 2.0000. Nothing adjudicated
  itself; `split_adjudicated` is false on all 11 marks.
- Non-USD currency is guarded but untested by the data: all 5,806 holdings are USD.
- `plan.md`'s ~$589 check is unreachable from bulk and says so rather than passing quietly.
- Carried: Week 3's live EDGAR path, 314 of 322 golden-set labels unattested, the 28
  `%COHERE%` holdings still inside the shipped universe layer, **milestone PR 1 still open**.

---

## 2026-09-04 (earlier) — Week 6 figures and narration, and a count they corrected

**Done**
- `scripts/make_week6_figures.py` and five SVG/PNG figures, one per visual beat: the funnel, the
  24-spellings collapse, the graph and its checkpointer, the three price steps, and the closing
  scoreboard. Every number is queried from Postgres at build time and dumped to
  `docs/_figdata_week6.json` before anything is drawn.
- Both QA passes: `npm run audit:layout` **0 errors on all five**, and each PNG read for
  substance. 3:00 narration script (441 spoken words, measured) and a README written to
  `D:\study_other
ew_humanitarians\humanitarians-youtubeellows\om-mali6-09-04-Building-the-human-review-queue`.

**A count the figures corrected**
- The Week 6 write-up said "all four `split` triggers" and "wrong three times out of four".
  Counted from `review_decisions`: **three** split-triggered questions (9 cards, 925 holdings),
  so it is **two times out of three**. Fixed in `docs/entity_resolution.md` §10.8, this worklog
  and `logs/RUN_LOG.md`. Same failure mode as Week 5's confidence numbers — a count typed by
  hand instead of queried, caught only because a figure was generated from the source data.
- Perplexity's unchanged value is **$4,228,993.75**, not $4,228,994; an earlier query had
  rounded it with `::numeric(14,0)` before the number reached a decision rationale. The figure
  now shows it to the cent, which strengthens the point rather than weakening it.

**Defects found in the accuracy pass, which the layout pass cannot see**
- The graph diagram stacked `accept` and `interrupt()` vertically under `triage`, so it read as
  a sequence — as though every holding were accepted and then interrupted. Redrawn as an
  explicit fork with "one or the other, never both" on it.
- The X.AI list showed three rows reading identically, because three of the 24 spellings share
  one issuer name and differ only in the security title. Titles added. This is the third week
  running that a figure has needed this same fix.
- The collapse figure's subtitle ran off the right edge; the audit does not catch that, because
  the text element's own box is inside the canvas.

**Defects found in the script, not the figures**
- `psycopg2` interpolates `%` even when the parameter tuple is empty, so `LIKE '%D-1%'` raised
  `IndexError`. Fixed by passing `None` rather than `()` when there is nothing to bind.
- A holding was selected with `value_usd = 4228994`, which matched nothing. Replaced with a
  subquery that picks the smallest position by value, scoped to the same two periods — data
  choosing the row instead of a typed constant.

---

## 2026-09-04 (earlier) — Week 6 gate cleared: the queue is empty

**Done**
- Om Mali answered all 8 review questions in seven commands. **1,269 holdings decided by a
  human; 5,806 of 5,806 (100%) now carry a resolution decision.**
- `review_decisions` holds 45 rows for 42 cards — the three `new_company` answers each also
  wrote a company-level key, so a new X.AI spelling next quarter resolves without asking.
- Exported to `tests/fixtures/review_decisions_v1.json` (45 decisions). The regression test
  that had been skipping now runs and passes. Suite: **154 passed, 0 skipped**.
- `docs/review_queue.md` regenerated and now reports an empty queue.

**What the answers hand to Week 7 — and they do not point the same way**
- **SpaceX, 894 holdings: not a split.** Filing-unit artifact; same fund reports common at
  81.00 and preferred at 810.00 on the same date. Do not adjust.
- **Perplexity, 18 holdings: a real 10:1 split.** 6,081 → 60,810 shares with value identical
  at $4,228,994. Adjust. This is `plan.md`'s own verification case, caught before it entered
  a series as a 90% price crash.
- **Anthropic, 13 holdings: a repricing**, consistent with the verified staircase. The 4.0181
  ratio near 4 is coincidence. Do not adjust.
- A split detector that treats all three the same way will be wrong two times out of three.

**Also settled**
- The 28 `%COHERE%` canary holdings are formally `not_in_universe` on a written ground. They
  stay in `raw_holdings` (append-only); removing them from the universe layer is a
  universe-version change.

**Open**
- Nothing in Week 6. `securities` is empty because Week 7 fills it; `match_decisions.security_id`
  stays null until then.
- Carried: Week 3's live EDGAR path, the 16 `NPORT-P/A` amendments, 314 of 322 golden-set
  labels unattested, and **milestone PR 1 still not opened**.

---

## 2026-09-04 (later) — Supabase reachable; the queue re-run on the real database

**Done**
- Connected to Supabase again: `db.<ref>.supabase.co` resolves, **to an IPv6 address only**.
  That was the cause all along — the retired IPv4 direct host — and it works from a machine
  with IPv6 egress. Not a paused project.
- Applied the Week 6 schema there (`companies`, `securities`, `review_decisions`,
  `match_decisions`, plus the four LangGraph checkpoint tables), seeded 11 companies, and
  re-ran the queue against the project's own 5,806-holding universe layer.

**Result: identical, on a different server, with nothing migrated**
- 231 questions · 189 auto-accepted · **4,537 holdings decided (78.1%)** · 42 paused ·
  **1,269 waiting (21.9%)** · alias 2,760 / LEI 1,681 / fuzzy 57 / SPV 39 · the same 8
  questions. Every figure matches the local run to the row.
- This is the reproducibility claim in §10.7 being cashed rather than asserted. The local
  cluster was a stand-in, not a fork of the truth.

**Retired**
- The local Postgres 17.2 cluster is stopped. `DATABASE_SETUP.md` keeps the recipe: it is
  still the right answer when the network or the project is unavailable, and it needs no
  administrator.

**Open**
- Unchanged and still the only blocking item: **the 8 questions need a named human**, and
  1,269 holdings (894 of them the SpaceX split) are blocked behind them. `review_decisions`
  is empty; the exported fixture has 0 rows.

---

## 2026-09-04 (earlier) — the local cluster died, and the queue proved itself

**Done**
- Corrected `DATABASE_SETUP.md`: the local-cluster recipe now writes `port` and
  `listen_addresses` into `postgresql.conf` rather than passing them with `-o`, and
  redirects `pg_ctl`'s output so the server does not die with the shell that launched it.

**What happened**
- The stand-in cluster was started from a long-running foreground command. When that command
  was terminated the server went with it (`terminated by exception 0xC0000142`). A status
  report written minutes earlier said it was running; it was not, and that was corrected.
- **Restarting it restored everything**: 5,806 holdings, 4,537 `match_decisions`, 231
  checkpoint threads, the same 42 paused reviews behind the same 8 questions.

**Why it is worth logging**
- `test_a_paused_review_survives_a_new_process` asserts a paused review survives a *process*
  exiting. This was a server crash and a cold restart with WAL replay — a stronger claim than
  the test makes, arrived at by accident. The queue is durable in the way the week claimed.

---

## 2026-09-03 (later) — Week 6: the resolution graph and the review queue

**Deliverable:** a resumable review queue with decisions persisted, reused and turned into
regression tests — `src/graphs/resolve_graph.py`, `scripts/review_queue.py`,
`docs/entity_resolution.md` §10, and the generated `docs/review_queue.md`.

**Done**
- LangGraph graph: `candidates -> recall -> triage -> (accept | review) -> persist`, with
  `interrupt()` on the review branch and a `langgraph-checkpoint-postgres` checkpointer, so a
  paused review lives in Postgres and not in a process.
- Four triggers, from `plan.md`: `split`, `unresolved`, `band`, `new_company`.
- Two new tables. `review_decisions` is keyed by the **question**; `match_decisions` keeps
  `unique (raw_id)` and is the per-holding audit trail. Also `companies` (seeded, 11 rows) and
  an empty `securities` for Week 7.
- Reviewer's view as a CLI: `--run --status --list --show --decide --decide-company --report
  --export-fixture`. `--report` writes the queue as Markdown for a person to read (P5).
- `tests/test_review_queue.py`, 16 passing + 1 skipped. Suite total **153 passed, 1 skipped**.

**Result against the real universe layer**
- 231 distinct questions over 5,806 holdings. **4,537 holdings (78.1%) decided with no human**
  — alias 2,760, LEI 1,681, fuzzy 57, SPV 39. **1,269 (21.9%) waiting.**
- 42 paused cards behind only **8 real questions**. X.AI reaches the queue under 24 spellings.
- **The queue found the 28 `%COHERE%` canary holdings on its own.** Week 4 logged them as
  contaminating the shipped universe layer; nothing was added to make the queue look for them.
  The card shows the disagreement plainly: matcher says nothing, frozen pattern says
  `Cohere Inc. [FALSE POSITIVE]`.

**Decisions**
- **The unit of work is a question, not a holding.** `plan.md` asks for both `unique (raw_id)`
  and "keyed so the same ambiguity is never presented twice", which one table cannot do: 5,806
  holdings are 231 pairs, so a holding-keyed queue would ask about Databricks 85 times. Two
  tables, both invariants intact. Logged as a `plan.md` conflict.
- **`new_company` is answered against the company, not the string.** Otherwise X.AI is 24
  identical questions. `--decide-company` applies one answer, one reviewer, one rationale to
  every paused spelling at once.
- **Model confidence is not a trigger, and the adjudicator stays off by default.** Week 5
  measured confidence at 1.000 on 315 of 322 answers including 12 of the 15 wrong ones.
  Sorting this queue by it would put the wrong rows at the bottom.
- **A split is asked even at 1.00 matcher confidence.** SpaceX, 894 holdings, still asked,
  because `plan.md` says a suspected split is never auto-adjusted.
- **Nothing was decided on the user's behalf.** A decision needs a named reviewer and a
  rationale, and naming a company outside `companies` is rejected — admitting a company is a
  universe-version decision at the Week 1 gate, not a review-prompt decision.

**Defects found and fixed**
- **The split trigger's tolerance was proportional (2% of the ratio) and wrong.** At a ratio of
  348 that is a window of ±7, so it flagged three OpenAI questions at 348x, 320x and 306x as
  "near-integer". Those are the `$1.00` placeholder rows carried since Week 2, not splits. Now
  an absolute ±0.02 with the ratio capped at 20: flagged questions fell 19 → 9, and the
  survivors are SpaceX and Perplexity at exactly 10.0000 and Anthropic at 4.0181. A test pins
  both what the rule catches and what it must not.
- **`match_decisions.decision_key` had a foreign key to `review_decisions`.** It rejected every
  auto-accepted holding — exactly the rows that never needed a reviewer. The key is a grouping
  identity, not a reference; FK dropped, index kept.
- **The review card broke when redirected.** Windows hands Python a cp1252 stdout, which encoded
  the card's em dashes as bytes that are not valid UTF-8, so piping it to a file produced
  something `grep` called binary and refused to print. The card is a human artifact; the CLI now
  forces UTF-8 on stdout.
- **The first band test asserted the wrong side of the boundary.** `DXYZ SpaceX I LLC` scores
  0.90 exactly and is therefore accepted, not reviewed. Replaced with the Week 4 blended-class
  MWAM string, which scores 0.80, and added a test that pins the band's ceiling as exclusive.

**Blocker — the user's, not the pipeline's**
- **The project's Supabase instance is unreachable.** `DATABASE_URL` names
  `db.<ref>.supabase.co`, which no longer resolves: a paused free-tier project, or the retired
  IPv4 direct host (the pooler host in `DATABASE_SETUP.md` §1 does resolve). Week 6 ran instead
  against a **local Postgres 17.2** cluster, `initdb`-ed into the scratchpad with no admin
  rights and loaded from the Parquet layer — which reproduced the documented counts exactly:
  5,806 holdings, 14 quarters, 1 null price, 64 SPVs. Documented in `DATABASE_SETUP.md`.

**Open**
- **8 questions, 1,269 holdings, waiting on a named human.** 894 of them are the SpaceX split.
  `review_decisions` is empty and the exported fixture has 0 rows, so
  `test_every_exported_human_decision_is_still_honoured` skips rather than passes.
- The 42 paused threads are in the local cluster. They need **re-running, not migrating**, once
  the real database is reachable; the graph is deterministic and reproduces the same 8 questions.
- `securities` is created and empty; `match_decisions.security_id` is null until Week 7.
- The split trigger does not catch the `$1.00` OpenAI placeholder. Different defect, still open.
- Carried unchanged: Week 3's live EDGAR path, the 16 `NPORT-P/A` amendments, 314 of 322
  golden-set labels unattested, and **milestone PR 1 still not opened**.

---

## 2026-08-28 (later) — Week 5 figures, and the two numbers they caught

**Done**
- Wrote `scripts/make_week5_figures.py` and generated five SVG/PNG figures, one per visual beat
  of the narration: the prompt as it reached the model, the scoreboard, three failures in the
  model's own words, a 322-dot confidence grid, and every row the veto policy sees. Every number
  is read from `docs/_adjudication_metrics.json` and `docs/_adjudication_results.json` at build
  time and dumped to `docs/_figdata_week5.json` before anything is drawn.
- Both QA passes: `npm run audit:layout` reports **0 errors on all five**, and each PNG was read
  and checked for substance. Copied to the week 5 video folder under `pantry/` with a README.

**Two factual errors the figures caught, both now corrected**
- **Confidence: "308 of 322" was wrong; it is 315.** And "nine of the fourteen wrong answers at
  0.95 or above" was wrong twice over: 12 of the **15** answers that disagree with their label
  came back at 0.95+, or 11 of the **14** band-policy breaks if that is the intended denominator.
  Both original numbers were typed by hand. The dot figure computes its counts from the cached
  replies and disagreed with the prose, which is the only reason this surfaced.
  `scripts/run_adjudication.py` now emits a `confidence` block into the metrics artifact, and
  `test_the_confidence_prose_is_read_from_the_artifact` recomputes it from the cache. Corrected
  in `docs/entity_resolution.md` §9.4, `README.md`, this worklog, the RUN_LOG and the narration
  script.
- **The model was offered 11 candidate companies, not 7.** The figure's count came from
  `user.count("
- ")`, which matches nothing (the block is indented, not bulleted) and fell
  through to a hand-typed `or 7`. Seven is the universe; the list also carries four watchlist
  companies — and Scale AI and X.AI, the two names the model most often promotes to, are both
  watchlist. A fallback that hides a failed measurement is worse than no fallback.

**Decisions**
- Red marks the deterministic matcher in the scoreboard (it is the primary series and the system
  that ships) and the model's answers in the failure and confidence figures (they are the
  subject). `DESIGN.md` forbids red as a danger colour, so this needed stating rather than
  assuming.
- The confidence figure is a dot grid rather than a histogram. The model used three values in the
  whole run, so a histogram would be one tall bar; the grid shows the wrong answers sitting
  *inside* the full-confidence block, which is the actual finding.
- The veto figure names the trailing-space duplicate. Two of its four rows are the same string
  filed twice, and without that note they truncate identically — the same defect week 4's tie
  figure had to fix.

**Open**
- Inter does not resolve in the renderer and falls back to monospace, so every non-title label
  renders mono. Week 4's figures do the same, so this is consistent rather than new, but it is
  not what `DESIGN.md` specifies.

---

## 2026-08-28 (later) — Week 5 narration script

**Done**
- Wrote `docs/video_script_week5.md` — 306 spoken words, six beats, no file names, matching the
  format of weeks 1, 2 and 4. Word count and timings computed from the file, not estimated.

**Decisions**
- The script leads with the negative result and does not soften it. The Notes section carries
  three guardrails against overclaiming in the opposite direction: don't call the model useless
  (it is mis-scoped, not incapable), don't imply a larger model would also fail (none was tried),
  and **don't quote the hard-subset score** — every LLM policy scores a perfect 1.0000 there
  because that subset excludes the negatives, which is the only place the model does damage.
  That number is true and misleading at once, which is exactly the kind of figure a video
  invites.
- The strongest beat is the confidence finding, not the precision gap: 1.000 confidence on 315
  of 322 answers, with 12 of the 15 disagreeing answers at 0.95 or above. It is also the finding
  that constrains Week 6, so it earns the on-camera beat.

**Open**
- No figures for this week yet; the shot directions describe them but nothing has been rendered,
  so neither figure QA pass has been run.

---

## 2026-08-28 — Week 5: the LLM was measured and not adopted

**Deliverable:** matcher v2 with measured precision, recall and throughput against the
baseline — `docs/entity_resolution.md` §9, `docs/_adjudication_metrics.json`, and every raw
model reply in `docs/_adjudication_results.json`.

**Verdict: keep the deterministic matcher.** `plan.md` wrote the instruction for this case
— *"if there is no lift, keep the deterministic matcher and say so"* — and there is no lift.

**Setup.** Installed Ollama 0.33.1 and `llama3.1:8b` (8.0B, Q4_K_M, 5.3 GB, 100% on an RTX
4070 Laptop). 322 calls, temperature 0, fixed seed, JSON-Schema-constrained decoding,
**zero failures**. The model saw issuer name, title, filer and the candidate list — exactly
what the plan specifies — and deliberately no price, since the deterministic matcher does not
get price either. A test asserts the label never reaches the prompt.

**Measured, 322 strings, macro**

| System | Precision | Recall | F1 | Lift |
|---|---|---|---|---|
| Deterministic matcher v1 | 0.9959 | 1.0000 | 0.9979 | — |
| + LLM in the review band | 0.9449 | 1.0000 | 0.9717 | **−0.0262** |
| + LLM overruling everything | 0.9447 | 0.9958 | 0.9696 | −0.0283 |
| LLM alone | 0.9447 | 0.9958 | 0.9696 | −0.0283 |

Per holding that is 1 wrongly-included holding becoming **196**.

**How it fails: it promotes resemblances.** Of the 85 strings it saw, it fixed 1 and broke 14,
and all fourteen are the same move — the matcher had resolved nothing and the model named a
company anyway. `HYPERSCALE DATA INC` → Scale AI, on the invented ground that it *"is the
parent company of Scale AI"*. A `SCALED AGILE` term loan → Scale AI. `COHERE TECHNOLOGIES` →
Cerebras. And `XAI3-FT5O.AF`, a **Fidelity internal security code**, → X.AI. Two replies
contradict themselves outright: the reason says *"do not match any of the candidate
companies"* while the company field names Scale AI.

**Confidence is unusable.** 1.000 on 315 of 322 answers, and only three distinct values in
the entire run. Twelve of the fifteen answers that disagree with their label came back at 0.95
or higher (eleven of the fourteen band-policy breaks). Week 6's review queue cannot triage on
it, and a test pins that. *(Corrected 2026-08-28 from "308" and "nine of the fourteen" —
see the entry below.)*

**The hard subset lied, and that is a methodology finding.** Every LLM policy scores 1.0000
precision on the 144-string hard subset. That subset was defined in Week 4 to exclude labels
decided by the name — which excludes the `E0` negatives, which is the only place the model
does damage. A subset built to test one system is not automatically the right lens for the
next one.

**A fourth policy, and an honest account of it.** Every break was a *promotion*; the single fix
was a *demotion* — the matcher had claimed OpenAI for `OPEN BAY AUTOS AI INC.`, a used-car
marketplace, and the model withdrew it. So `POLICY_VETO` lets the model only withdraw a weak
claim, never create one. It scores 1.0000/1.0000. **That number should not be believed:** it is
consulted on 4 of 322 strings, vetoes one, and is right about the other three by declining to
act. It was also designed after reading the failures, so this golden set motivated it and
cannot validate it. Decisively, those four strings are *the same four Week 4 already routes to
a human*, so it saves no human effort. Retained, measured, **off by default**.

**Throughput.** 3.236 s mean per call, 196.9 tokens/s, 2.4 s cold load. Against the shipped
universe layer (231 distinct pairs): LLM-alone 12.5 min, band policy 16 s, veto policy 10 s.
Note the band policy consults 26.4% of the golden set but only 2.2% of the corpus — the golden
set over-samples near-miss negatives by design, so quoting its consult rate as an operating
cost would overstate the bill tenfold. Cost is not why this was declined; negative accuracy is.

**One dependency deviation.** `plan.md` pins `ollama==0.4.5`; `src/resolve/llm.py` uses
`requests`, already pinned, against the same HTTP API. One POST to one endpoint does not need
a wrapper package, and `OLLAMA_HOST` can now point anywhere.

Suite is **136 passing**, all of it stub-backed — no test needs a GPU or a 5 GB model.

---

## 2026-08-23 — Week 4 video figures, and two counting errors they exposed

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
