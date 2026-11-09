# Sources of Truth — NVDA Desk  
Where every number I act on is allowed to come from. Ranked by authority.  
Rule: a number is only "verified" when I have opened a Tier-1 source and read it myself.

## Sources of truth (verify against these)  
- SEC EDGAR — NVDA's 10-K (annual) and 10-Q (quarterly) filings. The authoritative  
  source for all financials: revenue, segment breakdowns, EPS, everything I'd act on.  
  When I mark a number "verified," it ties to a specific line in one of these filings.

## Context only (read, but never verify against)  
- Stock Analysis (stockanalysis.com) — convenient pre-computed metrics and history.  
- Yahoo Finance — quick quotes, ratios, charts.  
- Macrotrends — clean long-run historical series.  
  All three are aggregators: useful for orientation and quick looks, but they pull  
  from filings and can lag, err, or use their own definitions (e.g. which growth  
  figure feeds PEG). Anything I'd act on gets traced back to EDGAR.

## Not a source (generates questions, never answers)  
- Tweets, Reddit, pundit videos, news hype.  
- Any AI paragraph, including my own tools' output.  
  These can suggest what to look into. They can never confirm a number.

## Options provider  
- None for now. Options signals are in BACKLOG.md (decided as noise in Chapter 2).  
  If I ever pull that work forward, I'll add a named provider (e.g. CBOE or my  
  brokerage's options chain) as a Tier-1 source at that time.  




## Exercise 5 — Validation (human-run gate)

Checklist run against sources-of-truth.md + the evidence stubs:
1. Correctness — PASS. Only EDGAR is Tier-1; data sites correctly demoted to context.
2. Completeness — PASS. All three decision-moving metrics have contract stubs with all fields.
3. Scope — PASS. No value, accession number, or "verified" mark was filled by the AI.
4. Provenance — PENDING (correct). Stubs are blank until I open the filings myself.
5. Source-tiering — PASS. Tweets/news/AI output all in "context only" or "not a source."
6. Failure-mode check — PASS. No hallucinated numbers or accession IDs; nothing feels verified yet.

Result: all pass → start filling the contracts against real EDGAR sources.

## AI Use Disclosure
Claude organized my named sources into three tiers and built empty data-contract
stubs for each decision-moving metric; I used these as a scaffold and will fill and
verify every cell myself against the actual EDGAR filings. Claude could not
determine whether any source is truly authoritative or whether a number ties to its
filing — that verification is mine to do by opening the source.