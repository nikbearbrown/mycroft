# PRE_REGISTRATION — insider-signal-agent

Rules fixed **before** any outcome is computed (recipe: Look-ahead Rule; gate G4). SIGNALS
and the backtest must follow this file. G4 (`signals.py --check-prereg`) checks that the code
matches it. A rule changed after outcomes have been seen voids the backtest, and the change
must be logged under **Amendments** below and in `logs/RUN_LOG.md`.

**Registered by:** Gomathy S.
**First registered:** 2026-11-04
**Recipe:** `recipes/insider-signal-agent.md` v0.1.0

## Project state at registration (2026-11-04)

Nothing that could reveal an outcome had been computed:

- INGEST: 2026 Q3 downloaded (ZIP SHA-256 `a4e6a681…92c90f3`). No other quarters.
- PARSE: 2026 Q3 row counts and flag counts only (`data/raw/parsed/2026q3_parse_summary.json`).
- **Not computed:** prices, returns, clusters, scores or labels. ENRICH and SIGNALS are not
  written. GIGO (`conformance.py`) had not been run.

---

## Rule 1 — flagged buys (registered 2026-11-04)

| Buy flag (as set by PARSE) | In `data/verified/insider_buys.csv` | Cluster detection | Scoring | Can a cluster that contains it be STRONG? |
|---|---|---|---|---|
| `espp_or_drip_flag = true` | **kept**, with its flags | **excluded** | **excluded** | n/a (never in a cluster) |
| `private_purchase_flag = true` | **kept**, with its flags | **excluded** | **excluded** | n/a (never in a cluster) |
| `is_10b5_1 = plan` | kept, with its flag | **may join** | counted | **no** (cluster is at most WATCH) |
| none of the above | kept | may join | counted | yes, if the STRONG thresholds are met |

What this means in practice:

- An excluded buy is not an input to SIGNALS. It does not form a cluster, does not count
  toward a cluster's number of insiders, and adds nothing to a score.
- A buy that is both a 10b5-1 plan buy and ESPP/DRIP- or private-flagged is excluded: the
  exclusion takes precedence.
- The flags are defined by `parse.py` at commit `86c002c`: `PRIVATE_PATTERNS` and
  `ESPP_DRIP_PATTERNS`, matched case-insensitively against footnotes on the transaction's own
  fields (`TRANSACTION_FN_COLUMNS`), and `is_10b5_1` normalized from `AFF10B5ONE`
  (`1`/`true` → plan, `0`/`false` → no_plan, anything else → unknown). **Changing a pattern
  changes this rule** and must be registered as an amendment before any outcome is computed.
- The private-purchase flag is the footnote rule only. No price-vs-market test is part of
  this rule.

**Not decided by Rule 1:** how `is_10b5_1 = unknown` is treated for STRONG → decided
2026-11-04 by **Rule 6** below.

---

## Rules 2–5 — cluster inputs (registered 2026-11-04)

Set by Gomathy S. on 2026-11-04, after the G2 conformance audit and **before any prices,
returns, clusters or scores were computed** (ENRICH and SIGNALS are not written). Like Rule 1,
these apply to **cluster detection and scoring only**. Every row stays in
`data/verified/insider_buys.csv` with its flags. Nothing is deleted or rewritten there.

| Rule | Applies to | Treatment in cluster detection and scoring |
|---|---|---|
| **2 — amendments** | a 4/A buy that repeats a buy in its original filing: same owner, trade date, shares and price | counted **once**, as the original's buy, at the **original's filing date** |
| **3 — stale disclosures** | buys with **more than 30 calendar days** between `trans_date` and `filing_date` | **excluded** |
| **4 — penny stocks** | buys with `price` **below $1.00** | **excluded** |
| **5 — joint filings** | all reporting owners named on one filing (accession) | count as **one insider** |

How the rules are applied (stated so G4 can check the code against it):

