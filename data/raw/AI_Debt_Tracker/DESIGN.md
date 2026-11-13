# AI Debt Tracker — Design Document

**A multi-agent system that keeps an always-up-to-date list of every bond and loan the AI build-out
is being financed with — who owes what, at what interest rate, and when it falls due — built from
SEC announcements as they happen, graded against each company's next official report, and run
entirely on a laptop GPU for $0.**

*Written 16 October 2026 for Mycroft ("Using AI to Invest in AI"). Every data number below was
checked against the live source on 16 October 2026; the probe scripts are in `scripts/`.*

---

# 0. Summary

| | |
|---|---|
| **What it does** | Reads every debt-related SEC filing from ~25 AI-sector companies as it appears, keeps a ledger of each bond and loan, and turns it into investment signals: how much the AI sector is borrowing, how fast, at what cost, and how much falls due soon. |
| **Who it helps** | Investors and analysts asking whether the AI build-out is sustainable; bond investors; the Mycroft coordination layer, which has no debt or credit signal today. |
| **Answer key** | The answer is published later: each company's next quarterly/annual report tags its debt in machine-readable form (XBRL). The agent only sees filings from *before* that report. |
| **Data** | All free from SEC EDGAR. 25 AI-sector companies filed **70** "new debt" 8-Ks, **123** "material agreement" 8-Ks, **130** bond prospectus supplements and **63** final term sheets between Jan 2025 and Sep 2026, plus **173** quarterly/annual reports to grade against. |
| **Models** | Local only, via Ollama on an RTX 4070 Laptop GPU (8 GB). Main pick: `qwen3:8b`; fast pick: `qwen3:4b`. |
| **Stack** | Python, LangGraph (agent workflow), MCP (tools), Ollama (models), Arelle / SEC bulk data (answer key). |
| **Time** | 10 weeks, one student, ~15–20 hours/week. |
| **Headline result** | "From announcements alone, the tracker reproduced X% of the bonds in companies' next official reports, Y points better than carrying last quarter forward, and published a quarterly AI-sector debt signal." |

---

# 1. The problem, in plain words

## Why debt matters for AI investing

Building AI takes data centres, chips and power plants, and that costs hundreds of billions of
dollars. A growing share of it is paid for with **borrowed money**:

- The five biggest cloud companies (Amazon, Alphabet, Meta, Microsoft, Oracle) sold **$121 billion**
  of US bonds in 2025, against an average of **$28 billion a year** in 2020–2024 (Bank of America
  data, reported by Reuters).
- AI-related investment-grade bonds reached **$218 billion by 8 July 2026** — already more than all
  of 2025 — and Morningstar reports signs of investor "indigestion".
- Smaller "neocloud" companies that rent out AI computing power (CoreWeave, Applied Digital, Cipher
  Mining, TeraWulf…) borrow heavily against their data centres and chip contracts.

Borrowing is not bad in itself, but it changes the risk. A company that funds AI from cash can slow
down; a company that funds it with debt **must** keep paying interest and must repay or refinance
each bond when it falls due. So investors want to know, at any moment: *how much does each AI
company owe, at what interest rate, and how much of it falls due in the next year or two?*

## Why that's hard to know today

A **bond** is an IOU sold to investors: a fixed amount (the *principal*), an *interest rate*
(the *coupon*), and a repayment date (the *maturity*). Companies also borrow through **loans**
from banks, sometimes as a *facility* they can draw on over time.

The official picture only arrives every three months, in the debt note of the quarterly report.
In between, a company might sell new bonds, pay old ones off early, buy some back, or sign a new
loan — and each of those is announced separately, in different kinds of filings:

| What happened | Where it's announced |
|---|---|
| A big company sells bonds through its pre-registered "shelf" | A prospectus supplement (form `424B2`/`424B5`) and a final term sheet (form `FWP`) |
| A smaller company sells bonds privately (to institutions only) | An 8-K with a press release, later the bond contract (the *indenture*) as an exhibit |
| A new loan or credit facility | An 8-K, item 2.03 ("creation of a direct financial obligation") and/or 1.01 ("material definitive agreement") |
| Early repayment, buy-back (*tender offer*), swap of old bonds for new | 8-Ks and press releases, often in several steps (launch, results, settlement) |
| A bond simply reaching its due date | Nothing — it just disappears |

Anyone wanting the current picture pieces it together by hand or buys it from a data vendor.

## What the AI Debt Tracker does

1. Watches the SEC filings of an AI-sector universe and picks out the debt-related ones.
2. **Reads each announcement** and extracts the bond or loan: principal, interest rate, maturity,
   currency, and when it takes effect — with a citation to the exact sentence it came from.
