# Context: Form D, N-CSR and the exposure map

Week 9 adds two sources beside the N-PORT marks panel. Neither of them produces a price, and neither can produce a valuation; both answer questions the marks panel structurally cannot.

| Source | Answers | Cannot answer |
|---|---|---|
| N-PORT (weeks 1–8) | what a position is worth on a period end | when it was bought, what was paid |
| **N-CSR / N-CSRS** footnote (Reg S-X 12-12) | acquisition date, and cost where the filer gives it per position | anything about the company as a whole |
| **Form D** | when an offering was made and how much was sold | any price — it carries no share count |

---

## 1. Form D: why a name join would have been wrong

The scan covers **49 quarters**, `2014q1` → `2026q1`, and returns **706 issuer rows** whose entity name matches a universe pattern, filed between 2014-01-22 and 2026-03-31.

**595 of those 706 rows are pooled investment vehicles.** Not a near-miss, not a long tail: the overwhelming majority. "Anthropic Jan 2026 a Series of CGF2021 LLC", "SpaceX Tender Dec 2025 a Series of CGF2021 LLC", "HII Cerebras V, a Series of HII Cerebras, LLC" — feeder vehicles raising money from accredited investors to buy existing shares on the secondary market. Their `TOTALAMOUNTSOLD` is the feeder's raise and has nothing to do with a round by the company.

Summing them per company and labelling the result "round timing and amounts" would have produced a clean-looking table of numbers that no universe company's filing ever produced. That is the P3 failure with a plausible chart attached.

So the classification uses the **filer's own declaration** — the offering's `ISPOOLEDINVESTMENTFUNDTYPE` flag — rather than an inference from the name. A filed fact, not a guess.

That leaves **111 rows across 3 distinct CIKs** for a human, and the machine stops there. The reason it has to stop is in `docs/identity_queue.md`; three examples:

- **`x.ai, inc.` (CIK 1609052)** normalises to exactly the same string as **`X.AI CORP.` (CIK 2002695)**. One is a Delaware company in New York that filed four Form Ds between 2014 and 2017; the other is a Nevada company in Palo Alto that started filing in 2023. No amount of string work separates them.
- **`Community Philanthropic Ventures, LLC`** matches `%ANTHROPIC%`, because *phil-anthropic* contains it.
- **`Gaingels Databricks 2024 LLC`** is a feeder with no pooling token in its name and no pooled-fund flag set. A rule wide enough to catch it would catch operating companies that file as LLCs.

**Affirmed identities:**

| Company | CIK | Filed as |
|---|---|---|
| Databricks, Inc. | `0001587468` | Databricks, Inc. |
| Figure AI Inc. | `0002014185` | Figure AI Inc. |
| Groq, Inc. | `0001686725` | Groq, Inc. |
| Perplexity AI, Inc. | `0001972171` | Perplexity AI, Inc. |
| Space Exploration Technologies Corp. | `0001181412` | SPACE EXPLORATION TECHNOLOGIES CORP |
| X.AI Corp | `0002079267` | X.AI Holdings Corp. |
| X.AI Corp | `0002002695` | X.AI CORP. |

> **Archive note.** 2008Q2-2013Q4 are not published by the SEC; 2008Q1 and 2012Q1 exist as orphans and are deliberately excluded so that the earliest observed filing is a property of a contiguous archive rather than of which orphan a company happened to appear in.

### What the archive says about the largest issuers

**Anthropic, OpenAI, Anduril and Cerebras have filed no Form D under their own identity** anywhere in the published archive. Every hit on their names is a vehicle. Cerebras has an EDGAR filer record, but it was created by the S-1 registration path — its first filing is a DRS in June 2024, and there is no `D` among them.

Two explanations fit and this project cannot distinguish them from filings alone: either those rounds relied on the statutory Section 4(a)(2) private-placement exemption, which requires no Form D, or they were filed in a form or quarter the archive does not carry. The observation is reported; the cause is not.

---

## 2. N-CSR: the entry dates N-PORT does not have

**60 filings** fetched across **30 registrants** (1.17 GB), of which **58** disclose restricted securities and **31** yielded a universe lot.

There is no bulk data set for N-CSR and no prescribed layout — Reg S-X names the required contents, not the columns. Five filers write it five ways, so the parser maps columns by reading the **header** rather than by knowing the filer. A sixth filer with a labelled header works without a code change.

| Filer | Layout |
|---|---|
| Baron | table · Name of Issuer, Acquisition Date(s), Value · cost given once **per fund** |
| Fidelity | table · Security, Acquisition Date, Acquisition Cost ($) |
| Lincoln | table · Investment, Date of Acquisition, Cost, Value |
| Neuberger | table · + Value and Percentage of Net Assets |
| **BlackRock** | **no table** · `(Acquired 10/22/19, cost $3,030,010)` inline in the Schedule of Investments line item |

