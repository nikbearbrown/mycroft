---
status: DRAFT          # DRAFT | SPECIFIED | RUNNABLE-SAMPLE | RUNNABLE-LIVE | VERIFIED
todos_open: 10
last_gate: null
attestation: null
recipe_version: 0.1.0
---

# Insider Signal Agent — Recipe

> Mycroft recipe. Canonical specification for the insider-trading (SEC Form 4) signal
> pipeline. Governed by `SNICKERDOODLE.md` (P1–P8). Where this recipe and a script
> disagree, the disagreement is a logged defect (P6) — neither silently wins.

---

## Purpose & Overview

Turn public SEC Form 4 filings into a sourced **STRONG / WATCH / SKIP** decision per
company. The question: do **open-market purchases** by insiders — especially several
insiders buying the same stock within a short window — show market-adjusted signal,
and how much of insider buying is noise that should be skipped?

Most Form 4 activity is routine compensation (grants, option exercises, tax-withholding
sales) and carries no information about the insider's view. The value of this recipe is
the **honest skip rate**: say how much is filtered out and why, and show the residual
set with every number traced to its filing.

- **Domain owner:** Gomathy S. (Fellow, Humanitarians AI)
- **Release approver (G6):** Gomathy S. (self-attestation during development; external review pending).
  Decided by Gomathy S. on 2026-11-03 (`logs/RUN_LOG.md#2026-11-03`). Until an external
  reviewer is named, every attestation and report must say it is a self-attestation.
- **This is research, not financial advice.** Nothing in this pipeline places a trade.

---

## Source Inventory

| Source | Type | Layer | Notes |
|---|---|---|---|
| SEC Insider Transactions Data Sets | Bulk quarterly ZIP (tab-delimited, UTF-8) | `data/raw/` | **v1 primary.** Forms 3/4/5 incl. amendments, Jan 2006 → latest quarter (2026 Q3 as of 2026-11-03). |
| SEC EDGAR Form 4 filings (individual XML) | Per-filing documents in EDGAR Archives | `data/raw/` | v1: spot-check sample only (G2 audit) and report links. v2: near-real-time ingest. |
| Yahoo Finance via `yfinance` | Live API | `data/raw/` → `data/verified/` | Daily adjusted closes for the stock and SPY. Not authoritative — see Risks. |

Only INGEST and ENRICH touch the network (P2). SIGNALS, AGENT and REPORT read **only**
from `data/verified/`.

### SEC data options compared