3. **Keeps a ledger** per company, applying new bonds, repayments and due dates in date order.
4. **Checks itself** for contradictions (a repayment of a bond it has never seen, tranche amounts
   that don't add up to the stated total) and goes looking for the missing document.
5. Publishes **signals** for Mycroft: total debt, new borrowing this quarter, the *maturity wall*
   (how much falls due in the next 12/24 months), average interest rate, and a sector-wide "AI
   debt index".

## How it fits Mycroft

Mycroft's existing ~99 recipes cover news, sentiment, talent, patents, funding news, SEC filings,
earnings calls and portfolios. **None tracks debt or credit.** Like the Private AI Valuation Agent
added the private-market view, this adds the balance-sheet view of the AI build-out — and it
follows the same rules: verified data, every number traceable to a filing, model judgments
labelled as judgments, and a human gate before anything enters `data/verified/`.

---

# 2. What "done" looks like (deliverables at week 10)

1. A ledger for every universe company, rebuilt for every quarter from Q3 2024 to Q2 2026, plus a
   **live mode** that updates it the day a new filing appears.
2. Five MCP servers (Section 6) and a LangGraph supervisor with parallel readers (Section 7).
3. A frozen, documented evaluation: AI universe + a broader generalisation set, with baselines and
   ablations and confidence intervals.
4. A versioned **signal contract** (`schema_version 1.0`) and a quarterly human-readable note.
5. A read-only MCP server so other Mycroft agents and AI assistants can query the debt data.
6. Documents in the shape the Private AI Valuation Agent used: `proposal.md`,
   `system_architecture.md`, `data_architecture.md`, `findings.md`, `docs/demo.md`, worklog.

---

# 3. Data

## 3.1 What to get, and from where

Everything is free, public, and needs no API key — only a `User-Agent` header with a real name and
email (the SEC's one rule).

| # | What | Source | Used for |
|---|---|---|---|
| D1 | **Filing timeline per company**, including the item codes of each 8-K | `https://data.sec.gov/submissions/CIK{10-digit}.json` (fields `form`, `filingDate`, `acceptanceDateTime`, `items`, `accessionNumber`, `primaryDocument`) | Finding candidate documents; the point-in-time cut-off |
| D2 | **The documents and their exhibits** | `https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/index.json` → 8-K body, `EX-99.1` press releases, `EX-4.x` indentures / supplemental indentures / note forms, `EX-10.x` credit agreements, `424B2`/`424B5` prospectus supplements, `FWP` final term sheets | **System input** |
| D3 | **The starting point**: the debt note in the company's last quarterly/annual report | The 10-Q/10-K for the *previous* quarter (allowed — it's already public) | The agent's opening ledger |
| D4 | **The answer key**: every debt fact in the *next* report, including notes and per-bond detail | SEC **Financial Statement and Notes Data Sets**, monthly: `https://www.sec.gov/files/dera/data/financial-statement-notes-data-sets/{yyyy}_{mm}_notes.zip` (≈53 MB zipped; `sub`, `num`, `dim`, `txt`, `pre`, `cal`, `tag` tables) | **Grading only — never shown to agents** |
| D5 | (Fallback answer key) the filing's own XBRL | Arelle on the 10-Q/10-K (already set up in `ledgerlint` and used by the Private AI Valuation Agent) | Filings missing from D4; spot checks |
| D6 | **Company-level totals** | `https://data.sec.gov/api/xbrl/companyfacts/CIK{10-digit}.json` (total debt, current portion, maturity buckets, cash, capital spending) | Aggregate grading; signal inputs (debt vs. capital spending, debt due vs. cash) |
| D7 | (Optional) market interest rates | FRED (US Treasury yields) | Context for "cost of debt vs. Treasuries" in the quarterly note |
| D8 | (Optional) bond identifiers | OpenFIGI (CUSIP → bond description) | Tie-breaking when two bonds look alike |

**Not used:** the smaller SEC *Financial Statement Data Sets* (the quarterly files SpreadCheck uses)
only cover the face of the financial statements, **not the notes**, so they contain none of the
per-bond detail. This was confirmed on 2025 Q1: zero bond-level facts for 17 AI companies.

**What the answer-key tables contain** (checked on `2026_08_notes.zip`):

- `num.tsv`: `adsh` (filing), `tag`, `ddate` (date), `qtrs`, `uom` (currency), `dimh` (link to the
  dimensions), `value`, `dcml` (rounding precision).
- `dim.tsv`: `dimhash` → `segments`, e.g. `DebtInstrument=ConvertibleNotes2030;LongtermDebtType=ConvertibleDebt;`
- `txt.tsv`: text and date facts.
- Example rows found: Cipher Mining's 10-Q (June 2026) tags 5 face amounts and 5 interest rates per
  instrument; CoreWeave's tags 6 face amounts, 12 rates and 25 carrying amounts, including each
  delayed-draw loan facility; TeraWulf's tags 8 face amounts.

## 3.2 The AI universe (draft — frozen in week 1)

Twenty-five companies in five groups. CIKs were checked against EDGAR's own company names;
`docs/archive/universe_draft.json` holds the machine-readable copy.

| Group | Companies |
|---|---|
| **Hyperscalers** (the big cloud companies) | Microsoft, Alphabet, Amazon, Meta, Oracle |
| **Chips and AI hardware** | Nvidia, AMD, Broadcom, Micron, Intel, Super Micro, Dell, Marvell |
| **Data-centre landlords and neoclouds** | Equinix, Digital Realty, CoreWeave, Applied Digital, Cipher Mining (now "Cipher Digital Inc."), TeraWulf, Core Scientific |
| **Power for AI data centres** | Vistra, Constellation Energy |
| **AI software** | Salesforce, Snowflake, IBM |

**Debt-filing activity, Jan 2025 – Sep 2026** (from D1):

| | 8-K item 2.03 (new debt) | 8-K item 1.01 (agreements) | Prospectus supplements | Final term sheets | Reports to grade against |
|---|---|---|---|---|---|
| **All 25** | **70** | **123** | **130** | **63** | **173** |
| Most active | Applied Digital 8, CoreWeave 7, Cipher 7, Vistra 7 | Applied Digital 19, CoreWeave 13 | Alphabet 28, Equinix 14, Amazon 12 | Alphabet 13, Equinix 7 | — |
| Quiet | Microsoft and Snowflake: none of the above | | | | |

Two things follow: (1) the big companies announce bonds mostly through prospectus supplements and
term sheets, **not** 8-Ks, so the tracker must read all four kinds of filing; (2) quiet companies
like Microsoft are real test cases too — the right answer is "nothing changed except bonds that
reached their due date".

A **generalisation set** of ~75 non-AI companies that tag individual bonds is added in week 1, so
the evaluation isn't limited to 25 names (Section 3.5).

## 3.3 What a sample of the answer key looks like

The latest report of all 25 universe companies was checked for how finely debt is tagged (distinct
members on the debt dimensions; the counts include loan facilities and credit lines, so they are not
bond counts — hand-checked in week 1):

| How finely debt is tagged | Companies (latest 10-Q/10-K) | What can be graded |
|---|---|---|
| **Each instrument separately** — **21 of 25** | e.g. Microsoft 13, Nvidia 15, Broadcom 64, Super Micro 53, Equinix 41, Vistra 51, CoreWeave 19, Applied Digital 12, TeraWulf 11, Cipher Mining 7, Snowflake 3 (full list in `docs/archive/universe_draft.json`) | Every bond: principal, rate, maturity |
| **Each offering** (all bonds sold on one day grouped together) | Meta — 6 members like `meta:November2025DebtMember`; **Alphabet and Amazon** — many members are offerings like `A2026USDollarNotes` ($20 bn, several tranches), found in the feasibility spike (P18) | Each offering's total and maturities |
| **Totals only** | Oracle — `orcl:SeniorNotesAndOtherBorrowingsMember` | Total debt, current vs. long-term, maturity buckets |

So **grading happens at three levels** (Section 9.1), and each company's level is recorded in the
universe file.

**Week 1 measurement (supersedes the member counts above).** Counting members overstated the
detail. Reading every 10-Q/10-K from July 2024 to September 2026 with the answer-key rules, and
asking how much of total debt the itemised instruments cover (P22–P26), gives **L1 14, L2 3,
L3 8** (draft: 21 / 3 / 1). Microsoft moves to L2 (issuance groups); Meta, Intel, Dell, TeraWulf,
Vistra, Constellation and IBM to L3, mostly because their 10-Qs itemise little of their debt.
Each episode is graded at its own target report's level, so Intel's and Oracle's 10-K quarters
are still graded per bond. Evidence: [`docs/universe_v1_review.md`](docs/universe_v1_review.md);
**frozen** on 2026-10-18 (Week 1 gate, `manifests/week1_gate.json`) with two tie-break overrides
— Meta → L2 and TeraWulf → L1 — giving **L1 15, L2 4, L3 6**.

## 3.4 Problems in the data sources, and how each is solved

| # | Problem | How we know | Fix |
|---|---|---|---|
| P1 | **Big companies don't announce bonds in 8-Ks.** They use prospectus supplements and term sheets. | Alphabet: 0 item-2.03 8-Ks, but 28 prospectus supplements and 13 term sheets. | The timeline reads four document families: 8-K (items 1.01, 1.02, 2.03, 2.04, 7.01, 8.01), `424B2`/`424B5`, `FWP`, and 8-K exhibits. Triage decides which are debt-relevant. |
| P2 | **Tagging detail varies by company** (bond / offering / totals only). | Section 3.3. | Three-level grading; each company's level is stored in the universe; the headline uses bond-level companies and the others are reported separately. |
| P3 | **Bond names aren't standardised** and maturity dates are rarely tagged as dates. Members look like `Notes3.30Due2027`, `ConvertibleNotes2030`, `TermLoans`. | `txt.tsv` had 0 `DebtInstrumentMaturityDate` facts for the three companies checked. | Match bonds on a **key** of (currency, interest rate, maturity year, principal), with the maturity year parsed from member names and labels (`pre.tsv` gives the human label). The matcher is plain code; ambiguous cases go to a hand-checked alignment table built in week 2. Unmatched bonds are reported, never silently dropped. |
| P4 | **Pricing date ≠ settlement date.** Bonds priced on 28 September may only exist from 3 October. | Normal market practice. | Each event records *announced*, *priced* and *settles* dates; the ledger uses the settlement date, so a bond priced before quarter-end but settling after it is correctly absent. |
| P5 | **Face vs. carrying amount.** Reports show the principal *and* a slightly different book value (discounts, fees). | Both tags appear in `num.tsv`. | Grade principal (`DebtInstrumentFaceAmount` or the face column) where tagged; carrying amount otherwise, with a 2% tolerance, reported separately. |
| P6 | **Loan facilities that are drawn over time** (CoreWeave's delayed-draw loans show carrying amounts of 0 when undrawn). Floating rates ("SOFR + 4%"), convertible bonds. | CoreWeave row in Section 3.1. | The ledger stores *capacity* and *drawn amount* separately; floating rates stored as a formula (benchmark + margin); convertibles flagged. Draws not announced are carried from the last report and marked "unannounced". |
| P7 | **Revolving credit lines and commercial paper** go up and down without announcements. | They're short-term and routine. | Excluded from event scoring; carried at the last reported balance and labelled. Totals are graded with and without them. |
| P8 | **Foreign-currency bonds** (euro, sterling, Swiss franc tranches). | Hyperscalers issue in several currencies. | Store the original currency; compare in that currency when the answer key's `uom` isn't USD; convert only for aggregate signals, at period-end rates, labelled. |
| P9 | **Debt that never appears on the company's balance sheet**: joint ventures that borrow on the company's behalf (e.g. a data-centre JV), and data-centre leases that haven't started yet. | Widely reported for 2025–26 hyperscaler deals. | Out of scope for the graded ledger. Tracked separately as "disclosed off-balance-sheet AI financing", extracted from the notes as text and **labelled as a model judgment**. Stretch goal only. |
| P10 | **Some debt is never announced** (private placements without an 8-K, quiet loan draws). | A ceiling on any announcement-based tracker. | Measured, not hidden: bonds that appear in the next report but are explained by no document in the window are counted as **"unannounced debt"** — a finding in itself. |
| P11 | **Look-ahead leakage**: the agent must not peek at the report it's graded on. | The core rule of the evaluation. | The `edgar_pit` MCP server enforces a cut-off by `acceptanceDateTime`, refuses the target 10-Q/10-K, and logs every request. A test fails the build if the graph can reach the grader. |
| P12 | **Renames and subsidiaries.** Cipher Mining now appears as "Cipher Digital Inc."; some debt is issued by subsidiaries with their own filer IDs. | EDGAR names in the probe. | The universe maps each company to its parent ID plus known issuing subsidiaries; reviewed by hand in week 1. |
| P13 | **Amended filings** (8-K/A, 10-Q/A). | Normal. | Amendments supersede the original; the answer key always uses the latest version filed *before* the grading date. |
| P14 | **SEC rate limits.** | SEC fair-access policy: ≤ 10 requests/second, contact in User-Agent. | One shared limiter (8 req/s) and an on-disk cache in `edgar_pit`. `.env` holds `EDGAR_NAME`/`EDGAR_EMAIL`. |
| P15 | **Bulky files don't belong in git** (filing caches, monthly zips, model weights, the Python environment — several GB). | Checked. | All of them live in a local directory outside the repo, set through `.env` (`AI_DEBT_DATA`, `UV_PROJECT_ENVIRONMENT`, `OLLAMA_MODELS`; Section 14). |
| P16 | **The model may remember famous bond deals** and "fill in" details not in the document. | A risk for any LLM. | The agent never types a number (Section 7.1); every field must point to a sentence in a document. A memorisation probe asks the model about deals with no document and reports the result. |
| P17 | **The bulk notes data rounds interest rates** (6.125% stored as 0.0613 → 6.13%). | Feasibility spike: CoreWeave 9.625% stored as 9.63, Nvidia 5.625% as 5.63. | Exact rates and principals for the answer key come from the target filing's own XBRL via Arelle (D5); D4 is used to find and index facts. Matching tolerates ±0.005. |
| P18 | **Some "per-instrument" members are offerings** (several bonds sold on one day). | Spike: Alphabet `A2026USDollarNotes` ($20 bn, several tranches); Amazon `March2026SeniorUnsecuredNotes` ($37 bn). | Alphabet and Amazon graded at L2; every company's level hand-checked in week 1 and stored in the universe. |
| P19 | **Annual and quarterly reports tag debt at different detail.** | Spike: Intel 42 instruments in its 10-K → 1 in the next 10-Q; Nvidia 0 → 7; Vistra 0 → 5. | Per-episode consistency check: if the target report tags far fewer instruments than the previous one, the episode is graded at L3, and downgrades are counted and reported. |
| P20 | **Member names spell numbers in words**, with typos. | Spike: Equinix `FourPointSixZeroZeroPercent…DueTwoThousandThirty`, `ThreePointTwoFieveZero…`. | Number-word parser for member names; match on human labels from `pre.tsv` as well. |
| P21 | **Bonds priced before quarter-end but settling after** are announced before the quarter's window. | Spike: CoreWeave 9.625% 2032 notes had no announcement inside the quarter. | The event window opens ~30 days before the previous quarter-end; settlement dates decide which quarter a bond belongs to (P4). |
| P22 | **Members numbered by issuance, not by bond.** | Week 1: Microsoft's 13 members are `IssuanceOfLongTermDebtOne…Thirteen` — one issuance date each, several bonds inside ($19.8 bn in one). | Parsed as offerings; Microsoft graded at L2, not L1. |
| P23 | **Partial per-bond tagging.** A 10-Q may tag only the quarter's new bonds, so counting members overstates detail. | Week 1: Oracle's 10-Qs tag 4–14 of ~56 bonds; Intel's latest 10-Q tags 5 bonds = 13% of its debt. | A report's level is decided by **coverage**: itemised instruments must account for ≥ 80% of total debt for L1 (`eval/answer_key.grading_level`). |
| P24 | **Maturity-year buckets as members.** | Week 1: IBM tags `Maturing2027`, `Maturing2026-2028`, … — 29 buckets, no bonds. | Recognised as buckets, never as instruments; IBM graded at L3. |
| P25 | **Total debt has no single tag.** | Week 1: Oracle reports `LongTermNotesAndLoans` + `NotesPayableCurrent`; others `DebtLongtermAndShorttermCombinedAmount` or debt incl. finance leases; some 10-Qs tag none. | A fixed fallback chain; when nothing is tagged the denominator is the sum of tagged instruments and the record says coverage was not independently measured. |
| P26 | **Subtotal members beside the instruments they sum.** | Week 1: Digital Realty's $16 bn "Unsecured senior notes"; Oracle's $125 bn "Senior Notes And Other Long Term Borrowings". | A member worth ≥ 50% of total debt is an aggregate; members without a maturity never count as itemised bonds. |
| P27 | **Facts about debt after the period end** sit inside the target report (`SubsequentEventType` axis). | Week 1: CoreWeave's June 2026 10-Q has 3 such facts. | Excluded from the answer key (they describe the next quarter); counted per filing. |
| P28 | **The notes data is monthly only for the last 12 months**; older periods are quarterly files (`2025q3_notes.zip`). | Week 1: `2024_07_notes.zip` returns 404. | The extractor maps each month to the file that holds it (`eval/fsn.periods_covering`). |
| P29 | **Two clocks for "accepted".** EDGAR's submissions index and the notes data's `sub.tsv` disagree by hours for the same filing (CoreWeave's June 2026 10-Q: `2026-08-12T03:24:42Z` vs `2026-08-11 19:25`). | Week 1 smoke test of `edgar_pit`. **Week 2: the submissions index itself moved** — between 18 and 23 Oct 2026, 43 of the 495 episode targets (9 filers) shifted by 4–5 h, consistent with Eastern → UTC. | Cut-offs are **pinned to the target report** (`PointInTimeEdgar.for_episode`, `EDGAR_PIT_TARGET`): the target's acceptance time is read from the live index when the server starts, so both sides share one snapshot of one clock; manifest timestamps are for people only. On the cut-off day a filing must also be ≥ 5 h earlier than the target to be visible, so a clock mix can never let a later filing in. |
| P30 | **Repaid notes keep their face tag.** Oracle tags notes repaid during the year with carrying 0 *and* their original face, dated at the period end. | Week 2 hand-check (Oracle 10-K FY2025). | An explicit zero balance wins; face at period end counts only when no balance is tagged (still unreliable alone — P35). |
| P31 | **Combined members.** One member names two bonds ("4.319% … Due 2028 And 4.212% … Due 2026"). | Week 2 answer-key anomaly check (AMD coverage 148%). | Members naming several coupons or maturities are deals, not bonds. |
| P32 | **Acquired debt on a `BusinessAcquisition` axis.** | Week 2 hand-check: Broadcom's 10 assumed VMware notes (56 facts) were dropped. | The axis is descriptive; its facts are kept. |
| P33 | **Members named by due date**, and misspelt. | Broadcom: `May2025SeniorNotes`, `November2025SeniorNotes`, `May2027SeniorNots`. | A month on or after the report's period end is a maturity; "Nots" reads as notes. |
| P34 | **A currency the XBRL never states.** A Swiss franc note whose label names no currency and whose face and carrying are both tagged in USD. | Week 2 hand-check (Equinix 10-K). | A key currency is *known* only from the label or a foreign-unit face; otherwise it does not block a match. |
| P35 | **Face-only "outstanding" is unreliable.** A repaid sterling note with no balance tag, only a face dated at the period end. | Week 2 held-out check (Digital Realty 10-Q). | **Fixed (Week 3):** a face-only bond due by the report's year, in a report that tags balances for its other debt, is repaid. (Requiring a balance tag outright was rejected: it drops new issues tagged only by face.) |
| P36 | **Filer tagging errors on currency.** A dollar exchangeable note's face tagged in euros. | Same. | **Fixed (Week 3):** when face and carrying are tagged in different units and the label names no currency, the currency is unknown and does not block a match. |
| P37 | **Translated face amounts.** Euro notes' face tagged as dollar translations, so the key's principal is in another currency from the printed one. | Same (principal 4 of 20 agree). | **Fixed (Week 3):** principal is scored only when the key's currency is known or equals the ledger's. |
| P38 | **Over-allotment tagged as its own bond.** The banks' $300 m option on a convertible is a separate member, although the base bond's amount already includes it — a double count. | Week 3 fresh held-out check (Super Micro 10-K FY2025). | **Fixed (Week 4):** a bond member named for an over-allotment (or greenshoe) with a base bond of the same maturity is a *component*, not a bond (19 such members across the key, all at Super Micro and TeraWulf). |
| P39 | **Small notes with no maturity anywhere in the XBRL.** Names carry the lender (HMC, Trilogy …), not a year; the year is only a printed column. | Week 3 fresh held-out check (Core Scientific 10-Q; 1 key bond vs 6 printed). | **Fixed (Week 4), by narrowing the truth:** a ledger bond that is one of the key's instruments with no maturity (same currency, amount within 1%/2%, same coupon where both state one) is set aside — neither a match nor an extra — and counted (`grader.covered_by_unkeyed`). |
| P40 | **A coupon found inside another number.** The change search read "0%" inside "escalates 20%" and credited a 0% 2031 convertible to an earnings release. | Week 3 triage report (Core Scientific). | **Fixed (Week 3):** a coupon must start a number; the notes are credited to the 8-K that announced them. Week 2's counts unchanged. |
| P41 | **Total debt from half a pair.** The key sums "long-term debt, noncurrent + current", but a filer tags the current part under a tag the key does not read (`LongTermDebtAndCapitalLeaseObligationsCurrent`), so the total is the noncurrent part alone. | Week 4 fresh held-out check (Constellation 10-Q: $7,321 m vs $8,358 m printed). | **Fixed (Week 5):** the current half is also read from `LongTermDebtAndCapitalLeaseObligationsCurrent`. Week 4's set re-graded: Constellation agrees. |
| P42 | **One bond under two members.** The same notes tagged twice, once with a coupon and once without, same maturity and amount. | Week 4 fresh held-out check (Marvell 10-Q: 4.875% 2028 notes, $499.9 m twice). | **Fixed (Week 5):** a bond with no coupon whose year and amount (within 0.5%) repeat a bond with one is a component. |
| P43 | **A member naming a range of maturities.** "Oregon and Arizona Bonds Due 2035 To 2040" (printed 3.80%–4.10%, one line) is read as one 2035 bond. | Week 4 fresh held-out check (Intel 10-K FY2024). | **Fixed (Week 5):** a due-year range is a series with no single maturity, so no match key. |
| P44 | **L1 with nothing to grade per bond.** No instrument carries a maturity and no total is tagged, so coverage is measured against the report's own instruments; and a note's face tag is its commitment ($125 m), not what is drawn ($105 m). | Week 4 fresh held-out check (Applied Digital 10-Q). | **Fixed (Week 5) in the grader:** an L1 episode whose target holds no bond with a maturity is graded on totals only, and says so (`level_note`). Changes B0's L1 count from 47 to 45 episodes. |
| P45 | **One document, two accessions.** A co-issued term sheet is filed under each co-issuer's CIK with different accession numbers, so de-duplicating co-filings by accession keeps both copies. | Week 4 fresh triage set (Dell's October 2024 term sheet, under Dell International and EMC). | **Fixed (Week 5):** same day, form, file name *and* text = one filing; the first copy lists the others (`timeline.drop_duplicate_documents`). |
| P46 | **A preliminary cover blank down to the century.** `€ % Notes due` (no "20") escapes the Week 4 blank-cover pattern, and rule R2 then reads "Preferred Stock" in the cover's contents as an equity offering. | Week 4 fresh triage check (IBM euro notes, Feb 2025) — the only miss, 8 of 9. | **Fixed (Week 5):** `% Notes due` with anything after it is a note offer, and a contents list ("Description of Preferred Stock") is not a share sale. Third fresh triage check: 15 of 15. |
| P47 | **A convertible-only filer's total.** A company whose only debt is a convertible tags its total as `ConvertibleDebt` / `ConvertibleDebtNoncurrent`, which the total-debt chain does not read, so the key has no total. | Week 5 fresh held-out check (TeraWulf 10-Q, June 2025: $488.7 m). | Open (Week 6). |
| P48 | **The same filer again: nothing keyed, and a repaid note carried.** No instrument names a year, so L1 has nothing to grade (P44), and the repaid CIM promissory note stays outstanding at its $125 m face. | Week 5 fresh held-out check (Applied Digital 10-Q, Nov 2024). | Open (Week 6). |
| P49 | **"Due in the next 12 months" is the next calendar year.** In 10-Qs the key's `…InNextTwelveMonths` value is the next full year's row of the printed ladder. | Week 5 fresh held-out check (IBM: 2026 row $6,431 m; Vistra: 2025 row $786 m). | Noted; it affects every 10-Q target's L3 ladder grading. Open (Week 6). |
| P50 | **The reader's currency sign rewritten while copying** (€1,500,000,000 "copied" as $1,500,000,000). | Week 4 reader evaluation (8 refused copies). | **Fixed (Week 5):** when the number is in the passage under another sign, the passage's own words are used and the citation says `sign from source`. |
| P51 | **An amount-only facility sentence below the passage threshold** ("a $500 million term loan facility"). | Week 4 reader evaluation (Super Micro: no passages). | **Fixed (Week 5):** a facility word beside an amount scores one more. |
| P52 | **Existing debt read from a blank prospectus's tables.** On a preliminary cover with every term blank, the model listed the existing-notes table as new issues. | Week 4 reader evaluation (Equinix: 15 of 29 extras). | **Fixed (Week 5):** on a blank cover, a new instrument whose every value comes from a table row is set aside (kept in the record, not used). |
| P53 | **A share tender read as a debt tender.** Rule R4's tender pattern fires on a third party's mini-tender for shares. | Week 5 fresh triage set (Alphabet, Sept 2024). | Open (Week 6): not fixed against the set that found it. |
| P54 | **An FWP for shares that names the concurrent notes.** Rule R3 keeps a borrowed-share pricing term sheet because it mentions the convertible notes. | Week 5 fresh triage set (Cipher Mining, May 2025). | Open (Week 6). |
| P55 | **Events after the quarter end applied to it.** The window runs to the target report's filing, weeks after the quarter; the first full run put bonds priced after the quarter end into that quarter's ledger. | Week 5 first full run on dev (CoreWeave's July 2025 notes in the June quarter; Super Micro's early-2025 notes in two 2024 quarters). | **Fixed (Week 5, dev):** only events filed on or before the quarter end are applied; the rest stay in the record. Filing date stands in for settlement (P4) until settlement dates are parsed. |
| P56 | **Existing notes read from a prospectus as new issues.** Descriptions of notes already outstanding, with no amount, added as new bonds. | Week 5 full run (Equinix, 10 of the 26 false additions in L1 episodes). | Open (Week 6). |
| P57 | **A proposed offering added as its own bond.** A launch or blank preliminary prospectus has no coupon yet, so its event has no match key and cannot merge with the priced bond. | Week 5 full run (10 false additions: Oracle, CoreWeave, Super Micro, Cipher Mining, Applied Digital, Equinix). | Open (Week 6): merge a keyless *new* event into a priced one of the same kind and year in the window. |
| P58 | **The banks' option read as a bond.** "Up to an additional $45 million" listed as an instrument (the reader's version of P38). | Week 5 full run (4 false additions) and fresh reader set. | Open (Week 6). |

## 3.5 How the data is used

**An episode** = one company, one quarter:

```
start:   the company's report for quarter t        (D3, public)       → opening ledger
events:  every filing accepted from ~30 days before
         the end of quarter t up to the report
         for quarter t+1 (exclusive)               (D1, D2)           → announcements to read
target:  the debt facts in the report for t+1      (D4 + D5, hidden)  → answer key
```

The window opens before quarter t ends because a bond priced in late March can settle in April
(P21); settlement dates decide which quarter each bond belongs to.

The agent rebuilds the ledger *as of the end of quarter t+1* from the start plus the events, then
the grader compares it with the target.

**Two starting modes**, both reported:
- **agent start** — the agent reads the previous report's debt note itself (the realistic mode);
- **oracle start** — the agent starts from the previous report's tagged facts, which isolates how
  well it tracks *changes*.

**Splits** (by time, so the test is always "the future" relative to development):

| Split | Quarter ends being predicted | Universe | ≈ Episodes |
|---|---|---|---|
| **dev** | Sep 2024 – Jun 2025 | AI-25 | ~100 |
| **test** | Sep 2025 – Jun 2026 | AI-25 + generalisation set | ~100 AI + ~300 general |
| **live** | Sep 2026 onward | AI-25 | as reports arrive (Q3 2026 reports land late Oct – mid Nov 2026) |

Exact counts are fixed in week 1 and recorded in the split manifests; no company is tuned on test.

**Week 1 counts** (`scripts/build_splits.py` → `manifests/dev.csv`, `manifests/test.csv`; frozen at
the Week 1 gate): **dev 95** AI episodes (L1 47, L2 12,
L3 36; CoreWeave listed in March 2025, so it has only one dev episode); **test 100** AI episodes
(L1 60, L2 13, L3 27) **+ 300** generalisation episodes (L1 293, L3 7). Seven episodes are
downgraded to L3 by the P19 check. None were dropped. The generalisation set is 75 US
non-financial, non-AI companies picked by a written rule (`scripts/select_generalisation.py`:
≥ 3 of 4 test reports at L1, at most 3 per SIC major group, larger debt first) from 496 that
qualified.

---

# 4. The output

## 4.1 The ledger — one record per bond or loan

```json
{
  "company_cik": 9999999,
  "instrument_id": "example-senior-notes-2031-6.500",
  "kind": "senior_notes",
  "currency": "USD",
  "principal": 1500000000,
  "rate": {"type": "fixed", "coupon_pct": 6.5},
  "maturity": "2031-06-01",
  "settles": "2026-05-27",
  "status": "outstanding",
  "events": [
    {"type": "priced", "date": "2026-05-21", "source": {"accession": "<accession>", "doc": "ex99-1.htm", "span": "s14"}},
    {"type": "settled", "date": "2026-05-27", "source": {"accession": "<accession>", "doc": "8-k.htm", "span": "s3"}}
  ],
  "confidence": "high",
  "checks_passed": ["tranches_sum_to_total", "settlement_after_pricing"]
}
```

*(A made-up example company and bond, to show the shape only. Real records are filled from the
cited sentences.)*

## 4.2 The signals (per company per quarter, and for the whole sector)

| Signal | Plain meaning |
|---|---|
| **Total debt** | Everything owed, split into bonds, term loans, drawn facilities, other |
| **Net new borrowing** | Bonds and loans added minus repaid, this quarter |
| **Maturity wall** | How much must be repaid in the next 12 and 24 months |
| **Debt due vs. cash** | Next-12-month maturities divided by cash on hand |
| **Average coupon** | The weighted interest rate on outstanding bonds — is borrowing getting more expensive? |
| **Debt vs. capital spending** | New borrowing divided by money spent on data centres and equipment this quarter |
| **AI debt index** (sector) | Total AI-universe bonds outstanding and quarterly issuance, by group |
| **Unannounced debt share** | How much of the change was never announced (P10) |

The signals are computed by code from the ledger, never written by the AI. They are published as a
versioned contract (`schema_version 1.0`), separate from a short human-readable quarterly note in
which every number is pulled from the contract and checked against it.

---

# 5. Architecture at a glance

```
                     ┌───────────────────────────────────────────────────────┐
                     │  BATCH SCHEDULER — runs several companies at once      │
                     └───────────────────────────────────────────────────────┘
                                          │  one episode (company, quarter)
                                          ▼
                     ┌───────────────────────────────────────────────────────┐
                     │  LangGraph SUPERVISOR (per episode)                    │
                     │  builds the timeline · triages · fans out · reconciles  │
                     └───────────────────────────────────────────────────────┘
        ┌───────────────────────┬──────────────┴───────────────┬──────────────────────┐
        ▼                       ▼                              ▼                      ▼
 ┌──────────────┐     ┌──────────────────┐          ┌──────────────────┐   ┌──────────────────┐
 │ Opening-     │     │ Event reader #1  │   ...    │ Event reader #N  │   │ Maturity sweeper │
 │ ledger reader│     │ (one filing each)│          │ (run in parallel)│   │ (code)           │
 └──────────────┘     └──────────────────┘          └──────────────────┘   └──────────────────┘
        └───────────────────────┴──────────────┬───────────────┴──────────────────────┘
                                               ▼
                     ┌───────────────────────────────────────────────────────┐
                     │  Merge + ledger engine (code)  →  self-checks (code)    │
                     └───────────────────────────────────────────────────────┘
                                 │ contradictions            │ all clear
                                 ▼                           ▼
                     ┌──────────────────────┐     ┌────────────────────────────┐
                     │ Investigators ×N     │     │ Signals (code) → contract   │
                     │ (parallel look-ups)  │     │ → human gate → data/verified│
                     └──────────────────────┘     └────────────────────────────┘

 MCP servers:  edgar_pit · docs · ledger · debt_signals (read-only)      Grader: separate, never connected
 Models:       qwen3:8b (reading, merging, investigating) · qwen3:4b (triage)  — via Ollama
```

---

# 6. MCP servers (the tools)

Each is a small Python process using the official MCP Python SDK (`FastMCP`, stdio). LangGraph loads
them with `langchain-mcp-adapters`. Separate processes give one place for caching and rate limits,
make each tool testable alone, and keep the agents physically away from the answer key.

| Server | Tools | Notes |
|---|---|---|
| **`edgar_pit`** (point-in-time EDGAR) | `timeline(cik, start, end)` → filings with form, item codes, accepted time · `exhibits(accession)` · `fetch(accession, doc)` → cached local copy | Started with an `AS_OF` timestamp; **refuses anything accepted later** and the target report. Shared 8 req/s limiter, on-disk cache under `AI_DEBT_DATA`. Every call logged. |
| **`docs`** | `sections(doc)` · `sentences(doc, section)` → sentences with ids · `tables(doc)` → cell grids with ids · `search(doc, query)` · `span(doc, id)` | Turns HTML/PDF filings into addressable sentences and cells, so the agent can **cite** instead of retype. Indentures are 100+ pages; `search` keeps the model's input small. |
| **`ledger`** | `get(cik, as_of)` · `propose(event)` → validated diff (not applied) · `open_questions(cik)` | The agent proposes; plain code validates and applies. |
| **`debt_signals`** (read-only, for Mycroft) | `company_debt(cik, quarter)` · `maturity_wall(cik)` · `sector_index(quarter)` · `unannounced(quarter)` | Same pattern as the Private AI Valuation Agent's server: token-bounded pages, a summary first, a cursor for the rest. Nothing here writes data or clears a gate. |
| **`grader`** | `grade(episode, ledger)` | **Not connected to the agent graph.** Used only by the evaluation harness; reads D4/D5/D6. |

---

# 7. Agent workflow (LangGraph)

## 7.1 Design rules

1. **The AI never types a number or a date.** It points at a sentence or table cell ("principal is
   in sentence `s14`"); code parses "$1.25 billion", "4.750%", "June 1, 2031" from that span. This
   removes made-up figures and keeps model output short.
2. **The AI never does arithmetic.** Sums, ledgers, signals and checks are code.
3. **Every ledger change cites a document.** A change with no citation is rejected.
4. **Point-in-time, always.** No tool can return anything accepted after the episode's cut-off.
5. **Hard limits:** at most 2 investigation rounds per episode, a per-episode time budget, and a
   maximum number of documents read.
6. **Use the AI only where judgment is needed** (Section 7.3 marks which steps use it).

## 7.2 Shared state

```python
class EpisodeState(TypedDict):
    cik: int
    quarter_end: str                       # the quarter being predicted, e.g. "2026-06-30"
    cutoff: str                            # acceptance time of the target report (exclusive)
    opening: list[Instrument]              # ledger at the start
    candidates: list[DocRef]               # filings in the window
    relevant: list[DocRef]                 # after triage
    events: Annotated[list[Event], add]    # appended by parallel readers
    questions: Annotated[list[Question], add]
    rounds: int
    ledger: list[Instrument] | None        # closing ledger
    signals: dict | None
```

`Annotated[..., add]` lets parallel branches append to the same list safely.

## 7.3 Nodes

| Node | AI? | What it does |
|---|---|---|
| **timeline** | no | Lists every filing in the window from `edgar_pit`, with form and item codes. |
| **opening-ledger reader** | **yes** | (Agent-start mode.) Reads the debt table in the previous report via `docs.tables` and turns each row into an instrument, citing cells. Runs **in parallel** with triage. |
| **triage** | rules + **yes** for doubtful cases | Rules first (item 2.03, form `FWP`, "aggregate principal amount", "notes due", "redemption", "tender offer", "credit agreement"). `qwen3:4b` decides only doubtful documents and labels the event type. |
| **event readers** ×N, **in parallel** | **yes** | One per relevant filing (LangGraph `Send`). Extracts each bond or loan as structured fields that **point to spans**: issuer, kind, currency, principal, rate or rate formula, maturity, priced/settles dates, and action (new, add-on, redeem, tender result, exchange, draw, amend, terminate). Output is forced to a JSON schema. Reads exhibits (term sheet, indenture) when the main document lacks a field. |
| **maturity sweeper** | no | Retires any instrument whose maturity date falls inside the window — no announcement needed. |
| **merge** | code + **yes** for ties | The same bond shows up in a pricing press release, a term sheet and a closing 8-K. Code merges on the match key (P3); the model decides only ambiguous pairs. |
| **ledger engine** | no | Applies events in settlement-date order to the opening ledger. |
| **self-checks** | no | Tranches add up to the announced total · settlement after pricing · no negative balances · every repayment refers to a known instrument · announced use of proceeds ("to repay the 2027 notes") matches a repayment · total change is plausible. |
| **investigators** ×N, **in parallel** | **yes** | One per open question: e.g. *"redeemed the 2027 notes, but they're not in the opening ledger"* → search older filings (still before the cut-off) for the original issuance; *"tender offer launched, no results"* → look for the results announcement. New findings go back through merge → ledger → checks (max 2 rounds). |
| **signals** | no | Computes Section 4.2 from the ledger plus company totals (D6). |
| **note writer** | **yes** (optional) | Drafts the quarterly note; a grounding check rejects any number not present in the signal contract. Labelled as model-written. |

## 7.4 Graph

```
timeline ─┬─► triage ─► plan ─┬─► reader(doc 1) ─┐
          │                   ├─► reader(doc 2) ─┤
          │                   └─► reader(doc N) ─┼─► merge ─► ledger ─► checks ─┬─ clear ─► signals ─► END
          └─► opening-ledger reader ─────────────┤                             │
              maturity sweeper ──────────────────┘                             └─ questions ─► investigators ×N (parallel)
                                                                                              └──► merge (loop, max 2 rounds)
```

LangGraph's SQLite checkpointer saves every step, so a crash or laptop sleep resumes where it
stopped.

## 7.5 Batch scheduler and what "parallel" means on one GPU

- The scheduler runs **several companies at once** (start with 4). Within a company, quarters run in
  order, because each quarter's closing ledger is the next one's opening ledger.
- Fetching and parsing filings is CPU and network work and overlaps freely with model calls.
- All model calls go through **one GPU semaphore** sized to Ollama's parallel slots
  (`OLLAMA_NUM_PARALLEL=2–3`). Ollama batches concurrent requests, so readers really do run at the
  same time — but the speed-up on one GPU is measured, not assumed (ablation A3).

## 7.6 Live mode

A daily job asks `edgar_pit` for new filings from the universe (cut-off = now), runs only the
triage → readers → merge → ledger → checks path for those documents, and updates the ledger and
signals. When the next quarterly report appears, the live ledger is graded against it
automatically — so the project keeps producing fresh, honest accuracy numbers after week 10.

---

# 8. Which models (local, free)

## 8.1 The hardware (checked)

| | |
|---|---|
| GPU | NVIDIA **RTX 4070 Laptop, 8 GB VRAM** |
| RAM | 32 GB |
| CPU | Intel i9-14900HX |
| Installed | Ollama 0.34.0, `llama3.1:8b` already pulled; `qwen3:8b` and `qwen3:4b` in the project's models directory. *Week 1 decision (Om Mali, 2026-10-18): stay on 0.34.0 rather than update to 0.40.6 mid-measurement, so the Week 0 and Week 1 speeds are comparable.* |

Debt documents are **text** (HTML, sometimes PDF with a text layer), so unlike SpreadCheck no vision
model is needed. 8 GB is the binding limit, so the design keeps **one model loaded at a time**.

## 8.2 The picks (sizes from the Ollama library)

| Role | Model | Size | Why |
|---|---|---|---|
| **Main** — reading announcements, the opening ledger, merging ties, investigating | **`qwen3:8b`** | 5.2 GB, 40K context, tools, thinking mode | Strong at structured extraction and tool calls for its size; fits 8 GB with room for 2 parallel slots at 8–16K context. |
| **Fast** — triage, and long documents | **`qwen3:4b`** | 2.5 GB, **256K context**, tools | Long context helps with 100-page indentures; small enough for 3–4 parallel slots. Tested as an all-in-one alternative (ablation A5). |
| **Continuity option** | `qwen2.5:7b-instruct` | ~4.7 GB | What the Private AI Valuation Agent already uses for entity resolution. |
| **Baseline only** | `llama3.1:8b` (already installed) | 4.9 GB | Older text model; comparison point. |

**Week 1 bake-off (§8.5) reversed the main pick.** On 29 real announcements with no hints,
`qwen3:4b` read 99% of fields (95% before 7 truth corrections), with 29/29 valid JSON and a 12.6 s
worst case. `qwen3:8b` read 88%: it had 2 runaway answers that looped until the output cap, and it
mislabelled new issues as redemptions. By the rule set in advance, **`qwen3:4b` is the main model**
(confirmed at the Week 1 gate), and `qwen3:8b` stays as the alternative for investigators, where
thinking mode may matter (untested). Every call carries an output cap (`num_predict`), because a
looping model otherwise holds the GPU for minutes.

**Why not bigger?** 14B+ models (e.g. `qwen3:14b`, 9.3 GB) don't fit fully on 8 GB and become several
times slower with CPU offloading. **Why not newer?** New ≤9B models appear on Ollama every month;
the week-1 bake-off includes up to two newer candidates and switches only if one wins clearly. The
design doesn't depend on any specific model.

## 8.3 Settings

```
OLLAMA_NUM_PARALLEL=2            # 3–4 with qwen3:4b
OLLAMA_FLASH_ATTENTION=1
OLLAMA_KV_CACHE_TYPE=q8_0        # halves context memory, small quality cost
OLLAMA_MAX_LOADED_MODELS=1       # never two models on the GPU at once
OLLAMA_MODELS=<local models directory>   # weights outside the repo
num_ctx = 8192–16384             # one announcement or one retrieved section
temperature = 0                   # repeatable runs
think = false                     # for triage/extraction; test true for investigators
format = <JSON schema>            # Ollama structured outputs force valid JSON
```

## 8.4 Budget

- Money: **$0.** No paid API anywhere.
- Speed (**measured** 16 Oct 2026 on 33 real announcements): `qwen3:8b` runs at **~43 tokens/s**,
  **3.7 s per announcement**, using **5.3 GB** of the 8 GB GPU at a 4K context — about 2 GB left for a
  second parallel slot. With ~20 relevant documents per active company-quarter, a full backtest is
  hours, not days — fine overnight.
- Weights (4.9 GB) live in the local models directory set by `OLLAMA_MODELS`, outside the repo.

## 8.5 Week-1 bake-off

Thirty real announcements from the dev window (term sheets, press releases, redemption notices,
credit agreements). Score per model: field accuracy against a hand check, JSON validity, and
seconds per document. Pick the best model that is ≥ 95% JSON-valid and reads a document in ≤ 30 s.

*Run in week 1* (`scripts/bakeoff.py`, results in [`docs/bakeoff.md`](docs/bakeoff.md)). Two
changes from the plan, both stated in the report: the dev window yielded **29** usable
documents (term sheets, prospectus supplements and 8-K announcements) and almost no redemption
notices or credit agreements; and the task is **harder than Week 0's** — the spike's prompt
named the coupon to look for, which made coupon accuracy 33/33 by construction, while the
bake-off gives the model only the document. Truth comes from the next report's XBRL. A row-by-row
review corrected 7 truth fields where the announcement itself says otherwise (euro amounts, prices
before the banks' extra allotment, a floating rate), recorded in
`manifests/bakeoff_truth_corrections.json` and [`docs/week1_review.md`](docs/week1_review.md).

---

# 9. Evaluation

## 9.1 Three levels of grading

| Level | For companies that tag… | A match means |
|---|---|---|
| **L1 — per bond** | each bond | Same currency, same rate (±0.01 pp), same maturity year, principal within 1% |
| **L2 — per offering** | each offering (e.g. Meta) | Bonds grouped by issue date; offering total within 1%, maturities match |
| **L3 — totals** | everyone | Total debt, current vs. long-term, and maturity buckets (next 12 months, years 2–5, after) within 2% |

Bond matching is plain code using the match key (P3) and an optimal one-to-one assignment
(Hungarian algorithm). Matches are audited by hand on the dev set in week 2.

## 9.2 Metrics

| Metric | Plain meaning |
|---|---|
| **Bond recall / precision (L1)** | Of the bonds in the report, how many the ledger has (and how many of the ledger's bonds are real). **The headline.** |
| **Change detection** | Of bonds **added** or **removed** during the quarter, how many the tracker caught. This is what announcement-reading adds over doing nothing. |
| **Principal accuracy** | Share of matched bonds with the right principal. |
| **Total-debt error (L3)** | Percentage difference in total debt and in the maturity wall. |
| **Unannounced debt share** | Share of changes explained by no document in the window (P10) — a data finding, not an agent error. |
| **Self-catch rate** | Of the episodes that ended wrong, how many the self-checks flagged. |
| **Cost** | Documents read, model minutes and wall time per episode. |

Reported per company group, per grading level, per split, and for agent-start vs. oracle-start.

## 9.3 Baselines (what it must beat)

| | Baseline | What it shows |
|---|---|---|
| **B0** | **Carry forward**: last quarter's ledger, minus bonds that reached their due date. No reading at all. | The floor. Strong for quiet companies like Microsoft, useless for active ones. |
| **B1** | Regex rules on press releases and term sheets ("$X aggregate principal amount of Y% notes due Z"). | How far simple pattern matching gets. |
| **B2** | One `qwen3:8b` call per document, no merging, no checks, no investigators. | The "just ask a model" approach. |
| **Full** | AI Debt Tracker. | |

*B0 measured in week 2* ([`docs/baseline_b0.md`](docs/baseline_b0.md), dev split, 95% bootstrap intervals):
**L1 bond recall 90.7%** (87.5–93.5), precision 90.3% (85.9–94.0), principal accuracy 99.2%; 18 of 47
L1 episodes reproduced exactly. **New bonds caught: 0 of 36; early removals caught: 3 of 16** (by the
maturity sweep). L2 offering recall 76.2%. The headroom the agent has to win is exactly those
additions and removals: 30 of the 32 searchable new bonds and 5 of the 6 early removals were announced
in a filing it could read ([`docs/changes_dev.md`](docs/changes_dev.md)). B0 opens from the last
report itemised finely enough (it walks back for Intel- and Oracle-style annual-only itemisers) and
sweeps bonds by maturity year.

*B1, B2 and the event reader measured in week 4* ([`docs/reader.md`](docs/reader.md)), on the 24 debt-relevant
filings of Week 3's labelled triage set (66 instruments, truth labelled before any run and checked against the
next report's XBRL): **B1 135 of 160 fields (84%)**; **B2 160 of 160 (100%)**; **the event reader 157 of 167
(94%)**. B2 is run with `qwen3:4b`, not `qwen3:8b` as first planned, so the comparison holds the model fixed.
The reader passes the week 4 check (beats B1), but B2 reads numbers at least as well on these documents; the
reader's gain is provenance — every value is parsed by code from a cited passage, and copies no passage contains
are refused (8 this week were currency signs the model rewrote).

*Week 5, the reader on fresh filings* ([`docs/reader.md`](docs/reader.md)): after fixing P50–P52, the 15 debt-relevant
filings of a fresh labelled set (27 instruments, truth labelled before any run): **reader 48 of 53 fields (91%), B1 39 of
53 (74%), B2 51 of 53 (96%)**; extras: reader 5, B1 1, B2 15. The ordering of Week 4 holds on filings nobody had read.

*Week 5, the full tracker on dev* ([`docs/episodes.md`](docs/episodes.md)), oracle start (A4: B0's opening ledger),
45 L1 episodes: **bond recall 97.8%** (96.0–99.3) vs B0's 90.9% — paired difference **+6.9 points** (+4.7 to +9.4);
**precision 90.2%** (85.8–93.5) vs 92.8%, **−2.6 points** (−5.7 to −0.2). **New bonds caught: 30 of 34** (B0: 0).
Removed bonds caught: 3 of 14 (B0: 1). The precision loss is 26 bonds added that the report does not hold — P56–P58.

## 9.4 Ablations

| | Change | Question answered |
|---|---|---|
| A1 | No self-checks / investigators | How much does reconciliation fix? |
| A2 | Main documents only, no exhibits | Are term sheets and indentures worth reading? |
| A3 | Readers one after another instead of in parallel | What does parallelism buy on one GPU? |
| A4 | Oracle start vs. agent start | How much error comes from reading the opening debt note? |
| A5 | `qwen3:4b` everywhere | Accuracy vs. speed. |

## 9.5 Honesty rules

- 95% confidence intervals by bootstrap over episodes; paired comparisons on the same episodes.
- The test split is run once for v1 and once for v2 (after dev-only fixes); both are reported.
- Every dropped company or episode is counted with its reason.
- Model judgments (triage labels, the quarterly note, off-balance-sheet text) are labelled as such.
- Live-mode accuracy (from Q3 2026 reports) is reported separately as the only truly unseen test.

## 9.6 Error taxonomy

Missed announcement · wrong document family · two tranches merged · tranche split · wrong
settlement date · wrong currency · rate formula misread · repayment of unknown bond · partial
redemption treated as full · tender result missed · draw/capacity confusion · subsidiary issuer
missed · answer-key problem (truth itself inconsistent) · unannounced debt.

---

# 10. Fitting Mycroft's rules (SNICKERDOODLE.md)

| Rule | How this project follows it |
|---|---|
| Only ingest scripts touch the network | All fetching goes through `edgar_pit`; agents read cached local copies. |
| Nothing enters `data/verified/` unvalidated | Ledgers and signals stay in this project's raw layer until a backtest report passes and a **named human** clears the gate, logged in `logs/RUN_LOG.md`. |
| Never invent a count, rate or confidence | Every number traces to a cited sentence or to the answer key; counts in this document come from scripts in `scripts/`. |
| Model judgments labelled | Triage labels, the quarterly note and off-balance-sheet text carry a `model_judgment: true` flag. |
| Log meaningful runs | Every backtest and live run appends a short entry to `logs/RUN_LOG.md`. |
| Never delete — archive | Superseded ledgers and runs are versioned, not overwritten. |

---

# 11. Ten-week plan

Each week ends with a check. If a check fails, fix it before moving on: everything downstream depends
on what came before. Each week also ends with a commit, a worklog entry and a short demo of what's
new — the contribution record.

| Week | Build | End-of-week check |
|---|---|---|
| **1 — Feasibility and universe** | Professor sign-off (F0). Freeze `universe_v1.json` (AI-25 + issuing subsidiaries + grading level per company) and pick the ~75-company generalisation set. Update Ollama; pull `qwen3:8b`/`4b`; run the bake-off (8.5). `edgar_pit` skeleton with the cut-off rule. Load the answer key for 10 companies from the monthly notes data. Run the remaining feasibility checks (`docs/feasibility.md`). | **Go / no-go:** all feasibility checks recorded with pass/fail; universe frozen; model chosen with measured speed. |
| **2 — Answer key and grader first** | Answer-key builder for every universe report Q2 2024 – Q2 2026 at all three levels. Bond matcher + grader. Baseline **B0** (carry forward). Hand-check 10 company-quarters against the debt tables in the reports. | Grader agrees with the hand check on 10/10. B0 scored on dev — this fixes the headroom. |
| **3 — Timeline, triage, documents** | `docs` server (sentences, tables, search, spans). Timeline across all four document families. Triage (rules + `qwen3:4b`). A hand-labelled set of 50 documents (relevant? which event?). | Triage finds ≥ 95% of the debt-relevant documents on the labelled set. |
| **4 — Event reader** | Single-document reader → structured events that point to spans; code parsers for amounts, rates, dates. Baselines **B1** (regex) and **B2** (single call). | Reader beats B1 on field accuracy on the 50 labelled documents. |
| **5 — Supervisor and parallel readers** | LangGraph supervisor; `Send` fan-out to readers; maturity sweeper; merge; ledger engine (settlement dates, add-ons, partial redemptions); self-checks; `ledger` server; checkpointing. | Full episodes run end to end on dev; first L1 bond recall/precision. |
| **6 — Opening ledger, investigators, hard cases** | Opening-ledger reader (agent-start mode). Parallel investigators with the 2-round limit. Loan facilities (capacity vs. drawn), floating rates, convertibles, foreign currency. "Unannounced debt" accounting. | Agent-start vs. oracle-start gap measured; self-catch rate measured. |
| **7 — Freeze and scale up** | Tag **v1**. Batch scheduler (companies in parallel, GPU semaphore). Signals (Section 4.2) and the draft signal contract. Run the whole dev window unattended; first `logs/RUN_LOG.md` entries. | Dev window completes overnight with no crashes; signal contract validates. |
| **8 — Full evaluation** | Run B0, B1, B2, Full and ablations A1–A5 on test (AI-25 + generalisation set). Bootstrap confidence intervals; cost table. | Complete results table. |
| **9 — Error analysis, one improvement round, signal server** | Classify every failure (9.6); fix the top 2–3 causes **using dev only**; re-run test as **v2**. Build the read-only `debt_signals` MCP server. | v1 and v2 results both recorded; MCP server answers the four tools with bounded output. |
| **10 — Live mode, documents, launch** | Daily live mode on the universe (it should pick up the Q3 2026 reports arriving late Oct – mid Nov). `proposal.md`, `system_architecture.md`, `data_architecture.md`, `findings.md`, `docs/demo.md` (a re-runnable demo script). Freeze signal contract `1.0`. Request the human gate; open the PR. | Someone else can run the demo from the README; first live episode graded automatically. |

**Buffer:** weeks 6 and 9 hold slack. If you're behind, drop the generalisation set to ~40 companies
and ablations A2/A5 — never cut the grader, the frozen test split, or the point-in-time rule.

---

# 12. Feasibility before commitment

A feasibility spike was run on 16 October 2026 on 46 real company-quarters (23 companies × 2
quarters). Full results in [`docs/feasibility.md`](docs/feasibility.md):

| Check | Result |
|---|---|
| Are debt changes announced? | **87.5%** of real new bonds (56 of 64) were explained by an 8-K, prospectus or term sheet in the window — **pass** |
| Is there anything to beat? | Carrying last quarter forward misses an announced change in **21 of 46** company-quarters (46%) — **pass** |
| Can bonds be matched between reports? | **83%** of instruments reappear under the same name or key — **partial**, with five specific, fixable causes (P17–P21) |
| Can a local model read the filings? | `qwen3:8b`, one naive call per document (baseline B2) on 33 real announcements: valid JSON 33/33, interest rate 33/33, maturity year 29/33, principal 7/13 — **87% of fields, 3.7 s per document — pass (narrow)**; principal is the weak field |
| Does the professor agree? | **Approved** (16 October 2026) |
| *Week 1:* matching on L1-graded episodes (dev) | **93.4%** — pass (all episodes 85%, the gap being Intel's and Oracle's 10-Q tagging, graded at L3) |
| *Week 1:* bake-off, no hints, 29 documents | `qwen3:4b` **95% of fields**, 29/29 JSON, ≤ 12.6 s — pass; `qwen3:8b` 84% |
| *Week 3:* triage on 50 labelled filings | recall **24 of 24 (100%)**, precision 92%, all 22 of Week 2's announcement filings kept; the model decided 34% of 593 filings at 3.1 s each — pass |
| *Week 4:* triage on a fresh labelled set | recall **8 of 9 (89%)** — **below the 95% line** (P46, a blank preliminary cover); the Week 3 set, now a calibration, 24 of 24 |
| *Week 4:* event reader vs B1 on the 24 labelled filings | **94% vs 84%** of fields — pass; B2 (one call, model types numbers) 100% |
| *Week 5:* triage on a third fresh labelled set (after P45, P46) | recall **15 of 15** — pass; precision 15 of 18 (two new rule weaknesses, P53, P54) |
| *Week 5:* event reader on fresh filings (after P50–P52) | **91% vs B1 74%** of fields; B2 96% |
| *Week 5:* full episodes end to end on dev (oracle start) | **95 of 95** ran; L1 recall **97.8%** vs B0 90.9%, precision 90.2% vs 92.8%; new bonds caught **30 of 34** vs 0 |

Verdict: **go.**

---

# 13. Risks

| Risk | Likelihood | What to do |
|---|---|---|
| Too few bond-level companies in the AI universe | Low (21 of 25 tag each instrument) | Hand-check the probe in week 1; the generalisation set adds statistical weight; Meta, Alphabet and Amazon are graded at L2, Oracle at L3. |
| Too much debt is never announced (P10) | Medium | It becomes a measured finding; change-detection is reported against announced changes only, alongside the unannounced share. |
| Matching bonds across documents is messier than expected (P3) | Medium | Week-2 hand-checked alignment table; report unmatched bonds; fall back to L2/L3 for messy companies. |
| 8 GB too tight / too slow | Low–medium | `qwen3:4b`, smaller context, `OLLAMA_NUM_PARALLEL=1`; overnight runs. Ablation A5 turns it into a result. |
| "Data vendors already do this" | Medium | True for paid terminals. What's new: open, reproducible, point-in-time, every entry cited, accuracy measured against official reports, $0 to run, and an AI-sector signal Mycroft doesn't have. Say it up front, with prior art, in `proposal.md`. |
| Scope creep (credit ratings, bond prices, off-balance-sheet deals) | High | Out of scope for v1 (Section 15). |

---

# 14. Repo layout, stack, and where things live

```
data/raw/AI_Debt_Tracker/
  DESIGN.md  README.md  pyproject.toml  uv.lock  universe_v1.json   (Week 0 draft in docs/archive/)
  .env.example  .gitignore
  src/ai_debt_tracker/
    config.py  sec.py  edgar.py               # env-only paths; the one door to sec.gov; filing index   [week 1]
    mcp_servers/   edgar_pit_core.py  edgar_pit.py                                                   [week 1]
                   docs.py                    # sections, sentences, tables, search, span            [week 3]
                   ledger.py  ledger_core.py  # get / propose (dry run) / open_questions                    [week 5]
                   debt_signals.py
    documents/     parse.py  store.py         # filing HTML -> addressable headings/sentences/tables [week 3]
    graph/         nodes/timeline.py  nodes/triage.py                                                [week 3]
                   nodes/reader.py            # event reader: points at passages, code parses           [week 4]
                   supervisor.py              # LangGraph episode graph: Send fan-out, SQLite checkpoints  [week 5]
                   state.py  scheduler.py  nodes/…
    ledger/        parsers.py  matcher.py                                                            [week 1]
                   values.py                  # amounts, rates, maturity years from cited words         [week 4]
                   engine.py  checks.py       # merge, maturity sweep, ledger; self-checks               [week 5]
    llm/           ollama_client.py  schemas.py
    signals/       compute.py  contract.py
    eval/          fsn.py  answer_key.py                                                             [week 1]
                   grader.py  baselines/carry_forward.py                                             [week 2]
                   baselines/regex_reader.py (B1)  baselines/single_call.py (B2)                     [week 4]
                   metrics.py   # nothing outside eval/ may import eval/ (enforced by a test)
  scripts/         probe_debt_filings.py  spike_*.py                                                  [week 0]
                   review_universe.py  select_generalisation.py  build_splits.py
                   load_answer_key.py  f1_matching.py  bakeoff.py                                    [week 1]
                   build_answer_key.py  score_baseline.py  handcheck.py  explain_changes.py           [week 2]
                   triage_eval.py                                                                    [week 3]
                   reader_eval.py                                                                    [week 4]
                   run_episodes.py  episodes_report.py                                               [week 5]
                   demo.py
  manifests/       dev.csv  test.csv  generalisation.csv  week1_gate.json                            [week 1]
                   handcheck/<episode>.json   (13 transcriptions of printed debt tables)  week2_gate.json [week 2]
                   handcheck/ +5 (fresh held-out)  triage_labels.json  week3_gate.json               [week 3]
                   handcheck/ +5  triage_labels_w4.json  reader_truth.json  week4_gate.json          [week 4]
                   handcheck/ +5  triage_labels_w5.json  reader_truth_w5.json  week5_gate.json       [week 5]
  docs/            feasibility.md  worklog.md  universe_v1_review.md  answer_key_week1.md
                   bakeoff.md  bakeoff_set.md  week1_review.md                                       [week 1]
                   answer_key.md  baseline_b0.md  handcheck.md  changes_dev.md                       [week 2]
                   triage.md  triage_labels.md                                                       [week 3]
                   reader.md  reader_truth.md  triage_labels_w4.md                                   [week 4]
                   episodes.md  triage_labels_w5.md                                                  [week 5]
                   archive/   (superseded: universe_draft.json, run_log_pending.md)
                   (later: findings.md, demo.md, mcp_server.md)
  tests/
```

The repo holds only code, documents and small manifests. Everything bulky lives in a local directory
outside the repo, configured in the gitignored `.env` (loaded by `scripts/_localenv.py`):

| What | Configured by | In git? |
|---|---|---|
| Code, docs, manifests, small test fixtures | this folder | yes |
| Filing cache, monthly notes zips, run outputs | `AI_DEBT_DATA` (optionally a gitignored `data` link in this folder) | no |
| Python environment | `UV_PROJECT_ENVIRONMENT` | no |
| Package cache | `UV_CACHE_DIR` | no |
| Model weights | `OLLAMA_MODELS` | no |

**Libraries:** `langgraph`, `langchain-ollama`, `langchain-mcp-adapters`, `mcp` (held below 2.0 —
2.x renamed FastMCP and the adapters target 1.x), `httpx`, `pydantic`,
`selectolax` or `lxml` (HTML), `pdfplumber` (occasional PDF exhibits), `arelle-release` (fallback
answer key), `pandas`, `scipy` (Hungarian matching), `pytest`, `ruff`.

---

# 15. Out of scope for version 1

- Bond prices, yields and credit ratings (no free, redistributable source).
- Off-balance-sheet financing as a graded quantity (tracked as labelled text only — P9).
- Foreign filers that report only twice a year (e.g. 20-F filers).
- Companies outside the frozen universe.
- Trading advice. The signals describe; they don't recommend.

---

# 16. Resume bullet (numbers come from the harness)

> **AI Debt Tracker** — Built a local, $0 multi-agent system (LangGraph + 5 MCP servers + Qwen3 on an
> 8 GB laptop GPU) that tracks every bond and loan financing the AI build-out from SEC filings as they
> appear. Parallel document readers, a ledger engine and self-checking investigators reproduced
> **X%** of the bonds in companies' next official reports (**Y** points above carrying the previous
> quarter forward), and the system publishes a quarterly AI-sector debt signal for the Mycroft
> research platform.

---

# 17. What to do first (this week)

*Done on 16 October 2026:* professor approval (F0); the local data directory; `qwen3:8b` pulled into
the local models directory and tested (F4).

*Done in week 1 (18 October 2026):* `.env` identity filled in; `qwen3:4b` pulled; the notes data for
July 2024 – September 2026 extracted; the answer key loaded for 10 companies; the universe
measured; the generalisation set and the dev/test episodes built; `edgar_pit` built and tested;
F1 re-run; the model bake-off run. **Week 1 gate cleared** the same day by Om Mali on the basis
of Claude's review ([`docs/week1_review.md`](docs/week1_review.md)): universe, generalisation
set, splits and the model (`qwen3:4b`) frozen. See [`docs/worklog.md`](docs/worklog.md).

*Done in week 2 (23 October 2026):* Weeks 0–1 committed and logged in `logs/RUN_LOG.md`; the answer key
built for all 100 companies (1,093 reports, Jan 2024 – Sep 2026); the grader (L1/L2/L3, change
detection, bootstrap intervals); baseline B0 scored on dev; the hand-check — **10 of 10** on the
calibration set after five answer-key and grader fixes (P30–P34), **2 of 3** on a held-out set (P35–P37
open); changes explained with a proper removal method; `edgar_pit` cut-offs pinned to the target report
after EDGAR's clock moved (P29). See [`docs/worklog.md`](docs/worklog.md).

**Week 2 gate cleared** by Om Mali on 23 October 2026: the hand-check
([`docs/handcheck.md`](docs/handcheck.md)) accepted as the week 2 check (`manifests/week2_gate.json`).

*Done in week 3 (31 October 2026):* P35–P37 fixed (Week 2's held-out set now 3 of 3); a fresh held-out
hand-check, drawn before reading — **1 of 3** gradable reports agree (Dell); Super Micro and Core Scientific
disagree because of two new answer-key defects, P38 and P39, left open on purpose; Cipher Mining and
TeraWulf had no debt to compare. The `docs` server (filings as addressable headings, sentences, tables and
cells, opened only through `edgar_pit`), the timeline across 8-Ks, 424Bs and FWPs including issuing
subsidiaries, and triage (rules R1–R5, `qwen3:4b` for the doubtful third). **Triage on the 50 labelled
filings: recall 24 of 24, precision 24 of 26** ([`docs/triage.md`](docs/triage.md)); the labels are
Claude's reading, made before the run ([`docs/triage_labels.md`](docs/triage_labels.md)). P40 (a
change-search coupon bug) found by the triage report and fixed.

**Week 3 gate** (`manifests/week3_gate.json`): Om Mali delegated the whole week in advance and did not
review it; the record says so, and every judgment in it is labelled as Claude's.

*Done in week 4 (7 November 2026):* P38–P39 fixed (Week 3's held-out set now 3 of 3, a calibration); a fresh
held-out hand-check of five reports drawn before reading — **1 of 5** agree (Amazon), four new answer-key defects
P41–P44 left open. The two triage weaknesses from Week 3 fixed, and a fresh 50-filing set labelled before the run:
**recall 8 of 9 — below the 95% line** (P46); one document turned out to be in both sets (P45). The event reader
(`graph/nodes/reader.py`, code parsers in `ledger/values.py`) and baselines B1 (regex) and B2 (one call): on the
24 labelled filings **reader 94%, B1 84%, B2 100%** of fields ([`docs/reader.md`](docs/reader.md)).

**Week 4 gate** (`manifests/week4_gate.json`): Om Mali delegated the week in advance and did not review it. The
reader passes its check; the fresh triage check does not, and the record says so. Whether that blocks Week 5 is
the reviewer's decision (§11: "if a check fails, fix it before moving on").

*Done in week 5 (13 November 2026):* P41–P46 and the three reader defects fixed (P50–P52). Fresh checks, each set
drawn and labelled before the run it scores: **triage 15 of 15** (third fresh set — passes; P53, P54 logged); **the
answer key 3 of 4 gradable reports** (P47–P49 logged); **the reader 91% vs B1 74%**, B2 96% ([`docs/reader.md`](docs/reader.md)).
Built: the ledger engine (merge on the match key, maturity sweep, new issues, add-ons, partial and full redemptions,
open questions), the self-checks, the `ledger` MCP server, and the LangGraph episode graph (timeline → triage → one
`Send` per relevant filing → ledger → checks, SQLite checkpoints). **The week 5 check: 95 of 95 dev episodes ran end to
end.** First L1 numbers, oracle start: recall 97.8% (B0 90.9%), precision 90.2% (B0 92.8%), new bonds caught 30 of 34
(B0 0) ([`docs/episodes.md`](docs/episodes.md)). One engine defect found by the first run and fixed on dev (P55: events
after the quarter end); the precision loss left is P56–P58.

**Week 5 gate** (`manifests/week5_gate.json`): delegated by Om Mali in advance, not reviewed. Weeks 3, 4 and 5 are all
DELEGATED, not CLEARED.

**Week 6 begins with** P56–P58 in the merge step (measured on dev, then on a fresh draw), P53–P54 in triage, P47–P49 in
the answer key, and the reader's misses on fresh filings; then §11's week 6: the opening-ledger reader (agent start —
the A4 gap), investigators for the 53 open questions, loan facilities (capacity vs drawn), and unannounced debt.
