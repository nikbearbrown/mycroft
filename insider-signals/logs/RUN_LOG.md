# RUN_LOG — Insider Signal Intelligence

Append-only execution history (SNICKERDOODLE P7). Concrete, dated, attributed.
Newest entries at top.

---

## 2026-11-12 — Survivorship risk recorded; share-type counts (no returns viewed); Rule 10 proposed, not registered

**Requested by:** Gomathy S.
**Recipe:** insider-signal-agent v0.1.0 (DRAFT)

**Survivorship risk** added to `status.md` and a new `## Risks` section of the recipe, in the owner's
words. `no_data` by quarter: 1,800 / 7,964 (2023 Q2) falling to 64 / 5,115 (2026 Q3); total 8,832.

**Share-type counts:** an ad-hoc classifier (session scratchpad `share_types.py`, not committed) read
only `security_title`, `source_quarter`, `price_status`, `filing_price_check` from
`enriched_buys.csv` (SHA-256 `fa146273…5bde`). No return, entry or exit column was read. First match
wins: warrants, notes, depositary/ADR, preferred, units, rights/options (→ other), foreign/ordinary,
common, other.

| Category | Buys | Priced | Rule 9 mismatch |
|---|---|---|---|
| common | 72,537 | 59,500 | 1,308 |
| foreign / ordinary | 1,716 | 1,077 | 352 |
| other | 1,568 | 892 | 98 |
| units | 1,236 | 990 | 3 |
| preferred | 886 | 117 | 482 |
| depositary / ADR | 529 | 291 | 88 |
| notes | 22 | 1 | 21 |
| warrants | 1 | 0 | 0 |
| **total** | **78,495** | **62,868** | **2,352** |

Totals match `enrich_summary.json`. Under a common-only rule (proposed Rule 10, strict match),
coverage would be 59,500 / 78,495 = **75.80%** over all buys and 59,500 / 72,537 = **82.03%** over
common buys. **Rule 10 is not registered or applied**; the decision is the owner's.

**Process note:** recipe edited on the owner's explicit written instruction (exact text supplied),
without a separate plan-mode step. **G3 not cleared.**

---

## 2026-11-09 — Rule 9 (filed price vs market) registered, built and run; coverage 80.09%

**Decided by:** Gomathy S. (Rule 9 registered in `PRE_REGISTRATION.md`, dated 2026-11-09, before any
returns were viewed; the first ENRICH run had computed per-buy returns, none viewed or summarized).

**Rule 9:** a buy whose filed price differs by more than 25% from the stock's unadjusted close on
`TRANS_DATE` (or the last bar before it), splits undone, gets `price_status = price_mismatch_vs_filing`
and no prices or returns. **Built:** `enrich.py` (split cache, `filing_price_check` halting check,
audit section); 9 new tests (suite 119, all pass; three deliberate Rule 9 bugs each failed them).

**Run:** `python enrich.py` with the price cache → 0 price requests; split histories for the 3,741
symbols with a priced buy, 94 batches of 40, 3 s apart, 2026-11-09 23:58 – 2026-11-10 00:10 UTC,
**0 refusals**. Exit 0; `--check` all PASS; a second run made no requests and gave the same file.
- `enriched_buys.csv` SHA-256 `fa14627333ac754a7f904e3417e5475241d7523659d46d6385779a7c65295bde`
  (replaces `657b98cd…`, gitignored).
- **Coverage 80.09%** (62,868 of 78,495; minimum 80%; thresholds unchanged). By quarter 71.58%
  (2023 Q2) to 87.48% (2025 Q4); 2023 Q2 – 2024 Q4 each below 80%.
