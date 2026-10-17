# Chapter 6 Project: Monthly Variance Pack (META)

Project: Your Own Mycroft. Ticker: META. Builds on theses/META.md, sources-of-truth.md, evidence-audit.md, and CANNOT-KNOW.md. Adds an earnings-surprise variance pack and, where the underlying data actually exists, a returns-vs-benchmark computation.

## Exercise 1 — When to Use AI

AI assistance was appropriate for, and used on, these tasks this chapter:

- Building the variance table structure for `theses/META/earnings-surprise-FY2025.md` — one row per income-statement line, with reported-actual, dollar/percent variance, and source-cell columns. This works because every reported figure traces to a specific line in the FY2025 10-K or the Q4/FY2025 press release, already used as the source of truth in `theses/META.md`, and the arithmetic is independently re-checkable.
- Ranking the flagged lines by absolute dollar variance. This is presentation of an already-computed number, not a judgment about which line matters more.
- Attempting to attach a "prior commentary (sourced)" column from Meta's own prior-period MD&A language, and flagging where no such filed language exists rather than inventing a plausible-sounding one.

The tell held here too: I could re-open the same 10-K and press release the pack cites and independently confirm every reported figure and every variance, which is why I trust the pack's computed columns.

## Exercise 2 — When NOT to Use AI

These stayed mine, and the pack left them blank on purpose:

- Writing the "current explanation" for why any flagged line moved the way it did (e.g., why the FoA advertising acceleration outran or lagged expectations). No consensus estimate is on file for this desk (see Caveats below), so there isn't even a variance to explain yet — but even once one exists, the cause is a business-judgment call I'd need to make myself, not something the model can determine from the filing.
- Deciding whether the pack's one available forward-looking data point — management's own 2026 Reality Labs guidance ("losses to remain similar to 2025," already logged in `human-card.md`) — was met, missed, or beaten once 2026 results post. Whether a "similar to 2025" guide counts as met is itself a judgment call about tolerance, not an arithmetic comparison.
- Whether my own portfolio's return relative to a benchmark, if I had one on file, would reflect skill or luck. That calibration question doesn't exist yet in this desk for the reason described in Exercise 4 — there's no positions file to compute it from — but the chapter is explicit that even where the return number exists, judging its cause stays mine.

The tell: I'd have crossed the line if I'd let a plausible AI-written sentence about "why" any line moved stand in the current-explanation column just because the deadline pressure in the chapter's framing is real even in a personal desk with no CFO waiting.

## Exercise 3 — LLM Exercise

Built `theses/META/earnings-surprise-FY2025.md` in the desk repo: an earnings-surprise variance pack with reported-actual figures pulled only from the FY2025 10-K and the Q4/FY2025 press release already cited in `theses/META.md`, a "consensus estimate" and "prior guidance" column that is explicitly marked **not on file** rather than filled with a remembered or estimated consensus number, and the required two-sub-column commentary structure (prior commentary sourced / current explanation owner-required), both left blank for the same reason the options-signal section in `evidence-audit.md` was left blank — no provider is wired up for this desk.

This produced a materially thinner pack than the chapter's worked example, which is the point: the chapter says a complete pack for thin data, honestly labeled, is more valuable than a confident-looking pack that papers over its gaps. Rather than estimate a plausible consensus figure from memory (which would violate the desk's standing rule against generating figures no source produced), the pack states the gap and what would close it — a named consensus-data provider (e.g., a licensed estimates feed), not currently in scope per `sources-of-truth.md`.

## Exercise 4 — CLI Exercise

Attempted to build `book/returns-vs-benchmark.md` per the chapter's script. `book/positions.csv` and `benchmark/spy.csv` do not exist in this desk — I hold no real position in META or any other ticker; this project is a research and judgment exercise, not a live book. Per the task's own stop condition ("if positions.csv has a missing price or weight, halt and list the offending rows — do not impute values"), the correct action on a missing *file* is the same halt-don't-impute discipline, one level up: the script did not run, and no return figures were fabricated to fill the report.