- **Order.** Rule 2 is applied first: a repeating 4/A buy collapses into its original, and Rules 1,
  3 and 4 are then judged on the original's row (its filing date, lag, price and flags). If the
  original is excluded, the repeat is excluded with it.
- **Rule 2 matching.** "Its original filing" is a Form 4 with the same issuer, the same set of
  reporting owners, and a filing date equal to the 4/A's `DATE_OF_ORIG_SUB`. "Same owner" means
  the same set of `RPTOWNERCIK`s. Shares and price are compared as they appear in the data set.
  A 4/A that does not repeat an original buy is its own event at its own filing date (look-ahead rule).
- **Rule 3** uses calendar days, `filing_date − trans_date > 30`. Exactly 30 days is kept.
- **Rule 4** uses the data-set price, which is rounded to 2 decimals. A buy filed at $0.995–$0.999
  appears as `1.00` and is kept.
- **Rule 5** governs the cluster rule's "≥ 2 distinct insiders": one filing contributes one
  insider, however many owners it names, so a joint filing cannot form a cluster by itself.

**Not decided by Rules 2–5:**
- ~~an original filed in an earlier quarter than its 4/A~~ → matching runs across every quarter
  of the study period (implemented 2026-11-04);
- ~~a 4/A that matches more than one candidate original~~ → **Rule 2a** below;
- ~~a 4/A whose original is not found, or that has no `DATE_OF_ORIG_SUB`~~ → **Rule 2b** below;
- whether the same owners on **different** filings count as one insider (Rule 5 covers one filing only).

---

## Rules 2a and 6 (registered 2026-11-04)

Set by Gomathy S. on 2026-11-04, **before any prices, returns, clusters or scores were computed**.
Like Rules 1–5 they apply to cluster detection and scoring only; every row stays in
`data/verified/insider_buys.csv` with its flags.

| Rule | Applies to | Treatment |
|---|---|---|
| **2a — several candidate originals** | a 4/A with more than one candidate original (same issuer, same owner set, filed on its `DATE_OF_ORIG_SUB`) | linked **only if exactly one** candidate contains a buy identical to one of the 4/A's buys (same owner set, trade date, shares and price); Rule 2 then applies to that link (`amendment_match = resolved_rule_2a`). Otherwise the 4/A is **its own event** at its own filing date, flagged `amendment_match = multiple` |
| **6 — unknown 10b5-1 status** | buys with `is_10b5_1 = unknown` | treated like 10b5-1 plan buys: **may join clusters but cannot make a cluster STRONG** |

---

## Rule 2b (registered 2026-11-05)

Set by Gomathy S. on 2026-11-05, after the G2 conformance audit for the study period and
**before any prices, returns, clusters or scores were computed**. Like Rules 1–6 it applies to
cluster detection and scoring only; every row stays in `data/verified/insider_buys.csv` with its flags.

| Rule | Applies to | Treatment |
|---|---|---|
| **2b — original not found** | a 4/A whose original is not found in the study period, or that has no `DATE_OF_ORIG_SUB` | **its own event** at its own filing date, flagged `amendment_match = none_in_study` or `no_date_of_orig_sub` |

---

## Rules 7 and 8 — return windows and G3 price coverage (registered 2026-11-09)

Set by Gomathy S. on 2026-11-09, **before any prices for the study's buys were fetched and before
any returns were computed** (ENRICH not written). Closes recipe TODOs 4 and 5.

Project state at registration (2026-11-09): `data/verified/insider_buys.csv` holds 78,495 buys
(SHA-256 `a7ec5529…db75b16`, G2 cleared 2026-11-05). No prices, returns, clusters or scores.
One format probe was made before this entry was written: a single yfinance request on 2026-11-09
for SPY, AAPL and a made-up symbol, 2026-10-01 to 2026-10-07, to learn the response layout. No
study buy was priced and no return was computed from it.