- Rule 9: 65,220 checked → ok 61,688, **mismatch 2,352**, not checkable 1,180 (no bar on or before
  the trade date; stay priced). Split adjustment applied to 6,484 checked buys (93.4% of them match
  vs 96.7% without a split, consistent with Yahoo's Close being split-adjusted).
- Mismatches: 535 issuers; largest TSM 211 (2026 Q2–Q3), AMH 79, GAM 72, ACR 51; 1,897 carry no
  PARSE flag; 2,289 use a same-day bar.
- Windows: 21d closed 62,864, series_ends_before_exit 4, not yet closed 0; 63d closed 59,754,
  **not yet closed 3,114**. No return statistics were computed or reported.
- File sizes: `prices_manifest.json` 1.55 MB, `fetch_log.jsonl` 0.10 MB, `splits_manifest.json`
  0.84 MB, all under 5 MB, so committed.

**Open:** G3 not cleared.

---

## 2026-11-09 — ENRICH built and run on the study period; 78,495 rows promoted (G3 not cleared)

**Fellow:** Gomathy S.
**Recipe:** insider-signal-agent v0.1.0 (DRAFT)

**Built:** `enrich.py` (Rules 7–8) and `tests/test_enrich.py` (17 tests, no network; suite 110, all
pass). Three deliberate bugs (entry on the filing day, exit one day early, no whole-batch refusal
check) each made the tests fail.

**Run:** `python enrich.py` (yfinance 1.3.0, pandas 3.0.3, in a virtual environment outside the
repo) → exit 0. 4,641 symbols (4,640 from the buys + SPY) in 117 batches of 40, threads off, 3 s
apart, 2026-11-09 23:18–23:39 UTC; **0 refusals**. Range 2023-03-24 to 2026-11-09 (exclusive); last
SPY bar 2026-11-06. Cache: 3,833 symbols with data, 808 without. Then `--offline` (0 requests, same
`enriched_buys.csv`) and `--check` → all checks PASS.
- `enriched_buys.csv` SHA-256 `657b98cd80721c0ae5ab5cd2e1bff7a6a44b67bb5e6ff2fac86ea342c95f9448` (gitignored).
- **Coverage 83.09%** (65,220 of 78,495 buys priced; minimum 80%). By quarter from 73.87% (2023 Q2)
  rising to 92.53% (2026 Q2); 2023 Q2 – 2024 Q1 are each below 80%.
- price_status: priced 65,220 · no_data 8,832 · placeholder_symbol 2,945 · series_starts_after_entry
  1,014 · unparseable_symbol 298 · multiple_symbols 175 · no_bar_on_entry_date 11.
- Windows: 21d closed 65,216, series_ends_before_exit 4, not yet closed 0. 63d closed 61,860,
  **not yet closed 3,360** (all 2026 Q3).
- No return statistics were computed or reported.

**Findings for the owner:**
- `no_data` has two kinds: 562 symbols Yahoo does not know ("no timezone found") and 246 it knows
  but returned no bars for ("no price data found"), including symbols of companies expected to be
  listed (TCBI, KFS). A re-request of TCBI and KFS outside the script (one request, same answer)
  showed it is not transient. Not overridden.
- 32 symbols are filed by more than one issuer CIK (729 buys); the symbol is not checked against the issuer.
- Requests outside `fetch_log.jsonl`: the format probe disclosed in the Rules 7–8 entry, and the
  TCBI/KFS re-request above.

**Open:** G3 is not cleared until the owner logs it.

---

## 2026-11-09 — Decision: Rules 7–8 (return windows, G3 coverage); TODOs 4 and 5 closed

**Decided by:** Gomathy S., before any prices for the study's buys were fetched and before any
returns were computed.

- **Rule 7:** primary return window 21 trading days; one secondary window of 63 trading days.
- **Rule 8:** minimum price coverage for G3 is 80% of verified buys.
- Registered in `PRE_REGISTRATION.md` (dated 2026-11-09). Recipe TODOs 4 and 5 closed;
  `todos_open` 6 → 4.
- **Disclosed:** before this entry was written, one yfinance format probe was made (SPY, AAPL and a
  made-up symbol, 2026-10-01 to 2026-10-07). No study buy was priced and no return was computed.
- Process note: the recipe was edited on the owner's explicit written instruction (CLAUDE.md asks
  for plan mode before edits under `recipes/`).

---

## 2026-11-05 — Decision: Rule 2b; TODO 3 closed; 2023 Q1 parse outputs kept out of git