| Company | Lots | Registrants | Position cost | Date ranges | Earliest entry | Latest entry |
|---|---|---|---|---|---|---|
| Databricks, Inc. | 74 | 13 | 74 | 0 | 2019-10-22 | 2025-12-18 |
| Space Exploration Technologies Corp. | 52 | 12 | 36 | 24 | 2015-01-20 | 2026-02-02 |
| Anduril Industries, Inc. | 49 | 5 | 49 | 0 | 2024-08-07 | 2026-05-12 |
| Anthropic PBC | 39 | 9 | 39 | 1 | 2025-08-18 | 2026-05-28 |
| OpenAI Group PBC | 20 | 6 | 20 | 0 | 2024-09-30 | 2026-03-31 |
| X.AI Corp | 10 | 5 | 4 | 0 | 2021-10-27 | 2025-12-19 |
| Cerebras Systems Inc. | 5 | 3 | 5 | 0 | 2025-09-19 | 2026-01-30 |

Two properties of the filed format are carried as columns rather than flattened away:

- **Acquisition dates are often ranges.** Baron files `11/15/2017-8/4/2020` for a SpaceX preferred position built across three years. Both ends are stored; collapsing to one would invent a precision the filing does not have.
- **Cost is not always per position.** Baron reports one cost for all restricted securities in a fund and says so — "See Portfolios of Investments for cost of individual securities". `cost_basis_scope` records `position`, `fund_total` or `absent`, so a fund total is never read as an entry price.

---

## 3. The exposure map

One row per (manager, company) at the latest period end that manager reported, with how long they have held it. `max_pct_net_assets` is the filer's own figure from N-PORT, not value divided by a net-asset number this project computed.