| Rule | Applies to | Value |
|---|---|---|
| **7 — return windows** | every verified buy (ENRICH) | **primary window: 21 trading days**; **one secondary window: 63 trading days**; no other window is used for any reported result |
| **8 — G3 minimum price coverage** | ENRICH, gate G3 | **80% of verified buys** priced |

How Rule 7 is applied (from the recipe's ENRICH stage, fixed here so G3 and G4 can check it):

- **Entry** = adjusted close on the **first trading day after** `FILING_DATE`.
- **Exit** = adjusted close **21** (primary) or **63** (secondary) trading days after entry.
- `stock_return = exit / entry − 1`; `spy_return` = SPY over the **identical** entry and exit dates;
  `abnormal_return = stock_return − spy_return`.
- A window whose exit date is after the last available market date is `not_yet_closed`; it has
  no return and is never filled in.

**Not decided by Rules 7–8:**
- exactly which buys count as "priced" for the 80% (for example: an entry price only, or an
  entry price and a closed primary window).

---

## Rule 9 — filed price vs market price (data quality; registered 2026-11-09)

Set by Gomathy S. on 2026-11-09, **before any returns were viewed**. State at registration: the first
ENRICH run (2026-11-09) computed per-buy returns into `data/verified/enriched_buys.csv`
(SHA-256 `657b98cd…c95f9448`); no return, average or other return statistic had been viewed,
summarized or reported. Only coverage and status counts had been seen.

| Rule | Applies to | Treatment |
|---|---|---|
| **9 — filed price vs market** | every buy ENRICH would otherwise price | compare the filed price per share with the stock's **unadjusted close on `TRANS_DATE`** (or the nearest prior trading day), accounting for stock splits. If they differ by **more than 25%**, `price_status = price_mismatch_vs_filing`: the buy gets no entry price, exit price or returns, and counts as unpriced for Rule 8 |

How Rule 9 is applied:

- **Filed price** = `price` in `data/verified/insider_buys.csv` (the data set's value, 2 decimals).
- **Reference close** = Yahoo's `Close` (split-adjusted, not dividend-adjusted) on the last day with
  a bar on or before `TRANS_DATE`, multiplied by every split ratio with a split date **after**
  `TRANS_DATE` and on or before the date the prices were fetched. A split on `TRANS_DATE` itself is
  not applied (the trade is already post-split).
- **Differ by more than 25%** means `|filed price ÷ reference close − 1| > 0.25`. Exactly 25% passes.
- If the stock has no bar on or before `TRANS_DATE`, the check cannot run: the buy stays priced and
  is marked `filing_price_check = not_checkable`.
- Missing split data for a symbol is a halting failure, not a pass.

---

## Rule 10 — instrument type in scope; Rule 8 denominator (registered 2026-11-13)

Set by Gomathy S. on 2026-11-13, **before any returns were viewed**. State at registration:
`data/verified/enriched_buys.csv` (SHA-256 `fa146273…5bde`) holds per-buy returns computed by
ENRICH on 2026-11-09; no return, average or other return statistic had been viewed, summarized or
reported. Only counts, price-status and coverage figures had been seen. The scope was decided by
instrument type (owner's decisions of 2026-11-12 and 2026-11-13, `logs/RUN_LOG.md`), not by coverage.

| Rule | Applies to | Treatment |
|---|---|---|
| **10 — instrument type** | every verified buy | classified from `SECURITY_TITLE` by `share_types.py` (SHA-256 `551a5ca6…31de44` at registration). **In scope:** reasons `common`, `ordinary`, `beneficial_interest`, `lp_common_units`, `depositary_common`, `share_equivalent_named`. **Everything else is out of scope.** Out-of-scope buys stay in `data/verified/` with their reason and are **excluded from clustering, scoring and coverage** |
| **8 (denominator)** | ENRICH, gate G3 | the 80% minimum is measured **over in-scope buys**: priced in-scope buys ÷ in-scope buys. "Priced" = `price_status = priced` |

**Both coverage figures (over all buys and over in-scope buys) were seen before this denominator
was chosen. Every report must show both.**

Figures seen (Rule 10 as registered, `data/raw/share_types/share_types-audit.md`):

| | Priced | Of | Coverage |
|---|---|---|---|
| Over all buys | 61,969 | 78,495 | 78.95% |
| Over in-scope buys | 61,969 | 75,638 | 81.93% |

By quarter, over all buys / over in-scope buys: 2023 Q2 70.49 / 73.78 · Q3 74.17 / 76.24 ·
Q4 72.71 / 75.40 · 2024 Q1 75.32 / 77.46 · Q2 76.76 / 79.07 · Q3 78.19 / 80.13 · Q4 78.31 / 80.13 ·
2025 Q1 79.13 / 81.55 · Q2 83.37 / 84.99 · Q3 85.30 / 88.71 · Q4 86.45 / 89.60 · 2026 Q1 85.03 / 88.50 ·
Q2 85.10 / 90.22 · Q3 81.31 / 88.75 (%).

How Rule 10 is applied:

- The title is upper-cased and whitespace-collapsed; the first rule in `share_types.RULES` that
  matches gives the reason. Out-of-scope instruments are tested first (warrants, debt, options,
  rights, depositary for preferred, preferred, convertible, foreign-exchange suffix), so a warrant
  or right on common stock, or `COMMON SHARES (2330.TW)`, is out.
- Owner decisions folded in: depositary shares with an unstated underlying are out; units that
  are not LP common units are out; fund share classes (Class I, Z, Advisor, A1/A2/A3 …) are out;
  titles naming only a company or person are out (`unclassifiable`); ADS / ADR without a stated
  underlying are in (`depositary_common`); SUBORDINATE VOTING SHARES, REGISTERED SHARES and titles
  ending in STOCK are in (`share_equivalent_named`); convertible securities are out.
- Counts at registration: in scope 75,638, out of scope 2,857.
- Any change to `share_types.RULES` changes Rule 10 and must be logged under Amendments.

---

## Rule 11 — reporting periods (registered 2026-11-13)

Set by Gomathy S. on 2026-11-13, **before any returns were viewed** (same state as Rule 10).

| Rule | Applies to | Treatment |
|---|---|---|
| **11 — periods** | the backtest and every report of its results | **The backtest reports results for 2023 Q2 – 2024 Q2 (in-scope coverage below 80%) separately from 2024 Q3 – 2026 Q3, as well as combined.** |

Quarter is `source_quarter` (the data-set quarter of the filing). At registration, in-scope
coverage is below 80% in each quarter 2023 Q2 – 2024 Q2 and at or above 80% in each quarter
2024 Q3 – 2026 Q3 (table under Rule 10).

---

## Not yet registered

These must be registered here before ENRICH outcomes or SIGNALS labels are computed. The
recipe's current values are proposals only and are **not** registered:

- Role weights and title → role mapping (TODO 7)
- Size buckets and whether relative size is used (TODO 8)
- T_strong (TODO 9)
- The cluster definition (≥ 2 distinct `RPTOWNERCIK`, 30-day `FILING_DATE` window) and the
  STRONG / WATCH / SKIP conditions, which are written in the recipe but have not yet been
  registered here

---

## Amendments

- **2026-11-13 · Rule 8 denominator · "80% of verified buys" → "80% of in-scope buys" (Rule 10).**
  Reason: buys of instruments other than common-equivalent shares (preferred, debt, warrants,
  foreign listings, unclassifiable titles) are not what the study measures, so they should not
  count for or against coverage. Computed when it changed: per-buy returns (not viewed), price
  status and coverage counts; both coverage figures (78.95% over all buys, 81.93% over in-scope)
  were seen before the denominator was chosen. Decided by Gomathy S.

Format for each one: date · rule changed · old → new · reason · what had been computed
when it changed · who decided.