**Decided by:** Gomathy S.

- **Rule 2b** registered in `PRE_REGISTRATION.md` (dated 2026-11-05, before any prices, returns,
  clusters or scores were computed): "A 4/A whose original is not found in the study period, or
  that has no DATE_OF_ORIG_SUB, is its own event at its own filing date, flagged amendment_match =
  none_in_study or no_date_of_orig_sub." This is what `conformance.py` already does; no code or
  count changes (168 `none_in_study`, 0 `no_date_of_orig_sub` in the study period).
- **TODO 3 closed** (4/A → original accession matching) by Rules 2, 2a and 2b. Recipe
  `todos_open` 7 → 6.
- **2023 Q1 parse outputs** (`data/raw/parsed/2023q1_*`, produced before `trans_date_after_filing`
  existed; 2023 Q1 is outside the study) added to `.gitignore`: kept on disk, not committed.

---

## 2026-11-05 — Gate decision: G2 cleared (study period)

G2 cleared by Gomathy S. for the study period 2023 Q2 – 2026 Q3 after reviewing the conformance audit: 98 of 98 halting checks pass; 78,495 buys promoted (SHA-256 a7ec5529…db75b16); spot-check 25/25 consistent (15 exact, 10 rounding only, 0 other).

---

## 2026-11-04 — PARSE and GIGO on the study period (2023 Q2 – 2026 Q3); 78,495 buys promoted

**Fellow:** Gomathy S.
**Recipe:** insider-signal-agent v0.1.0 (DRAFT)

**PARSE:** `python parse.py --quarters 2023q2:2026q3` → 78,495 qualifying buys. `trans_date_after_filing`
excluded 11 buys (2023q2 1, 2023q3 1, 2024q1 3, 2024q2 2, 2024q4 1, 2025q2 3): exactly the 11 that
halted the earlier dry run.

**GIGO:** `python conformance.py --quarters 2023q2:2026q3`, User-Agent set (value not logged) → exit 0.
- All 7 halting checks PASS in all 14 quarters (98 of 98). 78,495 buys promoted;
  `insider_buys.csv` SHA-256 `a7ec55298bf886c0090f7c5fc4e93bfb18faeabc5d4c407db8d77abefdb75b16` (44.6 MB, gitignored).
- Spot-check (seed 16486067862572434945, a new sample over 14 quarters): 25 requests, all HTTP 200,
  spaced ≥ 1.0 s, all on the issuer-CIK path. **15 exact, 10 rounding only, 0 other mismatches.**
- Amendments: 1,743 buys on 1,033 4/A filings. Original: unique 849, resolved by Rule 2a 9,
  multiple 7 (own events), none in study 168 (72 with an original date before 2023 Q2; 96 inside
  the study period but not matched on issuer, owner set and date). 135 links to an earlier quarter.
  699 repeat buys (128 across quarters).
- Eligible for clustering (counts only): 78,495 → Rule 2 −699 → Rule 1 −3,032, Rule 3 −4,028,
  Rule 4 −5,630 → **65,106** at 4,146 issuers, from 38,320 filings (Rule 5). Cannot be STRONG
  (Rules 1, 6): 4,404 plan, 0 unknown.

**Open:** TODO 3, for the 168 4/As with no original found. G2 was cleared on 2026 Q3; the owner has
not logged a G2 decision for the study-period promotion.

---

## 2026-11-04 — Gate decision: G1 cleared

G1 cleared by Gomathy S. for 2023 Q1 – 2026 Q3: 15 requests, all HTTP 200, at 1 request/second, SHA-256 recorded for every quarter.

Note (from `data/raw/form345/request_log.jsonl`): the 15 requests are the 2026-11-04 batch
(data-set page + 14 ZIPs). 2026 Q3 was fetched on 2026-11-03 with 2 more requests, also HTTP 200,
so the log holds 17 requests for the 15 quarters. `ingest.py --verify` on 2023q1:2026q3 → PASS.

---

## 2026-11-04 — Decisions: dates rule, study period, Rules 2a and 6, file size, rounding

**Decided by:** Gomathy S., before any returns were computed.