| Company | Manager | As of | Positions | Value | Max % of net assets | First held | Periods |
|---|---|---|---|---|---|---|---|
| Anduril Industries, Inc. | Fidelity | 2026-04-30 | 23 | $227.9m | 0.25% | 2024-08-31 | 21 |
| Anduril Industries, Inc. | Franklin Templeton | 2026-04-30 | 4 | $49.1m | 0.81% | 2024-09-30 | 14 |
| Anduril Industries, Inc. | BlackRock | 2026-04-30 | 4 | $33.7m | 0.12% | 2024-09-30 | 14 |
| Anduril Industries, Inc. | StepStone | 2026-03-31 | 3 | $28.1m | 0.27% | 2024-06-30 | 8 |
| Anduril Industries, Inc. | Fundrise | 2026-03-31 | 1 | $7.4m | 1.08% | 2026-03-31 | 1 |
| Anduril Industries, Inc. | T. Rowe Price | 2026-04-30 | 3 | $7.2m | 0.06% | 2025-04-30 | 9 |
| Anduril Industries, Inc. | Coatue | 2026-03-31 | 1 | $2.4m | 0.05% | 2025-09-30 | 3 |
| Anduril Industries, Inc. | Neuberger Berman | 2026-04-30 | 1 | $1.2m | 0.09% | 2026-04-30 | 1 |
| Anthropic PBC | Coatue | 2026-03-31 | 1 | $479.8m | 5.18% | 2025-09-30 | 3 |
| Anthropic PBC | Fidelity | 2026-04-30 | 18 | $468.1m | 0.35% | 2024-03-31 | 26 |
| Anthropic PBC | Capital Group | 2026-03-31 | 3 | $384.4m | 0.39% | 2025-09-30 | 5 |
| Anthropic PBC | Destiny Tech100 | 2026-03-31 | 1 | $134.1m | 17.92% | 2026-03-31 | 1 |
| Anthropic PBC | BlackRock | 2026-04-30 | 3 | $100.5m | 0.44% | 2025-09-30 | 8 |
| Anthropic PBC | New York Life | 2026-04-30 | 2 | $74.3m | 0.31% | 2025-09-30 | 6 |
| Anthropic PBC | Alger | 2026-04-30 | 8 | $65.2m | 2.23% | 2026-04-30 | 1 |
| Anthropic PBC | JPMorgan | 2026-03-31 | 1 | $60.7m | 0.30% | 2025-09-30 | 3 |
| Anthropic PBC | Franklin Templeton | 2026-04-30 | 3 | $47.9m | 0.78% | 2025-10-31 | 3 |
| Anthropic PBC | T. Rowe Price | 2026-04-30 | 2 | $34.8m | 0.35% | 2025-09-30 | 6 |
| Anthropic PBC | ARK | 2026-04-30 | 1 | $23.1m | 2.68% | 2023-04-28 | 13 |
| Anthropic PBC | Nuveen | 2026-04-30 | 2 | $6.6m | 0.40% | 2025-10-31 | 3 |
| Cerebras Systems Inc. | Fidelity | 2026-04-30 | 6 | $167.8m | 0.12% | 2025-09-30 | 8 |
| Cerebras Systems Inc. | Private Shares Fund | 2026-03-31 | 1 | $22.1m | 1.91% | 2022-12-31 | 14 |
| Cerebras Systems Inc. | StepStone | 2026-03-31 | 1 | $17.4m | 0.27% | 2026-03-31 | 1 |
| Databricks, Inc. | Capital Group | 2026-02-28 | 4 | $757.4m | 0.37% | 2025-02-28 | 5 |
| Databricks, Inc. | Morgan Stanley | 2026-03-31 | 7 | $396.3m | 7.60% | 2022-12-31 | 14 |
| Databricks, Inc. | Alger | 2026-04-30 | 16 | $257.6m | 2.94% | 2024-12-31 | 13 |
| Databricks, Inc. | Coatue | 2026-03-31 | 2 | $232.3m | 3.11% | 2025-09-30 | 3 |
| Databricks, Inc. | Fidelity | 2026-04-30 | 18 | $231.1m | 0.12% | 2022-11-30 | 42 |
| Databricks, Inc. | Franklin Templeton | 2026-04-30 | 5 | $205.2m | 1.44% | 2022-12-31 | 30 |
| Databricks, Inc. | BlackRock | 2026-04-30 | 2 | $176.6m | 0.81% | 2022-11-30 | 42 |
| Databricks, Inc. | AMCAP Fund | 2026-02-28 | 1 | $156.3m | 0.17% | 2026-02-28 | 1 |
| Databricks, Inc. | StepStone | 2026-03-31 | 3 | $128.5m | 1.59% | 2025-12-31 | 2 |
| Databricks, Inc. | Brighthouse | 2026-03-31 | 8 | $122.3m | 3.51% | 2022-12-31 | 14 |
| Databricks, Inc. | T. Rowe Price | 2026-04-30 | 9 | $113.7m | 0.72% | 2025-01-31 | 16 |
| Databricks, Inc. | Robinhood Ventures Fund I | 2026-03-31 | 2 | $81.7m | 7.63% | 2026-03-31 | 1 |
| Databricks, Inc. | JPMorgan | 2026-03-31 | 2 | $55.5m | 0.18% | 2025-09-30 | 3 |
| Databricks, Inc. | Lincoln Financial | 2026-03-31 | 10 | $44.2m | 0.90% | 2022-12-31 | 14 |
| Databricks, Inc. | New York Life | 2026-04-30 | 1 | $37.4m | 0.30% | 2025-03-31 | 7 |
| Databricks, Inc. | Private Shares Fund | 2026-03-31 | 1 | $34.7m | 2.99% | 2022-12-31 | 14 |
| Databricks, Inc. | VALIC Co I | 2026-02-28 | 1 | $29.2m | 1.65% | 2022-11-30 | 12 |
| … | _50 more rows in `docs/_context.json`_ | | | | | | |

---

## 4. The two sources agree, and neither cites the other

This is what joining them was for. The issuer files Form D because it sold securities; the fund files N-CSR because it owns them. Neither references the other, so agreement between the two is evidence rather than arithmetic.

**10 of 18 fund acquisition dates fall on the exact day an issuer reported a first sale** (56%), and 11 of 18 fall within a week.

| Company | Acquired | Funds | Days to nearest filed round |
|---|---|---|---|
| Databricks, Inc. | 2021-02-01 | 8 | 0 |
| Databricks, Inc. | 2019-10-22 | 5 | 0 |
| Databricks, Inc. | 2021-08-31 | 5 | 0 |
| Databricks, Inc. | 2025-09-08 | 3 | 0 |
| X.AI Corp | 2024-11-22 | 3 | 0 |
| Databricks, Inc. | 2023-09-14 | 1 | 0 |
| Databricks, Inc. | 2024-12-17 | 1 | 0 |
| Space Exploration Technologies Corp. | 2020-08-04 | 1 | 0 |
| Space Exploration Technologies Corp. | 2021-02-16 | 1 | 0 |
| X.AI Corp | 2025-12-19 | 1 | 0 |
| Databricks, Inc. | 2021-09-01 | 1 | 1 |
| X.AI Corp | 2024-06-11 | 2 | 32 |
| Space Exploration Technologies Corp. | 2017-09-11 | 1 | 47 |
| Space Exploration Technologies Corp. | 2017-09-13 | 1 | 49 |
| Databricks, Inc. | 2025-03-12 | 1 | 76 |
| Databricks, Inc. | 2020-08-28 | 1 | 157 |
| Databricks, Inc. | 2020-07-24 | 1 | 192 |
| Databricks, Inc. | 2024-06-03 | 1 | 197 |

