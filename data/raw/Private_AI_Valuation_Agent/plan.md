# Private AI Valuation Agent: Project Plan

> **Status:** this plan reflects a live feasibility verification performed against SEC data on
> 2026-08-04. Every data-source claim below was checked against real filings, not documentation.
> Verified figures are marked as such; the record lives in `docs/feasibility.md`.

## Why this project exists

Mycroft is an open source educational experiment, "Using AI to Invest in AI," built as a collection
of independent agents. Each agent takes one free public data source and turns it into an investment
signal about the AI sector.

Most of the AI sector's value sits in companies an individual investor cannot buy and cannot see
into: OpenAI, Anthropic, xAI, Databricks, Anduril, Cohere, Perplexity, Figure, Groq. There is no
ticker, no earnings call, no 10-K. What exists instead is indirect: US registered investment
companies that hold stakes in these companies must disclose **every portfolio position** on SEC Form
N-PORT, including private ones, with a US dollar value and a share count.

This is real and it is verified. A single Fidelity filing for period 2026-03-31 discloses:

```xml
<name>ANTHROPIC PBC</name>
<title>ANTHROPIC PBC SERIES F PC PP</title>
<cusip>N/A</cusip>
<balance>46814.00000000</balance>
<valUSD>12131380.00000000</valUSD>
<isRestrictedSec>Y</isRestrictedSec>
<fairValLevel>3</fairValLevel>
```

That is $12,131,380 across 46,814 shares — **$259.14 per share** — signed by a fund with a legal
obligation to value the position honestly and no incentive to talk its book to retail.

### The working hypothesis

**Fund marks are an informative, stepwise record of private AI pricing, and the way a new round
propagates across independent managers is itself measurable and interesting.**

This is a hypothesis to be tested, not a premise to be operationalized — but unlike most projects at
this stage, the first-order feasibility questions are already answered, and the answers reshaped the
thesis. Verified observations that drive the design:

* **Marks move stepwise at round events, not continuously.** Roughly 30–40% of consecutive
  observations are unchanged. Staleness is real but is *not* the majority case.
* **Managers converge hard at round events.** Anthropic was marked **$259.14** by Fidelity (3/31),
  T. Rowe (3/31), Alger (4/30) and ARK (4/30) — four independent managers, identical to the cent.
  Then a new round repriced it and BlackRock (5/29) marked **$589.01** while Capital Group (5/31)
  marked **$589.00**. Everyone moved together.
* **Genuine dispersion exists but is small.** Databricks near-simultaneously: ARK $198.01 (4/30),
  BlackRock $184.38 (5/29), Capital Group $180.92 (5/31) — roughly a 9% spread. Perplexity showed
  ~19% between T. Rowe and ARK.

So the interesting question is **not** "do funds disagree about value" — they mostly don't. It is
**how a repricing event propagates**: which managers move first, how long the lag is, and how wide
the spread gets in the window before everyone converges. Because fund fiscal quarter-ends are
staggered across the calendar (see below), that propagation is actually observable.

### How it helps the Mycroft project overall

* **Adds a private-market dimension the framework does not have.** All 40+ existing agents work on
  public-market, news, sentiment, hiring, patent, or repository data. None can see a private
  company's valuation. This closes a structural blind spot in a framework whose stated subject is
  the AI sector — where the most important companies are private.
* **Triangulation over trust.** The output is several independent parties' numbers for the same
  thing and the structure of their agreement. That maps onto the framework's Verification Agent
  concept and onto Cross-Agent Validation in the Mycroft layer, which prefers tracing conflicting
  conclusions over averaging them.
* **Feeds the coordination layer** with a versioned, machine-ingestible signal, distinct from the
  human-readable note.
* **Educational by design.** The intellectual content is not the pipeline; it is learning how fund
  marks actually behave — how often they move, how fast a round propagates, and what the
  write-up-all-classes convention hides.

### Honest positioning: this data is not undiscovered

**It would be false to call this an underused source, and the plan says so up front.**

