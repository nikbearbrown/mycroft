# Chapter 6, Exercise 5 — Validation Record

**Artifact validated:** `theses/earnings-surprise-STM-Q2-2026.md`

## Validation Checklist Results

| Check | Result | Reasoning |
|---|---|---|
| Correctness | Pass, with limitation | Reported figures tie to STM's press release; consensus figures tie to Zacks-sourced reporting, with a minor cross-source disagreement ($3.45B vs $3.46B) surfaced rather than hidden. |
| Completeness | Fail (partial, honestly) | Gross margin and net income lines could not be flagged — no consensus estimate found for those specific lines anywhere searched. |
| Scope | Pass | Confined to STM Q2 2026 only. |
| Variance integrity | Pass, with flagged discrepancy | Computed against stated consensus; separately surfaced that Q3 guidance itself is reported inconsistently across sources ($3.70B midpoint vs. $3.52-3.88B range). |
| Gate discipline | Pass | "Current explanation" column genuinely blank — no causal language for the EPS beat. |
| Failure-mode check | Pass, real catch | Surfaced a guidance-figure discrepancy that directly threatens the precision of the pre-committed Q3 exit signal in `CANNOT-KNOW.md`. |

**Verdict:** Passes overall. The completeness gap (gross margin/net income consensus unavailable) is correctly left as "cannot compute" rather than estimated. The guidance discrepancy is a genuine finding requiring human resolution before Q3.

**AI Use Disclosure:** The AI retrieved and structured consensus estimates from public reporting, computed variances, and left every causal-explanation cell blank. The AI could not determine why EPS beat consensus by 19.2% (share buybacks, tax rate, one-time items, or genuine operating strength are all plausible and untested here), and could not resolve which of two conflicting Q3 guidance figures is authoritative — both remain open human tasks.