**The denominator is the method.** Only acquisitions *inside* a company's Form D filing window are counted. SpaceX stopped filing Form D in July 2022 and 9 of its 13 single-date acquisitions come after that; measured against the nearest round they give gaps of 873, 911, 1090 and 1293 days, and every one of those numbers is the distance to the end of the archive rather than anything about when a fund bought. Left in, a real 56% agreement reads as 33%.

Date ranges are excluded for the same reason: a position built across three years has no single acquisition date, and picking an endpoint would manufacture either the match or the miss.

| Company | Form D window | Single dates outside it |
|---|---|---|
| Databricks, Inc. | 2013-09-11 → 2025-12-16 | 1 of 12 |
| Figure AI Inc. | 2024-02-27 → 2024-02-27 | 0 of 0 |
| Groq, Inc. | 2016-10-06 → 2018-08-28 | 0 of 0 |
| Perplexity AI, Inc. | 2023-03-21 → 2023-03-21 | 0 of 0 |
| Space Exploration Technologies Corp. | 2015-01-20 → 2022-07-20 | 9 of 13 |
| X.AI Corp | 2023-11-29 → 2025-12-19 | 2 of 5 |

> **What this is not.** Agreement is evidence, not proof of causation: a fund buying on the day an issuer reports first sale is consistent with participating in that round, and also with a secondary purchase that happened to settle the same day. What it is not is circular -- neither filing cites the other.

---

## 5. Timelines for the top three by coverage

### Databricks, Inc.

- **N-PORT:** 51 period ends, 2022-11-30 → 2026-04-30.
- **N-CSR:** 74 restricted lots, 74 with a position-level cost; earliest acquisition 2019-10-22.
- **Form D:** 17 filings — dates and amounts only. Form D carries no share count and no price, so no valuation is derivable from it

| Registrant | Fund | Reported | Acquired | Cost | Scope | Value | Cost→value |
|---|---|---|---|---|---|---|---|
| BLACKROCK GLOBAL ALLOCATION FUND | — | 2026-04-30 (N-CSR) | 10/22/19 | $11.8m | `position` | — | — |
| BlackRock Series Fund, Inc. | — | 2026-06-30 (N-CSRS) | 10/22/19 | $88.4k | `position` | — | — |
| BlackRock Series Fund, Inc. | — | 2025-12-31 (N-CSR) | 10/22/19 | $88.4k | `position` | — | — |
| BlackRock Variable Series Funds, | — | 2025-12-31 (N-CSR) | 10/22/19 | $3.0m | `position` | — | — |
| BlackRock Variable Series Funds, | — | 2026-06-30 (N-CSRS) | 10/22/19 | $3.0m | `position` | — | — |
| LINCOLN VARIABLE INSURANCE PRODU | — | 2025-12-31 (N-CSR) | 10/22/2019 | $885.9k | `position` | $11.8m | 13.27× |
| LINCOLN VARIABLE INSURANCE PRODU | — | 2026-06-30 (N-CSRS) | 10/22/2019 | $885.9k | `position` | $13.8m | 15.56× |
| SEASONS SERIES TRUST | — | 2025-09-30 (N-CSRS) | 10/22/19 | $5.0k | `position` | $72.2k | 14.32× |
| LINCOLN VARIABLE INSURANCE PRODU | — | 2026-06-30 (N-CSRS) | 7/24/2020 | $466.4k | `position` | $6.5m | 13.91× |
| LINCOLN VARIABLE INSURANCE PRODU | — | 2025-12-31 (N-CSR) | 7/24/2020 | $466.4k | `position` | $5.5m | 11.87× |
| … | _64 more_ | | | | | | |

### Space Exploration Technologies Corp.

- **N-PORT:** 46 period ends, 2022-11-30 → 2026-04-30.
- **N-CSR:** 52 restricted lots, 36 with a position-level cost; earliest acquisition 2015-01-20.
- **Form D:** 19 filings — dates and amounts only. Form D carries no share count and no price, so no valuation is derivable from it