* **Commercially exploited.** [Caplight](https://framer.caplight.com/solutions/investors) holds
  20,000+ investment fund marks across 370 late-stage companies and explicitly markets tracking how
  BlackRock, Fidelity, Franklin Templeton and Lincoln Financial value their stakes. Notice, Sacra,
  Forge and Nasdaq Private Market operate in adjacent space.
* **Academically mature.** Agarwal, Barber, Cheng, Hameed & Yasuda, "Private Company Valuations by
  Mutual Funds," *Review of Finance* 27(2) 2023; Gornall & Strebulaev, "Squaring Venture Capital
  Valuations with Reality," *JFE* 2020; Chernenko, Lerner & Zeng, "Mutual Funds as Venture
  Capitalists? Evidence from Unicorns," *RFS*; Kwon, Lowry & Qian, "Mutual Fund Investments in
  Private Firms," *JFE*.

**What does not exist is an open, reproducible, continuously-updated, AI-cohort-specific artifact.**
No public repository parses N-PORT for private-company marks; the GitHub "unicorn dataset" projects
are static Crunchbase scrapes, not filings-derived. The contribution is **open infrastructure, not
discovery.** Claiming novelty of the data source would not survive a literature review, and this
project will not claim it.

### Where it sits in the framework

**Analytical Agents.** Primarily a Research Agent ("combing through financial statements... to
construct profiles of target companies") and a Comparative Analysis Agent, with a Financial Report
Agent ingestion layer.

## What the agent does

On each run it:

1. Ingests N-PORT holdings from the SEC bulk data sets, topped up from live filings for the current
   quarter.
2. Filters to private positions: `IS_RESTRICTED_SECURITY = Y`, `FAIR_VALUE_LEVEL = 3`, and
   `CUSIP = 'N/A'`.
3. Resolves each holding to a canonical company and share class — the hard part.
4. Computes price per share: `value_usd / balance`.
5. Detects splits and recapitalizations before computing any change (see the trap below).
6. Builds the panel, detects re-mark versus carry-forward, and measures cross-manager dispersion and
   propagation lag around repricing events.
7. Emits a versioned JSON signal and a human-readable note.

The JSON signal and the note are deliberately distinct artifacts. The signal is a contract
(`schema_version`) the coordination layer parses and that must change slowly; the note is human
presentation that can be restyled freely.

## What the data supports — and what it does not

**Supported — arithmetic on disclosed figures, not estimates:**

* Price per share, per fund, per security, per period.
* Change over time, once split-adjusted.
* Dispersion across managers marking the same company in a near-simultaneous window.
* Propagation lag: how long between the first manager repricing and the last.
* Re-mark versus carry-forward.
* Which funds hold what, at what percent of fund net assets.

**Not supported:**

* **Company-level valuation.** N-PORT gives the fund's share count, never the company's total shares
  outstanding. Every alternative was checked and rejected: Form D has no share count or price;
  Delaware franchise filings give *authorized* and *issued* shares per-document for a fee, not
  fully-diluted, not by series, and near-useless for PBCs and LLCs; secondary marketplaces are
  paywalled and are themselves estimates, making the whole thing circular; and the 1940 Act
  affiliate threshold (Reg S-X 12-14, ≥5% of voting securities) never triggers at OpenAI or
  Anthropic scale. **This project does not publish company valuations.** Any such number would only
  be as good as an imported third-party share count, and would inherit that source's error.
* **Anything timely.** Verified lag is ~55–60 days after fiscal quarter end for individual filings,
  and the bulk data sets lag those by up to another ~90 days. The latest available mark is routinely
  2–5 months stale relative to the round that set it. This is structurally unsuitable as a trading
  signal and every output says so.
* **Complete coverage.** Some exposure is structurally invisible (see SPVs below) and the size of
  that gap cannot be quantified.

**Explicitly out of scope:** comparison of implied private multiples against public comparables.

## Verified data mechanics

### Filing cadence — quarterly, not monthly

The SEC adopted monthly N-PORT filing in August 2024, but **delayed compliance in April 2025** to
2027-11-17 (fund groups ≥$10B) and 2028-05-18 (smaller), and then in **February 2026 proposed to
reverse the monthly-publication element entirely** — file monthly within 45 days, publish quarterly
within 60 days — citing front-running concerns. The monthly public regime is **not in effect and may
never arrive.**

Verified empirically against Fidelity Contrafund (CIK 24238):

| Period end | Filed | Lag |
|---|---|---|
| 2025-03-31 | 2025-05-27 | 57d |
| 2025-06-30 | 2025-08-22 | 53d |
| 2025-09-30 | 2025-11-25 | 56d |
| 2025-12-31 | 2026-02-24 | 55d |
| 2026-03-31 | 2026-05-26 | 56d |

Four filings a year, median 56-day lag. Search form type **`NPORT-P`** plus `NPORT-P/A` amendments.
Build a quarterly pipeline, not a monthly one.

### The staggered fiscal-quarter insight

Period ends are **fund fiscal** quarter ends, not calendar. Observed across filers: Nov 30, Dec 31,
Jan 30/31, Feb 28, Mar 31, Apr 30, May 29/31. Each fund reports quarterly, but the *aggregate
universe* produces near-monthly observation density.

**This is what makes propagation measurable.** The Anthropic repricing is visible precisely because
Fidelity and T. Rowe report 3/31, Alger and ARK report 4/30, BlackRock reports 5/29 and Capital
Group 5/31. Exploiting the stagger is a core design decision, not an incidental detail.

### Fields — Level 3 and the restricted flag are public

Confirmed against the DERA schema and live XML. Items C.1–C.6, C.8 are public, including
**C.6 `isRestrictedSec`** and **C.8 `fairValLevel`**, which together make the private-position filter
work. **C.7 liquidity classification is reported but not public** and is absent from the bulk data.

**The identifier gotcha:** for private holdings `cusip` is the literal string `"N/A"`, ISIN is
absent, and the "other" identifier is a **proprietary internal code that does not join across fund
families** (Fidelity's `LKV546000` means nothing to BlackRock). LEI coverage is partial:

| Company | LEI |
|---|---|
| Anthropic PBC | `984500B6DEB8CEBC4Z70` |
| Anduril | `254900CIXLZUXXNYQW57` |
| Databricks | `984500FEDAC7FBD96273` |
| SpaceX | `549300B9WLO96RQCXP87` |
| OpenAI Group PBC | *none* |
| Cerebras | *none* |

Entity resolution must therefore be **fuzzy name matching with LEI as an assist**, not the reverse.

### Bulk data sets

* Landing page: `https://www.sec.gov/data-research/sec-markets-data/form-n-port-data-sets`
* Files: `https://www.sec.gov/files/dera/data/form-n-port-data-sets/{YYYY}q{N}_nport.zip`
* Coverage **2019Q4 → 2026Q2** (27 quarters). 2026Q1 is **441.6 MB compressed, ~4 GB uncompressed**,
  31 files (30 tab-delimited TSVs plus `nport_metadata.json`).
* Schema reference: `https://www.sec.gov/files/nport_readme.pdf`
* Join keys:
  `SUBMISSION / REGISTRANT / FUND_REPORTED_INFO --[ACCESSION_NUMBER]--> FUND_REPORTED_HOLDING --[HOLDING_ID]--> IDENTIFIERS`
* `FUND_REPORTED_HOLDING` carries C.1–C.8 and C.11 including `IS_RESTRICTED_SECURITY` and
  `FAIR_VALUE_LEVEL`.

**Order 10–15M holding rows per quarter** across the full fund universe. This drives the storage
decision below.

### Access

* **10 requests/second** maximum. A declared `User-Agent` is **required** — requests without one
  return HTTP 403, verified empirically.
* EDGAR full-text search **does** cover N-PORT:
  `https://efts.sec.gov/LATEST/search-index?q="Anthropic PBC"&forms=NPORT-P`, back to 2019–2020. It
  indexes both `primary_doc.xml` and the human-readable `QTLY_*.htm` exhibit, so **every filing
  returns duplicate hits — dedupe on accession number.** 10 hits per page, 10,000 result cap, so
  chunk queries by date range.
* `https://data.sec.gov/submissions/CIK{10-digit}.json` enumerates a filer's full N-PORT history.

## The two traps

These are the failure modes that produce confident, wrong output. Both are handled from day one.

### Trap 1: splits and recapitalizations create false crashes

Perplexity's per-share series runs `328.87 → 328.87 → 629.49 → 695.44 → 695.04 → 58.26`. That final
move is **not** a 92% collapse; it is roughly a 12x split. SpaceX shows common at $526.59 against
Series G/H/N preferred at **$5,265.90** — exactly 10x, a unit artifact rather than a preference
differential.

Without split detection, every return and volatility series the project produces is silently
garbage. A detector runs before any change is computed: flag near-integer ratio moves (2x, 5x, 10x,
12x), flag any single-period move beyond a threshold, and route to human review rather than
publishing. **A suspected split is never auto-adjusted.**

### Trap 2: per-filer title grammar, not liquidation preference

The expectation was that different share classes carry different marks. **They overwhelmingly do
not.** From one Fidelity filing, 2026-03-31:

| Issuer | Classes held | Price per share |
|---|---|---|
| Anthropic PBC | Series E, F, G | all **$259.14** |
| OpenAI Group PBC | A, A-2, A-3 | all **$687.69** |
| Anduril | Ser G, Cl B, Cl C | all **$63.74** |
| Cerebras | Ser G, Ser H | all **$89.02** |
| Stripe | Class B, Ser H, Ser I | all **$63.00** |
| Zipline | common + Ser E/F/G/H | all **$56.26** |

This reproduces **Gornall & Strebulaev** exactly: funds write up *all* classes to the latest round
price regardless of liquidation preference. Marks are therefore comparable across classes — but they
are **economically wrong**, because they ignore preference. Replicating and quantifying that on the
AI cohort is a legitimate finding this project can produce.

Genuine exceptions exist and must survive the pipeline: **World Labs** Series C $315.12 versus Series
C **Prime** $337.66 is a real differential, not an artifact.

**The actual engineering problem is that title grammar differs per filer and drifts over time:**

| Filer | How Anthropic appears |
|---|---|
| Fidelity | `ANTHROPIC PBC SERIES F PC PP` |
| T. Rowe | `ANTHROPIC PBC SER F-1 CVT PFD PP` |
| Capital Group | `ANTHROPIC PBC CL F-1 PFD PP (PHYSICAL) (NOT LISTED OR T…` |
| BlackRock | `ANTHROPIC PBC` — **no class at all** |
| ARK | `Anthropic, Inc.` — no class, different entity suffix |

`assetCat` (`EC` common / `EP` preferred) helps but is unreliable — ARK tags preferred stock as `EC`.

**Design consequence.** The original plan restricted dispersion to within-share-class comparison.
Given the write-up-all-classes convention and the fact that BlackRock reports no class at all, that
would discard most of the usable data. **Revised rule:** compare at the **company** level by default,
justified by the documented convention, with class recorded and the split/unit detector plus a
"genuine class differential" flag catching the exceptions. The justification is written into
`docs/entity_resolution.md`, not left implicit.

## Universe v1 (verified, frozen)

Discovered from the data rather than hand-picked. NPORT-P hit counts over the trailing 12 months:

| Company | Hits |
|---|---|
| Databricks | 1917 |
| Anthropic PBC | 476 |
| X.AI Corp | 427 |
| Anduril | 352 |
| OpenAI Group | 215 |
| Figure AI | 62 |
| Cohere | 32 |
| Perplexity AI | 26 |
| Groq | 17 |
| ~~Scale AI~~ | **0 — dropped** |

**Scale AI has zero N-PORT presence** post-Meta transaction and is removed from the target list.
Cohere appears essentially only via the **Private Shares Fund (CIK 1557265)**.

The universe is versioned and frozen within a phase; additions occur only at version boundaries, and
a boundary is treated as a discontinuity in every series.

### Verified holders (CIKs for direct ingestion)

| Complex | CIKs |
|---|---|
| **Fidelity** (deepest) | Contrafund 24238, Advisor Series I 722574, Select Portfolios 320351, Mt Vernon St 707823, Securities Fund 754510, Puritan Trust 81205, Investment Trust 744822, Hastings St 35348, Capital Trust 275309, Trend 35402, VIP 356494 / 831016 / 927384 / 720318 |
| **ARK Venture Fund** | **1905088** — 90 Level 3 positions, richest single filing |
| T. Rowe Price | Science & Technology 819930, International Funds 313212 |
| BlackRock | Capital Appreciation 887509, Large Cap Focus Growth 1097293, BlackRock Funds 844779 |
| Capital Group | New Economy 719608, Growth Fund of America 44201, American Funds Ins. Series 729528 |
| Alger | Alger Funds 3521, Alger ETF Trust 1807486, Alger Institutional 911415 |
| Others | Franklin Strategic 872625, Nuveen Investment Trust II 1041673, New York Life 787441 / NYLIM VP 887340, Fundrise Innovation 1867090, **Private Shares Fund 1557265** |

Unverified, worth checking in Week 2: Baillie Gifford US-registered funds, Morgan Stanley
Insight/Growth (Counterpoint Global historically held many), Neuberger Berman, Invesco.

### SPVs — three patterns, one of them a permanent coverage hole

* **Transparent (ARK):** `U First Capital Fund III LLC (SpaceX)`, `Studio Type One Soul II LLC
  (OpenAI)` — underlying named in parentheses. Parseable.
* **Hybrid (T. Rowe):** `AESTAS LLC dba OPENAI LLC EV UNITS Class A` — the SPV is the linked entity.
* **Opaque (Fidelity):** `FSOIFD TC HOLDINGS LLC`, `FSOIFDA FHUS HOLDINGS LLC` — no LEI, no CUSIP,
  underlying undisclosed. `FSOIFD` is the fund's own initials. **These cannot be seen through.**

Some private AI exposure is structurally invisible and the size of that gap is unquantifiable. The
project reports the count of opaque SPV positions rather than pretending they don't exist.

## Signals produced

* **Per-share mark** (deterministic): `value_usd / balance`.
* **Split flag** (deterministic + human): suspected split or recapitalization; blocks change
  computation until adjudicated.
* **Re-mark event** (deterministic): re-priced this period versus carried forward. A zero delta and
  a carry-forward are different facts and are never conflated.
* **Cross-manager dispersion** (deterministic): spread across managers marking the same company
  within a rolling window, with a minimum-holders threshold.
* **Propagation lag** (deterministic): days between the first and last manager reflecting a
  repricing — the project's most distinctive output, enabled by staggered fiscal quarter-ends.
* **Exposure map** (deterministic): who holds what, at what percent of fund net assets.
* **Quarterly commentary** (LLM): labeled commentary, never a verified claim, consistent with the
  desk convention in `chapter_exercises/your-own-mycroft/CLAUDE.md` — the AI gathers, structures and
  flags; only a human, citing a source, marks a claim verified.

Every signal except the commentary is deterministic and reproducible from stored raw data. The LLM
sits in exactly two places — entity-resolution adjudication and commentary — and in neither does it
touch a number.

## The validation experiment: Cerebras

Fidelity marked Cerebras **Level 3 at $89.02** on 2026-03-31. BlackRock reports it **Level 1 at
$236.99** on 2026-05-29 — it went public in between.

That is a free, clean, private-mark-to-public-price event study with no additional data collection:
how far below the eventual public price were the Level 3 marks, and how did that gap close as the
IPO approached? It is the single best available check on whether these marks mean anything, and it
is built into Week 8 rather than left as future work.

## Entity resolution

Everything downstream depends on: *which company and which share class is this row?* This is where
the LLM genuinely earns its place, and it is budgeted at **30–40% of total project time.**

No CUSIP, no ISIN, partial LEI, proprietary non-joining internal identifiers, four or more name
variants per company per filer, per-filer title grammar that drifts, and opaque SPVs.

**Three layers, deterministic first:**

1. **Deterministic candidate generation.** Normalize (case, punctuation, legal-suffix stripping —
   `PBC`, `Inc.`, `Corp`, `LLC`), block on normalized tokens, score with `rapidfuzz`. LEI is an exact
   short-circuit where present. High-confidence matches auto-accept.
2. **LLM adjudication** (local Ollama, structured JSON output) on ambiguous candidates only: issuer
   name, title of issue, filer, candidate set → company, normalized share class, confidence.
3. **Human review queue** below threshold, and unconditionally for every first appearance of a new
   company and every suspected split. Decisions persist in `match_decisions`, keyed so the same
   ambiguity is never presented twice, and each becomes a regression test case.

A **hand-labeled golden set** of 200–300 holdings is built in Month 1 before any LLM work, drawn to
include the known-hard cases: the five Anthropic title variants, opaque `FSOIFD` SPVs, the SpaceX
10x artifact, World Labs Series C versus C Prime, and ARK's `EC`-tagged preferred.

**Precision over recall.** A wrong match silently corrupts a company's whole series and is very hard
to notice; a missed match leaves a visible gap. Unresolved rows are retained and reported in every
run — never dropped, never quietly excluded.

## Pipeline architecture

```
DERA bulk N-PORT (2019Q4-2026Q2, ~442MB/qtr)     EDGAR FTS + primary_doc.xml (current qtr)
                 |                                            |
                 +---------------------+----------------------+
                                       v
                   [1] ingest/  — DuckDB over Parquet; filter to
                       IS_RESTRICTED_SECURITY=Y & FAIR_VALUE_LEVEL=3 & CUSIP='N/A'
                       (10-15M rows/qtr in, a few thousand out)
                                       v
                              raw_holdings  (Postgres, append-only)
                                       v
                   [2] resolve/  — normalize -> LEI short-circuit ->
                       block -> rapidfuzz -> per-filer title grammar
                                       v
                   [3] LangGraph resolution graph
                       candidates -> Ollama adjudicate -> confident?
                            |                                 |
                         yes|                                 |no / new company / split
                            v                                 v
                       securities                     interrupt() -> human review
                       match_decisions                (Postgres checkpointer, resumable)
                            +----------------+----------------+
                                             v
                   [4] marks/  — price_per_share = value_usd / balance
                       SPLIT DETECTOR -> re-mark vs carry-forward
                                             v
                                          marks
                                             v
                   [5] LangGraph analysis fan-out (per company)
                       dispersion + propagation lag -> synthesis (Groq)
                                             v
              +------------------------------+------------------------------+
              v                              v                              v
       JSON signal                  quarterly note                    MCP server
     (schema_version 1.0)          (human-readable)                (FastMCP, stdio)
              |                              |
              v                              v
      coordination layer           optional n8n digest email
```

## Where LangGraph earns its place (and where it does not)

Most of this project is batch ETL, and batch ETL should not be a graph. Being explicit about that is
part of the design.

* **Not a graph.** Bulk download, Parquet conversion, DuckDB filtering, loading. Plain Python,
  CLI-invoked, idempotent, re-runnable. Wrapping these in a state machine would add ceremony and
  remove nothing.
* **Is a graph — entity resolution.** A genuine agent loop: look up candidates, call tools (prior
  decisions, the alias table, LEI registry, Form D issuer names), re-evaluate, and on low confidence
  `interrupt()` to a human, backed by a Postgres checkpointer so the run pauses, survives a restart,
  and resumes when the reviewer returns days later. This would be the repository's first use of
  LangGraph checkpointing and `interrupt()`.
* **Is a graph — quarterly analysis.** Per-company fan-out computing dispersion and propagation lag,
  then a synthesis node. Follows the topology already in
  `AI_Vendor_Intelligence_Platform/agents/supervisor.py`: `TypedDict` state, `add_conditional_edges`
  with a `route_next` function, nodes returning `{**state, "field": value}`.

## MCP server

A small FastMCP server over stdio, exposing the resolved dataset so it is queryable from Claude
Desktop or Claude Code and reusable by other Mycroft agents without importing this project's code.
Repository first.

Tools: `list_companies`, `get_marks(company, share_class?)`, `compare_managers(company, window)`,
`get_propagation(company, event)`, `get_fund_exposure(fund)`, `list_unresolved`. Every response is
token-bounded with a cursor — a tool returning the whole marks table is useless to a model, so
summary-first with drill-down is the rule.

## Tech stack

* **Python 3.11** standalone core, patterned on `AI_Vendor_Intelligence_Platform`.
* **DuckDB + Parquet** for bulk filtering — 10–15M rows per quarter across 27 quarters.
* **Supabase Postgres** via `psycopg2-binary`, `DATABASE_URL`, following
  `AI_Vendor_Intelligence_Platform/collector/db.py`.
* **`requests`** with `EDGAR_NAME` / `EDGAR_EMAIL` User-Agent identity and a 10 req/s limiter,
  following `collector/edgar_collector.py`.
* **`rapidfuzz`** for deterministic fuzzy matching.
* **`langgraph`** + `langgraph-checkpoint-postgres`.
* **Ollama** (local, free), 8B-class instruct model (`qwen2.5` / `llama3.1`) with structured JSON
  output, for resolution adjudication.
* **Groq `llama-3.3-70b-versatile`** (free tier) for quarterly commentary only.
* **`fastmcp`** for the MCP server.
* **`pytest`** with golden fixtures, following `Hacker_News_AI_Buzz_Tracker/tests/`.
* **n8n** (optional, thin) for quarterly scheduling and digest email.

### Technology decisions

| Decision | Choice | Rationale | Alternatives rejected |
| --- | --- | --- | --- |
| Core runtime | **Standalone Python**, thin optional n8n wrapper | Bulk file parsing, entity resolution, and a longitudinal relational store. n8n has no good answer for any of the three. | Pure n8n (cannot parse 4 GB TSVs or host a resumable review queue); Airflow (heavy for one quarterly job). |
| Bulk processing | **DuckDB over Parquet** | 10–15M holding rows per quarter × 27 quarters. Verified 441.6 MB compressed / ~4 GB uncompressed for 2026Q1 alone. | **pandas in memory — rejected on verified volume.** An earlier draft of this plan chose pandas; the measured file sizes overturned it. |
| Ingestion path | **DERA bulk for history, EDGAR FTS + `primary_doc.xml` for current quarter** | Bulk sets are rebuilt quarterly and lag live filings by up to ~90 days; the hybrid gets both depth and freshness. | Bulk only (up to 3 months staler); per-filing XML only (thousands of requests against a 10 req/s limit). |
| SEC library | **Raw `requests` + bulk files** | N-PORT is not the shape `edgartools` is built around; bulk TSVs need no library. | `edgartools` (correctly used elsewhere in the repo for 10-K/8-K — just not here). |
| Private-position filter | **`IS_RESTRICTED_SECURITY='Y'` AND `FAIR_VALUE_LEVEL=3` AND `CUSIP='N/A'`** | All three fields verified public in the bulk data. | Identifier heuristics alone (would sweep in illiquid public positions). |
| Entity key | **Fuzzy name match, LEI as assist** | LEI is absent for OpenAI Group PBC and Cerebras; internal identifiers do not join across fund families. | LEI-primary or CUSIP-primary keying — verified impossible. |
| Matching | **Deterministic first, LLM only on ambiguity** | Reproducibility is the priority; most matches are unambiguous and should never reach a model. | LLM-on-everything (non-reproducible, slow, worse at easy cases than string matching). |
| Matching model | **Local Ollama 8B-class** | Thousands of rows, free, offline; short-string classification with constrained output suits small models. | Groq for matching (burns the free daily token limit — `AI_Vendor_Intelligence_Platform/README.md` documents dying at 33 of 50 companies on exactly this). |
| Commentary model | **Groq `llama-3.3-70b-versatile`** | A handful of calls per quarter; quality matters; free tier covers it. | Local 8B (weaker prose); Claude (paid, documented drop-in). |
| Persistence | **Relational tables, not one-row-per-run jsonb** | Longitudinal joins across periods, funds, companies and classes. | The house `hn_buzz_runs` / `patent_runs` pattern — deliberately broken; a jsonb blob per run cannot answer "every manager's mark on this company over eight quarters." |
| Dispersion basis | **Company level, class recorded** | Funds write up all classes to the latest round price (Gornall & Strebulaev, verified on this cohort); BlackRock reports no class at all. Within-class-only would discard most usable data. | Within-class only — an earlier draft's rule, overturned by the verified data. |
| Split handling | **Detect and route to human; never auto-adjust** | Perplexity's 12x and SpaceX's 10x would otherwise register as crashes and silently corrupt every return series. | Auto-adjust on ratio heuristic (would mis-adjust genuine repricings). |
| Human gate | **LangGraph `interrupt()` + Postgres checkpointer** | Review happens days after the run; the graph must genuinely pause and survive restart. | Blocking CLI prompt (loses state); a review web app (more surface than needed). |

## Storage schema

```sql
funds           (fund_id pk, cik, series_id, fund_name, family, first_seen, last_seen);
filings         (filing_id pk, fund_id fk, accession, form_type, period_end,
                 filed_date, source_url, unique (accession));

-- immutable raw layer: one row per disclosed private position, never edited
raw_holdings    (raw_id pk, filing_id fk, holding_id, issuer_name, title_of_issue,
                 cusip, other_id, other_id_type, lei, balance numeric, units, currency,
                 value_usd numeric, pct_net_assets numeric, asset_category,
                 issuer_category, is_restricted bool, fair_value_level int, ingested_at);

-- canonical layer
companies       (company_id pk, canonical_name, aliases text[], lei, is_ai bool,
                 universe_version int, notes);
securities      (security_id pk, company_id fk, share_class_raw, class_normalized,
                 filer_grammar, is_spv bool, spv_opaque bool, notes);

-- resolved analytical layer
marks           (mark_id pk, security_id fk, fund_id fk, filing_id fk, period_end date,
                 balance numeric, value_usd numeric, price_per_share numeric,
                 is_remark bool, prior_price_per_share numeric,
                 split_suspected bool, split_ratio numeric, split_adjudicated bool,
                 confidence numeric,
                 unique (security_id, fund_id, period_end));

-- audit trail: every resolution decision, machine or human
match_decisions (decision_id pk, raw_id fk, security_id fk null,
                 method text,   -- 'deterministic' | 'lei' | 'llm' | 'human' | 'rejected'
                 confidence numeric, model text, reviewer text, rationale text,
                 decided_at timestamptz, unique (raw_id));

runs            (run_id pk, started_at, completed_at, periods_ingested text[],
                 rows_scanned bigint, rows_private int, rows_resolved int,
                 rows_unresolved int, spv_opaque_count int, complete bool);
```

Three invariants:

* **`raw_holdings` is append-only.** Resolution never mutates source data, so the pipeline is fully
  re-runnable from raw and a matcher bug is always recoverable.
* **A run with `complete = false` is never the prior-period baseline** for re-mark detection — the
  same partial-run guard that protects the Hacker News tracker's velocity series.
* **A mark with `split_suspected = true` and `split_adjudicated = false` never enters a change
  calculation.**

## Deliverables (files in this folder)

`plan.md` (this document), `proposal.md`, `system_architecture.md`, `data_architecture.md`,
`README.md`, `DATABASE_SETUP.md`, `.env.example`, `docs/feasibility.md`,
`docs/entity_resolution.md`, `docs/findings.md`, `docs/worklog.md`,
`src/{ingest,resolve,marks,graphs,signal}/`, `tests/` with golden fixtures, `mcp_server/`, optional
`workflow.json`.

## Verification (how to test end to end)

* Ingest one quarter; reconcile private-position row counts against a DuckDB query on the source
  Parquet.
* Verify the Anthropic 2026-03-31 Fidelity position by hand: 46,814 shares, $12,131,380,
  **$259.14** per share.
* Confirm four managers resolve to the same $259.14 for Anthropic in the 3/31–4/30 window, and that
  the 5/29–5/31 pair resolves to ~$589.
* Confirm Perplexity's 695 → 58 transition is flagged as a suspected split and blocked from the
  change series until adjudicated.
* Confirm SpaceX common versus preferred is flagged as a 10x unit artifact, not a class differential.
* Confirm World Labs Series C versus C Prime survives as a genuine differential.
* Confirm unresolved rows and opaque SPV counts appear in the run summary rather than vanishing.
* Confirm the resolution graph pauses at a low-confidence row, survives a process restart, and
  resumes with the reviewer's decision applied.
* Confirm the JSON signal validates against `schema_version` 1.0.

### Error-handling decisions (fixed in Phase 1)

* **Missing or zero balance** is not a zero price. The row is retained with a null
  `price_per_share` and counted unresolved. Division by an absent balance must never produce a mark.
* **A partially ingested period** marks the run `complete = false` and is excluded from re-mark
  baselines.
* **An unresolved holding is never dropped** — it stays in `raw_holdings`, appears in the run
  summary, and enters the review queue.
* **A low-confidence match is never auto-accepted.** Silence is not consent.
* **A suspected split blocks change computation** rather than being auto-adjusted.
* **Pipeline failure alerting is separate** from analytical output, so a failed ingest is never
  mistaken for a quiet quarter.

## Risks, ranked

1. **Entity resolution.** No CUSIP or ISIN, partial LEI, non-joining internal identifiers, 4+ name
   variants per company per filer, drifting title grammar, opaque SPVs. The single biggest
   engineering cost and the main source of *silent* error. **Budgeted at 30–40% of project time.**
2. **Split and recapitalization artifacts.** Verified 12x (Perplexity) and 10x (SpaceX) cases that
   would silently corrupt every return series. *Mitigated by an explicit detector plus a human gate.*
3. **Novelty framing.** Caplight commercializes this and the academic literature has answered
   several of the interesting questions. *Mitigated by positioning as open reproducible
   infrastructure and citing the literature up front rather than being corrected later.*
4. **Data freshness.** Quarterly, 55–60 day lag; bulk sets up to 90 days behind that; the monthly
   regime is delayed to 2027/2028 and may be cancelled. *Accepted and stated, not mitigated.*
5. **SPV opacity.** Fidelity-style `FSOIFD` entries hide exposure and the gap cannot be quantified.
   *Mitigated by reporting the count rather than ignoring it.*
6. **Thin coverage on the tail.** Groq (17 hits), Perplexity (26) and Cohere (32, essentially one
   holder) may not support dispersion analysis at all. *Mitigated by the minimum-holders threshold
   and honest per-company coverage reporting.*
7. **Volume and infrastructure.** ~442 MB compressed per quarter × 27 quarters. *Mitigated by
   DuckDB/Parquet.*
8. **Title grammar drift over time.** Regex rules will rot. *Mitigated by the LLM adjudication layer
   and the golden-set regression suite.*

## Phase 1 exit criteria

Deliverable-based, not calendar-based:

* At least eight quarters ingest end to end with row counts reconciled against source.
* The golden set is labeled and matcher precision and recall are measured and recorded in
  `docs/entity_resolution.md`.
* The Anthropic four-manager convergence at $259.14 and the subsequent move to ~$589 are both
  reproduced from the pipeline, not from hand inspection.
* The Perplexity split is caught by the detector rather than published as a crash.
* Unresolved rows and opaque SPV counts are reported in every run summary.
* The JSON signal validates against `schema_version` 1.0.

## Why this is a good contribution

* **Genuinely useful.** It makes visible a part of the AI investment landscape individual investors
  cannot otherwise see.
* **Real data only.** No synthetic data, no paid services, no keys beyond a free Groq tier.
* **Verified before built.** The feasibility work is done; the plan rests on real filings, not hope.
* **Honest by construction.** It refuses to publish a company valuation it cannot derive, and it
  cites the prior art instead of claiming novelty it does not have.
* **Open where the alternatives are closed.** Caplight is a product; the academic work is not
  reproducible infrastructure. This is both.

---

# Three Month Weekly Plan

Feasibility is already established, so Month 1 goes straight to ingestion at scale. Month 2 solves
entity resolution — the acknowledged hard problem, budgeted the most time. Month 3 delivers the
distinctive analysis (propagation, the Cerebras event study), the query interface, and publication.

## How the work stays visible (do every week)

* Keep `docs/worklog.md` updated weekly — date, what was done, decisions, blockers, next — newest
  first, following `Hacker_News_AI_Buzz_Tracker/docs/worklog.md`.
* Attach artifacts: resolved mark tables, matcher metrics, run summaries, the propagation chart, and
  screenshots of the review queue and MCP server.

## Month 1: Ingest at scale

**Week 1: Reproduce the verification, scaffold, and lock universe v1**
* Reproduce by hand the Anthropic $259.14 position and the four-manager convergence, from the
  original filings, so the foundation is personally confirmed rather than inherited.
* Scaffold the folder, `.env.example`, `requirements.txt`, Supabase project, SEC User-Agent identity.
* Download 2026Q1 bulk, confirm the 30-TSV layout and the three-field private filter against
  `nport_readme.pdf`.
* Freeze universe v1 from the verified hit counts (Scale AI excluded) and write the selection
  criteria.
* Deliverable: `docs/feasibility.md` with hand-reproduced marks, confirmed schema, and universe v1.

**Week 2: Bulk ingestion at scale**
* Downloader with 10 req/s limiting and User-Agent; retry and resume on partial downloads.
* Convert TSVs to Parquet; DuckDB filter on `IS_RESTRICTED_SECURITY`, `FAIR_VALUE_LEVEL`, `CUSIP`.
* Create `funds`, `filings`, `raw_holdings`; write `DATABASE_SETUP.md`; make loads idempotent.
* Ingest all 27 quarters (2019Q4–2026Q2). Reconcile counts per quarter.
* Check the four unverified fund complexes (Baillie Gifford, Morgan Stanley, Neuberger, Invesco).
* Deliverable: 27 quarters of private positions loaded, with a reconciliation table by quarter.

**Week 3: Current-quarter path and deterministic matching**
* EDGAR FTS discovery for the current quarter, deduping on accession; `primary_doc.xml` parser.
* Normalization, LEI short-circuit, blocking, `rapidfuzz` scoring.
* First per-filer title grammar rules for the five known Anthropic variants.
* Deliverable: hybrid ingestion (bulk + live) plus a candidate match table with a distinct-issuer
  count.

**Week 4: Golden set and baseline metrics**
* Hand-label 200–300 holdings including the hard cases: five Anthropic variants, opaque `FSOIFD`
  SPVs, ARK's `EC`-tagged preferred, SpaceX 10x, World Labs C versus C Prime.
* Measure deterministic-only precision and recall; set thresholds from the measured curve.
* Write the first half of `docs/entity_resolution.md`. Open milestone PR 1.
* Deliverable: golden set committed as a test fixture, plus baseline matcher metrics.

## Month 2: Resolve entities and build the panel

**Week 5: Local LLM adjudication**
* Ollama with an 8B-class instruct model; structured JSON output schema.
* Adjudication prompt: issuer name, title, filer, candidates → company, normalized class, confidence.
* Measure lift over baseline on the golden set. **If there is no lift, keep the deterministic
  matcher and say so.**
* Record throughput so the cost of a full re-resolution is known.
* Deliverable: matcher v2 with measured precision, recall, and throughput versus baseline.

**Week 6: Resolution graph and human review queue**
* LangGraph graph: candidates → adjudication → confidence check → `interrupt()` on low confidence,
  new company, or suspected split.
* Postgres checkpointer so a paused run survives restart and resumes days later.
* Reviewer view; persist to `match_decisions`; guarantee decisions are reused, never re-asked.
* Deliverable: a resumable review queue with decisions persisted, reused, and added as test cases.

**Week 7: Marks panel and the split detector**
* Populate `securities` and `marks`; compute `price_per_share`.
* Build the split detector: near-integer ratio moves, single-period threshold breaches, routed to
  human, never auto-adjusted.
* Handle amended filings restating prior periods, non-USD currency, and opaque SPV flagging.
* Verify three series end to end by hand against source filings.
* Deliverable: the per-company/manager/period mark panel with splits caught and quarantined.

**Week 8: Dispersion, propagation, and the Cerebras study**
* Re-mark versus carry-forward with the partial-period guard; measure how often marks actually move.
* Cross-manager dispersion with the minimum-holders threshold.
* Propagation lag around repricing events, exploiting staggered fiscal quarter-ends.
* Run the Cerebras Level 3 → Level 1 event study.
* Open milestone PR 2.
* Deliverable: `docs/findings.md` with re-mark frequency, dispersion, propagation lag, and the
  Cerebras result.

## Month 3: Interface, integration, and publication

**Week 9: Form D and N-CSR context**
* Form D join on resolved issuer identity, not name string — dates and amounts only, never
  valuation, stated explicitly in the docs.
* **N-CSR / N-CSRS restricted-securities footnote (Reg S-X 12-12)**, which requires acquisition date
  and cost per restricted position — entry price and round timing that N-PORT lacks entirely. Scope
  this to the top three companies by coverage; treat wider coverage as a stretch.
* Build the per-fund exposure map and the per-company timeline.
* Deliverable: enriched timelines with entry cost where available, plus the exposure map.

**Week 10: MCP server**
* FastMCP server with `list_companies`, `get_marks`, `compare_managers`, `get_propagation`,
  `get_fund_exposure`, `list_unresolved`.
* Token-bounded responses with cursors; summary-first with drill-down.
* Test from Claude Desktop end to end; document setup in the README.
* Deliverable: a working MCP server queryable from Claude Desktop, with documented setup.

**Week 11: Commentary graph, signal contract, scheduling**
* Quarterly analysis graph: per-company fan-out → dispersion and propagation → synthesis via Groq.
* Prompt grounded strictly in computed numbers, with an explicit instruction to state when coverage
  is thin rather than filling the gap.
* Freeze the JSON signal at `schema_version` 1.0 and validate.
* Optional thin n8n workflow: quarterly trigger plus digest email, credentials in the n8n store.
* Deliverable: a generated quarterly note, a validated `schema_version` 1.0 signal, and a scheduler.

**Week 12: Documentation, catalogue, and launch**
* Finalize `README.md`, `proposal.md`, `system_architecture.md`, `data_architecture.md`,
  `DATABASE_SETUP.md`, `.env.example`.
* Complete `docs/entity_resolution.md` with final metrics and `docs/findings.md` with the full
  results, citing the prior-art literature honestly.
* Add the catalogue entry to `n8n_Workflows/README.md`.
* Record a demo: ingest, a review-queue decision, a resolved series, a propagation chart, an MCP
  query.
* Open final milestone PR 3.
* Deliverable: a complete, documented agent with a findings write-up and demo.
