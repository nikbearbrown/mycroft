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

## Not yet registered

These must be registered here before ENRICH outcomes or SIGNALS labels are computed. The
recipe's current values are proposals only and are **not** registered:

- Return window N and at most one secondary window (recipe TODO 4)
- Minimum price coverage for G3 (TODO 5)
- Role weights and title → role mapping (TODO 7)
- Size buckets and whether relative size is used (TODO 8)
- T_strong (TODO 9)
- The cluster definition (≥ 2 distinct `RPTOWNERCIK`, 30-day `FILING_DATE` window) and the
  STRONG / WATCH / SKIP conditions, which are written in the recipe but have not yet been
  registered here

---

## Amendments

None.

Format for each one: date · rule changed · old → new · reason · what had been computed
when it changed · who decided.