| Registrant | Fund | Reported | Acquired | Cost | Scope | Value | Cost→value |
|---|---|---|---|---|---|---|---|
| FIDELITY SECURITIES FUND | — | 2026-01-31 (N-CSRS) | 1/20/2015 - 7/14/2025 | $40.4m | `position` | — | — |
| FIDELITY MT VERNON STREET TRUST | — | 2025-11-30 (N-CSR) | 4/8/2016 - 4/6/2017 | $4.6m | `position` | — | — |
| FIDELITY MT VERNON STREET TRUST | — | 2026-05-31 (N-CSRS) | 4/8/2016 - 4/6/2017 | $4.6m | `position` | — | — |
| FIDELITY PURITAN TRUST | — | 2026-02-28 (N-CSRS) | 8/4/2017 - 10/25/2022 | $29.8m | `position` | — | — |
| FIDELITY PURITAN TRUST | — | 2026-02-28 (N-CSRS) | 9/11/2017 | $756.9k | `position` | — | — |
| FIDELITY SECURITIES FUND | — | 2026-01-31 (N-CSRS) | 9/11/2017 - 7/14/2025 | $15.6m | `position` | — | — |
| BARON SELECT FUNDS | Baron Partners Fund | 2025-12-31 (N-CSR) | 9/13/2017 | — | `fund_total` | $1.1bn | — |
| BARON SELECT FUNDS | Baron Partners Fund | 2026-06-30 (N-CSRS) | 9/13/2017-8/4/2020 | — | `fund_total` | $6.2bn | — |
| BARON SELECT FUNDS | Baron Partners Fund | 2026-06-30 (N-CSRS) | 9/13/2017-10/17/2025 | — | `fund_total` | $1.3bn | — |
| BARON SELECT FUNDS | Baron Partners Fund | 2025-12-31 (N-CSR) | 9/13/2017-10/17/2025 | — | `fund_total` | $434.5m | — |
| … | _42 more_ | | | | | | |

### Anduril Industries, Inc.

- **N-PORT:** 22 period ends, 2024-06-30 → 2026-04-30.
- **N-CSR:** 49 restricted lots, 49 with a position-level cost; earliest acquisition 2024-08-07.
- **Form D:** 0 filings — empty until a named human affirms an operating-company CIK for this company; a name join would attribute SPV raises to the company

| Registrant | Fund | Reported | Acquired | Cost | Scope | Value | Cost→value |
|---|---|---|---|---|---|---|---|
| FIDELITY MT VERNON STREET TRUST | — | 2025-11-30 (N-CSR) | 8/7/2024 | $32.0k | `position` | — | — |
| FIDELITY MT VERNON STREET TRUST | — | 2026-05-31 (N-CSRS) | 8/7/2024 | $32.0k | `position` | — | — |
| FIDELITY SECURITIES FUND | — | 2026-07-31 (N-CSR) | 8/7/2024 | $2.6m | `position` | — | — |
| FIDELITY SECURITIES FUND | — | 2026-07-31 (N-CSR) | 8/7/2024 | $32.1m | `position` | — | — |
| FIDELITY SECURITIES FUND | — | 2026-01-31 (N-CSRS) | 8/7/2024 | $2.6m | `position` | — | — |
| FIDELITY SECURITIES FUND | — | 2026-01-31 (N-CSRS) | 8/7/2024 | $32.1m | `position` | — | — |
| VARIABLE INSURANCE PRODUCTS FUND | — | 2026-06-30 (N-CSRS) | 8/7/2024 | $114.2k | `position` | — | — |
| VARIABLE INSURANCE PRODUCTS FUND | — | 2025-12-31 (N-CSR) | 8/7/2024 | $114.2k | `position` | — | — |
| FIDELITY MT VERNON STREET TRUST | — | 2025-11-30 (N-CSR) | 4/17/2025 | $1.3m | `position` | — | — |
| FIDELITY MT VERNON STREET TRUST | — | 2025-11-30 (N-CSR) | 4/17/2025 | $8.7k | `position` | — | — |
| … | _39 more_ | | | | | | |

---

## What none of this computes

1. A return from N-CSR cost against an N-PORT price. The cost is for a position whose share count may have changed -- Week 7 confirmed seven splits and blocked 301 marks. Where a single filed row carries both cost and value, cost_to_value is reported instead.
2. Any company-level valuation. Neither source carries shares outstanding, so there is no arithmetic from these tables to a company value.
3. A per-share price from Form D. Form D reports dollars offered and dollars sold, and no share count at all.

The first one is the tempting one. Holding an entry cost and a current mark, dividing them looks like a return — and it is not, because the cost belongs to a number of shares that may have changed since. Week 7 confirmed seven splits and blocked 301 marks for exactly that reason. Where one filed row carries both a position cost and a position value, that ratio is reported as `cost→value`, because it is a comparison the filer made.