| | A. Insider Transactions Data Sets (bulk) | B. Individual Form 4 filings | C. EDGAR latest-filings feed |
|---|---|---|---|
| What it is | Quarterly ZIP per quarter: data extracted by SEC from the XML part of Forms 3, 4, 5, flattened into 8 tables (SUBMISSION, REPORTINGOWNER, NONDERIV_TRANS, NONDERIV_HOLDING, DERIV_TRANS, DERIV_HOLDING, FOOTNOTES, OWNER_SIGNATURE) | One XML document per filing in EDGAR Archives, located through the quarterly/daily full-index files or the `data.sec.gov` submissions API | A rolling feed of filings as they are accepted |
| Coverage | Jan 2006 → latest completed quarter | Full history, same-day | Recent filings only |
| Freshness | Quarterly. Filings made after 5:30 pm ET on a quarter's last business day appear in the next quarter's posting | Same day | Minutes |
| Requests needed | One per quarter (~12 for a 3-year study) | At least one per filing — many thousands per quarter | Polling |
| Parsing | Already tabular, SEC-defined keys | We write and maintain an XML parser against SEC's Ownership XML technical specification | Index only; still fetch each filing |
| Caveats (SEC's own) | "as filed", may contain "redundancies, inconsistencies, and discrepancies"; SEC "cannot guarantee the accuracy"; "not a substitute for such filings" | The filing itself is the record | Not a history |

**Recommendation for v1: option A, the bulk data sets**, with a small option-B sample for
verification. Reasons:

1. **The research question is historical.** A backtest does not need same-day data, so
   the quarterly lag costs nothing in v1.
2. **Fair access is easy to respect.** About a dozen downloads versus thousands of
   per-filing requests.
3. **Fewer parser bugs.** SEC has already extracted the fields and defined the keys
   (`ACCESSION_NUMBER`, `NONDERIV_TRANS_SK`); we parse tab-delimited text, not hand-rolled XML.
4. **Provenance is cleaner (P3).** Each quarterly ZIP is a fixed artifact we can hash;
   every row still carries `ACCESSION_NUMBER`, which links back to the original filing
   for the report.
5. **The caveats are handled, not ignored.** SEC says the data sets are not a substitute
   for the filings, so the G2 audit checks a random sample of rows against their
   individual Form 4 XML (option B), and the report links every signal to the filings
   themselves, not to the data set.

Option B (with C to discover new filings) becomes the v2 ingest once the method is
validated, if the project moves to monitoring.

---

## SEC fair-access rules (INGEST must follow these)

From SEC's "Accessing EDGAR Data" page (checked 2026-11-03):

- **Rate limit:** "Current max request rate: 10 requests/second." SEC may lower it.
  This pipeline defaults to **1 request/second** and refuses any setting ≥ 10.
- **User-Agent:** declare one with contact info, in SEC's sample form
  `Sample Company Name AdminContact@<sample company domain>.com`. INGEST reads it from
  `SEC_USER_AGENT` (the same variable `verification-layer/datasources/edgar.py` uses) and
  **refuses to run** if it is unset or lacks an email address.
- **Efficient scripting:** download only what is needed; send `Accept-Encoding: gzip, deflate`;
  never re-download a quarter whose recorded SHA-256 already matches; no crawling.
- **On 403 / 429:** stop, back off, and log. Do not retry in a tight loop. Repeated refusals
  are a blocker for the human, not something to work around.

---

## Inputs & Dependencies

| Input | Required | Approval gate |
|---|---|---|
| `SEC_USER_AGENT` env var (name + contact email) | yes | INGEST refuses without it |
| Quarter range for the study | yes | **2023 Q1 – 2026 Q3** (15 quarters). Chosen because SEC's 10b5-1 flag (`AFF10B5ONE`) exists for 2023+ data, so the plan-purchase rule applies to every quarter. Decided 2026-11-03. |
| `data/raw/form345/<YYYY>q<N>_form345.zip` | yes | G1 |
| `data/verified/insider_buys.csv` | yes | G2 |
| `data/verified/enriched_buys.csv` | yes | G3 |
| `ANTHROPIC_API_KEY` | optional | enables the LLM research note; falls back to rule-based notes |

---

## Pipeline Stages

### 1. INGEST — SEC Insider Transactions Data Sets → `data/raw/`

`ingest.py --quarters 2023q1:2026q3`

- Downloads each quarterly ZIP. The download URL is read from SEC's data-set page, **not
  assembled from a pattern**: SEC hosts recent quarters under different folders
  (`/files/datastandardsinnovation/...` for 2026 Q3, `/files/structureddata/...` for
  earlier quarters, as of 2026-11-03).
- Writes `data/raw/form345/manifest.json`: per quarter, `source_url`, `retrieved_at`,
  `sha256`, `bytes`, `user_agent`, `http_status`.
- Appends every HTTP request to `data/raw/form345/request_log.jsonl` (timestamp, URL,
  status, elapsed) so the G1 check can prove the rate limit was respected.
- **Checkpoint/resume:** a quarter whose ZIP exists and whose hash matches the manifest is
  skipped; an interrupted download is discarded, never half-kept.
- Labor: AI executes. Human approves the quarter range and the live fetch (G1).

### 2. PARSE — Form 4 data and transaction codes → `data/raw/parsed/`

`parse.py`

- Joins SUBMISSION ⋈ REPORTINGOWNER ⋈ NONDERIV_TRANS on `ACCESSION_NUMBER`.
- Keeps `DOCUMENT_TYPE` in {`4`, `4/A`}; Forms 3 and 5 are out of scope for v1.
- Classifies every transaction row by `TRANS_CODE`, using SEC's Trans Code List:

| Code | SEC meaning | Treatment |
|---|---|---|
| **P** | Open market or private purchase of non-derivative or derivative security | **Candidate buy** (see filter below) |
| S | Open market or private sale | excluded (sales are out of scope for v1) |
| A | Grant, award or other acquisition pursuant to Rule 16b-3(d) | excluded — compensation |
| M | Exercise or conversion of derivative security exempted pursuant to Rule 16b-3 | excluded — option exercise |
| X | Exercise of in-the-money or at-the-money derivative security | excluded — option exercise |
| O | Exercise of out-of-the-money derivative security | excluded — option exercise |
| F | Payment of exercise price or tax liability by delivering or withholding securities | excluded — tax withholding |
| C, D, E, G, H, I, J, L, U, W, Z | conversion, disposition to issuer, expirations, gift, discretionary 16b-3(f), other, small acquisition, tender, will/descent, voting trust | excluded |

- **A row counts as a buy only if all hold:** `TRANS_CODE = 'P'`; `TRANS_ACQUIRED_DISP_CD = 'A'`;
  it is in **NONDERIV_TRANS** (Table I — derivative purchases are excluded in v1);
  `TRANS_SHARES > 0`; `TRANS_PRICEPERSHARE > 0`; `EQUITY_SWAP_INVOLVED` is not true.
- Code P covers **private** as well as open-market purchases, and the code alone cannot
  separate them. [TODO: DEFINE] the footnote/price rule used to flag likely private
  placements (e.g. price far from that day's market close), and whether flagged rows are
  excluded or kept with a flag.
- **10b5-1 plans:** SEC added `AFF10B5ONE` to SUBMISSION for 2023+ data. Pre-planned
  purchases are less informative; they are kept but flagged and **cannot score STRONG**.
  **[verify]** the column's exact name and values in the downloaded files — it is
  announced on SEC's data-set page but not yet in the PDF readme's table definitions.
- Every excluded row is counted by reason in the parse audit. Nothing is dropped silently.

### 3. GIGO — conformance checks, raw → verified promotion

`conformance.py` → `data/verified/insider_buys.csv` + `data/verified/conformance-audit.md`

Checks that **halt** the run (verification stack, layer 1):

| Check | Pass condition |
|---|---|
| Required columns | every field named in `DATA_CONTRACT.md` is present in each table |
| Keys | `ACCESSION_NUMBER` non-null; (`ACCESSION_NUMBER`, `NONDERIV_TRANS_SK`) unique |
| Dates | `FILING_DATE`, `TRANS_DATE` parse as `DD-MON-YYYY`; `TRANS_DATE` ≤ `FILING_DATE` |
| Codes | `TRANS_CODE` is in SEC's list; `TRANS_ACQUIRED_DISP_CD` ∈ {A, D} |
| Buys file purity | every row of `insider_buys.csv` meets the PARSE buy filter |
| Identity | `ISSUERCIK` and `RPTOWNERCIK` non-null (entity = CIK, never a name — see `DATA_CONTRACT.md` at repo root) |
| Hash | the ZIP's SHA-256 matches `manifest.json` |

Findings that are **reported, not halted on** (layer 2, the audit): rows excluded by
reason and code; amendments found and how they were resolved; blank or `NONE` trading
symbols; late filings (`TRANS_TIMELINESS = 'L'`); `TRANS_DATE` → `FILING_DATE` lag
distribution; joint filings (one accession, several reporting owners).

**Spot-check against the filings:** the audit samples [TODO: DEFINE] N rows (proposed: 25)
at random, fetches their individual Form 4 XML (within fair-access limits) and records
per row whether code, shares, price and date match. Mismatches are listed in the audit
for the human. They do not silently correct the data.

**Promotion rule:** `data/verified/insider_buys.csv` is written **only** when every halting
check passes (exit 0). On failure, nothing in `data/verified/` changes.

**Amendments (4/A):** `DATE_OF_ORIG_SUB` links an amendment to its original. The verified
file keeps the original row and records the amendment as a separate dated event, so a
backtest can use only what was public on a given date (see Look-ahead Rule).
[TODO: DEV] the matching rule from a 4/A to the specific original accession, which
`DATE_OF_ORIG_SUB` alone may not identify uniquely.

### 4. ENRICH — prices and market-adjusted returns → `data/verified/enriched_buys.csv`

`enrich.py`

- **Event date** = `FILING_DATE`, the first day the market could know (not `TRANS_DATE`).
- **Entry** = adjusted close on the **first trading day after** `FILING_DATE`. The data
  set gives the filing date but not the acceptance time, so a filing accepted after the
  close could not have been traded the same day. Entering the next day avoids that.
- **Exit** = adjusted close N trading days after entry. [TODO: DEFINE] N, fixed before any
  outcome is looked at (proposed primary: 21 trading days ≈ 1 month; one secondary window
  at most, declared in advance, to limit multiple comparisons).
- `stock_return = exit / entry − 1`; `spy_return` over the **identical** window;
  `abnormal_return = stock_return − spy_return`.
- Missing prices (delisted, renamed, foreign, bad symbol) are recorded with a reason
  (`price_status`). They are not dropped and not filled in.
- Gate G3 checks price coverage. [TODO: DEFINE] the minimum coverage (proposed: 80% of
  qualifying buys priced).

### 5. SIGNALS — insider cluster buys → `data/verified/clusters.json`

`signals.py`

- **Cluster:** ≥ 2 **distinct** insiders (`RPTOWNERCIK`) at the same company (`ISSUERCIK`)
  whose qualifying buys have `FILING_DATE`s within a **30-day** window.
- **Signal date** = the `FILING_DATE` of the filing that completes the cluster (the day it
  became knowable). Returns for scoring validation start from this date, using ENRICH's
  entry rule.
- **Joint filings:** [TODO: DEFINE] whether a single accession naming several reporting
  owners (e.g. a fund and its managing members) counts as one insider or several.
  Proposed: one, so a joint filing cannot form a cluster by itself.
- **Role weight** (from `RPTOWNER_RELATIONSHIP` + `RPTOWNER_TITLE`) — a model of judgment,
  labeled as such. Proposed: CEO 3 · CFO 3 · other officer 1.5 · director 2 ·
  10% owner 1 · other 0.5. [TODO: DEFINE] the weights and the title-to-role mapping
  (titles are free text: "Chief Executive Officer", "CEO & President", "Pres. and CEO"…).
- **Size factor** (purchase value = `TRANS_SHARES × TRANS_PRICEPERSHARE`, summed per
  insider per cluster). Proposed: < $25k → 0 · $25k–$100k → 1 · $100k–$1M → 2 ·
  ≥ $1M → 3. [TODO: DEFINE] the buckets, and whether a size relative to the
  insider's holdings (from `SHRS_OWND_FOLWNG_TRANS`) is used too.
- **Score** = Σ over distinct insiders of (role weight × size factor).
- **Labels:**
  - **STRONG**: cluster score ≥ T_strong **and** (≥ 3 insiders **or** ≥ 2 including the
    CEO or CFO) **and** no member's buy flagged 10b5-1.
  - **WATCH**: a cluster that does not meet STRONG.
  - **SKIP**: everything else, including every single-insider buy.
- [TODO: DEFINE] T_strong. All thresholds above are frozen in
  `PRE_REGISTRATION.md` **before** the backtest is run, and G4 checks that the thresholds
  in code match the pre-registration file.
- Outputs the counts at every step: qualifying buys → clusters → STRONG / WATCH / SKIP, and
  the **skip rate** (SKIP ÷ qualifying buys).

### 6. AGENT — LangGraph pipeline with gates → `logs/run_*.json`

`langgraph_pipeline.py`

```
conformance_gate ──(fail)──→ END                      never analyze unverified data
      │
      ↓
cluster_node ──→ score_node ──(0 STRONG and 0 WATCH)──→ review_packet
                     │
                     ↓
              research_node (LLM, optional) ──→ review_packet
                                                     │
                                                     ↓
                                      attestation_gate (human; LangGraph interrupt)
                                        │                         │
                                  (attested)                (not attested)
                                        ↓                         ↓
                                  report_node                 END — nothing reported
```

- Shared typed state with an **append-only run-log reducer**. Each node appends what it
  read, what it wrote, and its counts.
- `research_node` writes at most one short note per STRONG/WATCH signal. Every note is
  labeled **"model judgment"** (P8), may cite only fields present in state, and may not
  introduce a number.
- `attestation_gate` pauses the graph with a LangGraph interrupt and waits for a named
  human. Resuming requires an attestation record at
  `logs/attestations/insider-signal-agent-<date>.md` in the SNICKERDOODLE format (Tested
  table, Did not test, Broke during testing). The gate checks that the file exists and
  names the run id. It does not judge the content; the human does.
- **No signal is reported before attestation.** Until then the only human-facing output is
  the review packet, marked `NOT ATTESTED — NOT A REPORT`.
- [TODO: DEV] choose the LangGraph checkpointer for the interrupt (in-memory for tests,
  SQLite for real runs).

### 7. REPORT — sourced report → `reports/signal_report_<run_id>.md`

`report_node` (inside the pipeline) and `server.py` (MCP tools, week 9).

Required sections:
1. **Run header** — run id, recipe version, quarters, data-set hashes, attestation path.
2. **Funnel** — Form 4 rows → code P → qualifying buys → clusters → STRONG / WATCH /
   SKIP, with the skip rate and every exclusion reason with counts.
3. **Signals table** — company, ticker, signal date, insiders (name, role), purchase
   value, score, label, abnormal return (if the window has closed), and **filing links**.
4. **Per-signal sources** — every filing in the cluster as
   `https://www.sec.gov/Archives/edgar/data/<ISSUERCIK>/<ACCESSION_NUMBER without dashes>/`.
   [verify] the issuer-CIK path resolves for Form 4 filings on a sample at G5.
5. **Model notes** — research notes, labeled as model judgment.
6. **Limits** — what this run did not test (copied from the attestation).

Every number traces report → run log → script → recipe → filing (P3).

---

## Look-ahead Rule

**Use only information that was public on the filing date.** Concretely:

- The event date is `FILING_DATE`, never `TRANS_DATE` (insiders have up to two business
  days to file, and late filers longer).
- Trading starts the first trading day **after** `FILING_DATE`.
- A cluster on date *d* includes only filings with `FILING_DATE` ≤ *d*.
- An amendment (4/A) affects signals only from its own `FILING_DATE` onward. It never
  rewrites a past signal in the backtest.
- Role, title, ticker and company identity are taken **as filed**, not from today's data.
- Thresholds, windows and weights are fixed in `PRE_REGISTRATION.md` before outcomes are
  computed. Changing them after seeing results voids the backtest, and the change is logged.
- The universe includes companies that were later delisted. Missing prices are reported as
  missing, so survivorship shows up in the coverage numbers instead of being hidden.

---

## Phase Gates

Lifecycle: `DRAFT → SPECIFIED → RUNNABLE-SAMPLE → RUNNABLE-LIVE → VERIFIED`

| Gate | What it checks | Test command | Cleared by |
|---|---|---|---|
| **G1 Ingest** | every requested quarter's ZIP present; SHA-256 recorded in `manifest.json` with source URL, time, User-Agent; `request_log.jsonl` shows ≤ the configured rate and no unhandled 403/429 | `python ingest.py --verify` | Gomathy S. — [TO] technical owner; approves the quarter range and the live fetch |
| **G2 Parse + conformance** | all halting checks in GIGO pass; `conformance-audit.md` written, including exclusion counts and the filing spot-check; only then raw → verified | `python parse.py && python conformance.py` (exit 0) | Gomathy S. — [TO]; reads the audit before promotion |
| **G3 Enrich** | price coverage ≥ the defined minimum; every unpriced buy has a `price_status` reason; windows use the look-ahead rule | `python enrich.py --check` | Gomathy S. — [PF] proof of fitness |
| **G4 Signals** | cluster and label counts plus the skip rate logged; thresholds in code match `PRE_REGISTRATION.md` | `python signals.py --check-prereg` | Gomathy S. with reviewer — [IJ] interpretive judgment |
| **G5 Agent / review packet** | graph completes; every signal has ≥ 2 filing links and a sample resolves on sec.gov; every LLM note labeled model judgment | `python langgraph_pipeline.py --no-llm`, then without `--no-llm` | Gomathy S. — [EI] external interface |
| **G6 Attestation** | attestation record exists in SNICKERDOODLE format for this run and recipe version; only then is the report written | human review of the review packet → `logs/attestations/insider-signal-agent-<date>.md` | named reviewer (see Release approver above) — [PA] policy/approval |

Capacity labels (as in `congressional-signals`): [TO] technical owner · [PF] proof of
fitness · [PA] policy/approval · [IJ] interpretive judgment · [EI] external interface.

Every gate decision is logged in `logs/RUN_LOG.md` with who, what and when (P4).

---

## Output Contract (P5 — two customers, twice)

| Customer | Artifact | Location |
|---|---|---|
| Agent / audit | full run state, provenance, run log | `logs/run_<run_id>.json` |
| Human / reviewer | review packet (pre-attestation) | `reports/review_packet_<run_id>.md` |
| Human / reader | attested signal report | `reports/signal_report_<run_id>.md` |

---

## Stop Conditions

- `SEC_USER_AGENT` unset or without an email → HALT before any request.
- Configured request rate ≥ 10/s → HALT (config error).
- Repeated 403/429 from SEC → HALT, log, hand to the human.
- Any G2 halting check fails → HALT; `data/verified/` unchanged.
- Price coverage below the G3 minimum → HALT at G3, flag a data-quality issue.
- Thresholds in code ≠ `PRE_REGISTRATION.md` → HALT at G4.
- No attestation at G6 → no report; the review packet stays a draft.
- `ANTHROPIC_API_KEY` missing → research notes degrade to rule-based (not a halt).
- Any signal reported without a logged attestation → contract violation (P4/P8).

---

## Tests

`tests/` follows `verification-layer/tests/`: stdlib `unittest` only, no network and no
live model, small trimmed fixtures in `tests/fixtures/`, and a module docstring per test
file stating what the file pins down. Planned coverage: buy filter per transaction code,
date parsing, amendment handling, look-ahead (a 4/A filed later cannot change an earlier
signal), cluster windows at the 30-day boundary, joint filings, scoring against the
pre-registration file, rate-limit and User-Agent refusal, and the attestation gate
refusing to report without a record.

Run: `cd insider-signals && python -m unittest discover -s tests`

---

## CLI Reference (planned — scripts not yet written)

```bash
export SEC_USER_AGENT="Gomathy S. <contact email>"
python ingest.py --quarters 2023q1:2026q3     # INGEST     (G1: --verify)
python parse.py                               # PARSE
python conformance.py                         # GIGO       (G2)
python enrich.py                              # ENRICH     (G3: --check)
python signals.py                             # SIGNALS    (G4: --check-prereg)
python langgraph_pipeline.py --no-llm         # AGENT      (G5) → review packet
# human writes logs/attestations/... → resume   (G6) → report
```

---

## [TODO]

Open items (counted in `todos_open`):

1. [TODO: DEFINE] Private-purchase flag rule for code P, and whether flagged rows are excluded.
2. [TODO: DEFINE] Spot-check sample size N for the G2 audit.
3. [TODO: DEV] 4/A → original accession matching rule.
4. [TODO: DEFINE] Return window N (primary) and at most one secondary window.
5. [TODO: DEFINE] Minimum price coverage for G3.
6. [TODO: DEFINE] Joint-filing rule for clusters.
7. [TODO: DEFINE] Role weights and title → role mapping.
8. [TODO: DEFINE] Size buckets and whether relative size is used.
9. [TODO: DEFINE] T_strong.
10. [TODO: DEV] LangGraph checkpointer for the attestation interrupt.

Closed 2026-11-03 (decisions by Gomathy S., logged in `logs/RUN_LOG.md`):

- ~~[TODO: APPROVE] Named reviewer who clears G6~~ → Gomathy S. (self-attestation during development; external review pending).
- ~~[TODO: DEFINE] Study period~~ → 2023 Q1 – 2026 Q3, so the 10b5-1 flag is available for every quarter.

Also open, but not counted as recipe TODOs: write `PRE_REGISTRATION.md` before week 8;
DEV for each script listed in the CLI reference.