`book/returns-vs-benchmark.md` was still written, but as a halted-run record rather than a populated table — it states what inputs are required, that neither exists yet, and that no computation was attempted. This is consistent with `CANNOT-KNOW.md`'s existing charter (no real financial picture is claimed for me by this desk) and keeps the desk's no-fabrication rule intact rather than inventing a demo portfolio to make the exercise look complete.

Per the exercise's own instruction, added to `CLAUDE.md`: "Account/return data is read-only. Never connect to a brokerage. Never place or suggest trades. Halt on missing data rather than imputing."

## Exercise 5 — AI Validation Exercise

Checked `theses/META/earnings-surprise-FY2025.md` against the chapter's validation checklist:

- **Correctness.** Pass. Every reported figure in the pack ties to a cell already confirmed in `theses/META.md` or its underlying 10-K/press-release sources — no new figures were introduced.
- **Completeness.** Fail, disclosed as such. The pack is missing consensus and forward-guidance comparisons for every line except the one place management gave forward-looking language at all (the 2026 Reality Labs loss guidance). This is stated in the pack itself, not silently omitted.
- **Scope.** Pass. The pack is confined to META, FY2025, with no cross-ticker or cross-period figures folded in.
- **Variance integrity.** Cannot determine for the consensus columns, since no consensus/guidance version is on file to compute a variance against; the one variance that *can* be computed (actual vs. the Reality Labs 2026 guidance) can't be evaluated yet because 2026 results aren't reported.
- **Gate discipline.** Pass. The "current explanation" column is blank throughout, and no causal language appears anywhere in the pack.
- **Failure-mode check.** Pass. No fluent-but-ungrounded consensus figure was substituted for the missing data; the gap is flagged as NEEDS HUMAN (a named consensus-data provider) rather than filled.

AI Use Disclosure: The AI structured the variance-pack template and populated it only with figures already confirmed against Meta's FY2025 10-K and press release; it declined to estimate or recall a consensus figure from training data and left every current-explanation cell blank. It could not determine whether the pack is adequate for any decision, since the one comparison the chapter is built around — actual vs. consensus — is currently unsourced on this desk.

## Update — 2026-07-23: both gaps closed with real, human-supplied data

The two "not on file" gaps above were subsequently closed, not by the assistant fetching anything, but by the human supplying real data directly:

- **Consensus data.** I pasted Yahoo Finance's analyst-consensus revenue/EPS figures for Q2 2026 / FY2026 / FY2027. Since this consensus data covers *future*, not-yet-reported periods (not FY2025, which was already closed), it was logged as its own contract, `evidence/consensus-estimates-Q2-2026.md`, and used to build a second, separate pack, `theses/META/earnings-surprise-Q2-2026.md`, rather than retrofitted onto the FY2025 pack — a live example of the chapter's mapping/period-consistency check catching a real period mismatch. The FY2025 pack (`earnings-surprise-FY2025.md`) is unchanged and still correctly shows "not on file" for FY2025 consensus, since no consensus data for that already-closed period was ever supplied. The Q2 2026 pack's actual-vs-consensus cells stay marked **PENDING** until Meta reports.
- **Portfolio data.** I supplied real entry/current prices for META, AAPL, and SPY (bought 2026-05-01) and asked the assistant to assign any weights that summed to 1. `book/positions.csv` and `benchmark/spy.csv` were created with this data (SPY doubling as both a 25%-weighted holding and the benchmark), and `book/returns-vs-benchmark.md` was rebuilt as a fully populated, ranked contribution table with a passing verification step (independently re-summed contributions matched the total return exactly). The template files (`positions.csv.template`, `spy.csv.template`) and their explainer README, no longer needed once real data existed, were archived rather than deleted, per this repo's no-delete rule.

Both updates stayed inside the exercise's stop conditions: no brokerage connection was made, no trade was placed or suggested, and the weights (assistant-assigned) are explicitly logged as illustrative, not a real allocation decision.