- **Dates:** PARSE excludes a buy whose trade date is after its filing date, under the new counted
  reason `trans_date_after_filing` (last in the reason order). GIGO's independent filter applies
  the same rule. Tests added.
- **Study period:** 2023 Q2 – 2026 Q3 (14 quarters), changed from 2023 Q1 – 2026 Q3 because
  `AFF10B5ONE` is blank on most 2023 Q1 filings. The 2023 Q1 download stays on disk, outside the study.
- **`PRE_REGISTRATION.md`:** Rule 2a (several candidate originals: link only if exactly one holds an
  identical buy; otherwise its own event, `amendment_match = multiple`) and Rule 6 (`unknown`
  10b5-1 is treated like plan: may cluster, cannot be STRONG). Implemented in `conformance.py`.
- **TODO 3 stays open:** Rule 2a covers the several-candidates case, but not a 4/A whose original
  is not found (`none_in_study`) or one with no `DATE_OF_ORIG_SUB`.
- **File size:** `data/verified/insider_buys.csv` is gitignored and removed from the index (the
  file stays on disk); its SHA-256 is recorded in `conformance_summary.json` and `status.md`.
- **Rounding:** settled for sub-$1 buys by Rule 4; at $1.00 and above the 2-decimal rounding changes
  price by at most 0.5%, accepted as negligible.

---

## 2026-11-04 — Full study period ingested and parsed; GIGO halted on dates (15 quarters)

**Fellow:** Gomathy S.
**Recipe:** insider-signal-agent v0.1.0 (DRAFT)

**INGEST:** `python ingest.py --quarters 2023q1:2026q2 --rate 1`, User-Agent set (value not logged).
15 requests (data-set page + 14 ZIPs), all HTTP 200. `--verify` on 2023q1:2026q3 → PASS
(15 quarters). G1 is not cleared until the owner logs it.

**PARSE:** all 15 quarters; 84,580 qualifying buys. Findings: 2023 Q1 has 4,934 buys with
`is_10b5_1 = unknown` (`AFF10B5ONE` blank on all Jan–Feb and most Mar 2023 filings); Rule 1 does
not yet say how unknown is treated. 2023 Q3/Q4 and 2024 Q1 each lose 430–1,030 code P rows to
`price = 0.0`, mostly one or two issuers (FOMO Worldwide; Himalaya Technologies), consistent with
the data set rounding sub-half-cent prices to 0.00.

**Built:** cross-quarter 4/A matching in `conformance.py` (`match_amendments`, for Rule 2) and Rule 1–5
eligibility counts (`prereg_counts`). New verified columns: `amendment_match`, `amends_accession`,
`repeats_original_buy`. 5 new tests; suite 88, all pass.

**GIGO:** `python conformance.py --quarters 2023q1:2026q3` (offline dry run into a scratch folder)
→ **HALT, exit 1**: the `dates` check fails for 11 buys in 6 quarters (TRANS_DATE after FILING_DATE,
e.g. trade 2027-07-27 filed 2023-07-28). All other checks pass in all 15 quarters. Nothing
promoted; `data/verified/` still holds the 2026 Q3-only promotion. Spot-check not run.

**Diagnostic (in memory, not promoted; counts only):** amendments 1,962 buys on 1,135 4/A filings;
original unique 916, none in study 203, **multiple 16**; 142 links to an earlier quarter; 724 repeat
buys (130 across quarters). Eligible under Rules 1–5: 70,090 of 84,580 (includes the 11 date-failing buys).

**Blocker for the owner:** how to treat buys dated after their filing (exclude in PARSE with a new
reason, or keep halting). Also: Rule 6 was referenced but is not registered.

---

## 2026-11-04 — Gate decision: G2 cleared

G2 cleared by Gomathy S. after reviewing the conformance audit: all 7 halting checks pass; 5,115 buys promoted; spot-check 25/25 consistent (15 exact, 10 rounding only). Confirmation re-run at 18:08Z: same CSV hash, 0 new SEC requests (deterministic).

---

