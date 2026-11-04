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

**Not decided by Rule 1:** how `is_10b5_1 = unknown` is treated for STRONG. In 2026 Q3 no
qualifying buy is unknown. This must be registered before SIGNALS runs on any quarter that
has unknown buys.

---

## Not yet registered

These must be registered here before ENRICH outcomes or SIGNALS labels are computed. The
recipe's current values are proposals only and are **not** registered:

- Return window N and at most one secondary window (recipe TODO 4)
- Minimum price coverage for G3 (TODO 5)
- Joint-filing rule for clusters (TODO 6)
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
