# RUN_LOG — Insider Signal Intelligence

Append-only execution history (SNICKERDOODLE P7). Concrete, dated, attributed.
Newest entries at top.

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