## 2026-11-04 — Decision: Rules 2–5 pre-registered; TODO 6 closed; TODO 3 updated

**Decided by:** Gomathy S.
**Recipe:** insider-signal-agent v0.1.0 (DRAFT), todos_open 8 → 7

**Registered in `PRE_REGISTRATION.md` (2026-11-04), before any returns were computed.** They apply
to cluster detection and scoring only; every row stays in `data/verified/` with its flags:
Rule 2 (a 4/A buy repeating its original's buy counts once, at the original's filing date);
Rule 3 (more than 30 calendar days from trade to filing → excluded); Rule 4 (price below $1.00
→ excluded); Rule 5 (all owners on one filing = one insider).

**TODO changes:** 6 (joint filings) closed by Rule 5. 3 (4/A matching, DEV) stays open and now
references Rule 2. New open item, not counted: identify fund and trust issuers (e.g. via SIC codes)
and decide whether to exclude them; not implemented.

**Count (2026 Q3, from `data/verified/insider_buys.csv` SHA-256 `dead8bee…26e07`; a count, not an
outcome):** 5,115 buys → 42 repeated 4/A buys collapse into their originals (Rule 2) → 5,073 →
excluded, first rule that applies: Rule 1 334, Rule 3 196, Rule 4 491 → **4,052 eligible for
clustering**, at 913 issuers. Each rule alone on 5,115: Rule 1 336, Rule 3 215, Rule 4 588.
Rule 5 changes how insiders are counted, not the number of eligible buys.

**Interpretations to confirm (AI-drafted, in `PRE_REGISTRATION.md`):** Rule 2 is applied first and
Rules 1/3/4 are judged on the original's row; "same owner" = same set of owner CIKs; Rule 3 keeps
exactly 30 days; Rule 4 uses the data set's rounded price. The reason sentence for TODO 6 in the
recipe is also AI-drafted.

**Process note:** recipe edited on the owner's written instruction, without a separate plan-mode step.

---

## 2026-11-04 — GIGO built; run on 2026 Q3; 5,115 buys promoted to data/verified/

**Fellow:** Gomathy S.
**Recipe:** insider-signal-agent v0.1.0 (DRAFT)

**Built:** `conformance.py` (stdlib only). Halting checks: hash, required columns, keys, dates,
codes, buy-filter purity (independent re-derivation from raw), identity. Promotion via a staging
folder only when all pass; on failure the audit goes to `data/raw/conformance/` and
`data/verified/` is unchanged. Spot-check of N = 25 seeded random buys against their EDGAR
filings. `ingest.SecClient.get` gained `allow_404`.
`tests/test_conformance.py`: 24 tests, including 7 that each break one halting check and prove
`data/verified/` keeps its bytes. A mutation run (failure branch disabled) made those 7 fail.
Suite: 83 tests, all pass.

**Run (real data):** `python conformance.py --quarters 2026q3`, User-Agent set (value not logged).
- All 7 halting checks PASS. 5,115 buys promoted → `data/verified/insider_buys.csv`,
  SHA-256 `dead8bee1a423dd97028b8e643b3e1ad24185c138cc7f3cad2410b1c86026e07`.
- Spot-check (seed 14553824015086086844): 23 requests (2 accessions sampled twice), all HTTP 200,
  spaced ≥ 1.0 s; all 25 resolved on the issuer-CIK path. **15 exact matches, 10 rounding only,
  0 other mismatches.** The data set rounds shares and price to 2 decimals (e.g. filed `0.006`
  → `0.01`). A re-run after adding the rounding classification used the cache: 0 requests.
- Rule 1 counts: 336 buys kept but excluded from clustering (private 135, ESPP/DRIP 201, both 0);
  136 plan buys may cluster but cannot be STRONG; 0 unknown; 4,779 cluster-eligible.
- Amendments: 144 buys on 92 Form 4/A filings; original found in quarter for 65 filings (unique),
  none for 27; **42 amendment buys repeat a buy on their original** (possible double count).
- Symbols: `NONE` 165 buys (41 issuers), `N/A` 45 (21), `NA` 3 (1).
- Lag (calendar days): median 2, p90 6, p99 342, max 7,308. 791 buys filed > 2 business days
  after the trade (no holiday calendar), none marked `L`; `TRANS_TIMELINESS`: blank 5,095, `E` 20.
- Joint filings: 686 buys from 231 filings.
- Not promoted, reported: 2 Form 4 rows with TRANS_DATE after FILING_DATE (codes S, J); 4 blank codes.

**Gate:** G2 is **not cleared**. Clearing it is the owner's logged decision after reading
`data/verified/conformance-audit.md`; G1 also still requires the full study period.

**Open for the owner:** (1) rounding: use filing values for low-priced buys, exclude them, or
accept; (2) the 42 repeated amendment buys (TODO 3); (3) Rule 1's `unknown` 10b5-1 case;
(4) confirm the AI-drafted reasons for closing TODOs 1 and 2.

**Process note:** recipe and `data/verified/` changed on the owner's written instruction
without a separate plan-mode step (see the entry below).

---

## 2026-11-04 — Decision: flagged-buy rule pre-registered; TODOs 1 and 2 closed

**Decided by:** Gomathy S.
**Recipe:** insider-signal-agent v0.1.0 (DRAFT), todos_open 10 → 8

**Rule (registered in `PRE_REGISTRATION.md`, Rule 1, dated 2026-11-04):** buys flagged
`espp_or_drip_flag` or `private_purchase_flag` stay in `data/verified/` with their flags but are
excluded from cluster detection and scoring. 10b5-1 plan buys may join clusters but cannot score
STRONG. Flag definitions are those in `parse.py` at `86c002c`.

**Recorded before any results:** no prices, returns, clusters or scores exist; `conformance.py`
had not been run. This entry and `PRE_REGISTRATION.md` were committed before the first GIGO run.

**TODO closures:** 1 (private-purchase rule) → the rule above. 2 (spot-check N) → 25, as
instructed for the G2 spot-check. The one-sentence reasons in the recipe were drafted by the AI
and await the owner's confirmation.

**Still open:** treatment of `is_10b5_1 = unknown` for STRONG (0 such buys in 2026 Q3).

**Process note:** CLAUDE.md asks for plan mode before edits under `recipes/` and
`data/verified/`. These edits were made directly on the owner's explicit written instruction,
which set out the change; no separate plan-mode step was used.

---

## 2026-11-03 — PARSE built; run on local 2026 Q3

**Fellow:** Gomathy S.
**Recipe:** insider-signal-agent v0.1.0 (DRAFT)

**Built:** `parse.py` (stdlib only): provenance check against manifest.json; headers read from
each file (missing required column → halt; AFF10B5ONE optional); SUBMISSION ⋈ NONDERIV_TRANS
with all REPORTINGOWNERs attached (joint filings stay one row); Form 4 / 4-A only; one class per
row; buy filter; AFF10B5ONE and RPTOWNER_RELATIONSHIP normalization; provisional footnote flags.
`tests/test_parse.py`: 24 tests on a synthetic fixture with real headers. Suite: 57 tests, all pass.

**Run (real data, no network):** `python parse.py --quarters 2026q3`, ZIP SHA-256 `a4e6a681…92c90f3`.
- Funnel: 59,885 non-derivative rows → 59,834 Form 4/4-A → 5,183 code P → **5,115 qualifying buys**.
- Independent recount from the raw TSVs (separate script) gave the same numbers.
- Excluded: 54,719. Largest reasons: sale 25,430; grant 9,791; option exercise (M) 7,433; tax withholding (F) 6,801. Code P rows failing the filter: 68 (price 53, shares 8, not acquired 6, equity swap 1).
- Qualifying buys by 10b5-1: plan 136, no plan 4,979, unknown 0.
- Flags (not excluded): likely private / issuer 135; ESPP / DRIP 201; joint filing 686.
- Context: 225 Form 4 code P rows are in the derivative table (excluded by design).

**Design change during the run:** flags first read footnotes from every column. The samples showed
holdings notes ("includes shares acquired through the DRIP") flagging purchases that weren't
DRIP. Flags now read only footnotes on the transaction's own fields. That removed 107 ESPP/DRIP
flags and 5 private flags. The 10b5-1 mention check still reads every footnote.

**Outputs:** `data/raw/parsed/2026q3_parse_summary.json`, `2026q3_parse-audit.md` (committed);
`2026q3_form4_transactions.csv` (gitignored, rebuildable).

**Open:** the private-purchase rule is still [TODO: DEFINE], and should cover ESPP/DRIP too. Nothing has entered data/verified/; that is G2.

---

## 2026-11-03 — INGEST built; live run on 2026 Q3

**Fellow:** Gomathy S.
**Recipe:** insider-signal-agent v0.1.0 (DRAFT)

**Built:** `ingest.py` (stdlib only): SEC_USER_AGENT required (name + email), 1 req/s
default, rates >= 10/s refused, ZIP URLs read from SEC's data-set page, manifest with
SHA-256, request log, checkpoint/resume via `.part` + hash, backoff then halt on 403/429/5xx,
safe extraction. `tests/test_ingest.py`: 33 unittest tests, no network. All pass.

**Live run (real data):** `python ingest.py --quarters 2026q3`, User-Agent set (value not logged).
- 2 requests to SEC (data-set page, ZIP), both HTTP 200, started 1.005 s apart.
- `2026q3_form345.zip`: 8,660,776 bytes, SHA-256 `a4e6a681cfcfa43a3d9e4ca9cfec1fd26a59d0a01eac7e9f7b5a0122092c90f3`.
- Extracted 8 TSVs + SEC's metadata JSON and readme HTM.
- Re-run: skipped (hash matched), 0 requests.

**G1 check:** `python ingest.py --quarters 2026q3 --verify` → PASS. G1 itself is not
cleared; that requires the full study period and the owner's logged decision.

**Resolved [verify] items (from the 2026 Q3 file, read locally):**
- `AFF10B5ONE` exists in SUBMISSION; values `0` (22,834), `false` (6,314), `1` (3,798),
  `true` (1,237), blank (3,969). PARSE must normalize them; blank = unknown.
- `RPTOWNER_RELATIONSHIP` is comma-separated and mixed case (e.g. `Director,Officer`), not the
  readme's uppercase.
- The file header says `FORM3_HOLDINGS_REPORTED`; the readme says `FORM3_HOLDING_REPORTED`.

**Raw counts (before any filter):** NONDERIV_TRANS 59,885 records, of which 5,184 have `TRANS_CODE = P`.

**Changed:** recipe (manifest field `user_agent` → `user_agent_set`, AFF10B5ONE note),
DATA_CONTRACT (resolved [verify] items, extracted file list), fixture rebuilt from real headers.

---

## 2026-11-03 — TODO closure batch: study period, G6 reviewer

**Fellow:** Gomathy S. · **Decided by:** Gomathy S.
**Recipe:** insider-signal-agent v0.1.0 (DRAFT)

- [TODO: DEFINE] Study period → **2023 Q1 – 2026 Q3**. Reason: SEC's 10b5-1 flag (`AFF10B5ONE`) exists for 2023+ data.
- [TODO: APPROVE] G6 reviewer → **Gomathy S. (self-attestation during development; external review pending)**.
  Attestations and reports must state they are self-attested until an external reviewer is named.

**Result:** `todos_open` 12 → 10.

---

## 2026-11-03 — Module scaffold (spec only)

**Fellow:** Gomathy S.
**Recipe:** insider-signal-agent v0.1.0 (DRAFT)

**Built:** README, _MANIFEST, DATA_CONTRACT, status, requirements, recipe, empty `tests/`.
**Checked:** SEC's Insider Transactions Data Sets page and readme PDF (coverage, tables,
fields, Trans Code List) and SEC's "Accessing EDGAR Data" fair-access rules, on 2026-11-03.
**Runs against real data:** none.
**Open:** 12 recipe TODOs at scaffold time; 2 `[verify]` items (AFF10B5ONE column, RPTOWNER_RELATIONSHIP format).
