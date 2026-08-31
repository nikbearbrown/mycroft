# Evidence Audit: STM

Audits every metric and signal on `theses/human-card-STM.md` against the six adequacy dimensions from Chapter 5, before any of it is allowed to inform the decision block.

**Note on scope:** This desk has no options-signal thesis for STM (confirmed in `theses/agent-recipe-STM.md`: "no options-chain inputs — no options thesis exists for STM on this desk yet"). The signal-specific columns below are marked N/A, not skipped — there is nothing to audit because nothing was ever claimed.

## Metric Audit

| Item | Source it ties to | Completeness | Freshness | Control total | Mapping/period consistent? | Warranted-verb level it should use | Adequate for the decision? |
|---|---|---|---|---|---|---|---|
| STM Q2 2026 revenue ($3.49B, +26.0% YoY) | STM Q2 2026 press release | Covers full consolidated entity, not just a segment — matches how the release itself reports it | Freshly pulled, same period as the claim | Ties directly to the press release's own headline figure | Period consistent — same fiscal Q2 comparison basis used throughout | **Can say** — this is a directly reported figure, reconciled to the release itself | [BLANK — yours to judge] |
| STM Q2 2026 margin drag ("~60bps from manufacturing-reshaping costs") | STM Q2 2026 earnings call transcript | Complete as a management statement, but this is a single disclosed figure, not a full breakdown of all cost components | Freshly pulled, same call | No independent control total exists to tie this to — it is a management-disclosed figure, not a reconciled line item from a filing table | Consistent — management stated it will persist "at similar level over the rest of the year" | **Can say** for the fact that management disclosed this; **can suggest** (not "can say") for any implication about how much it will matter going forward | [BLANK] |
| "the market saw through it" (claim 5, `theses/STM.md`) | Partial — AMD/Intel same-day moves (context-only tier per `sources-of-truth.md`), NXPI/ASML unconfirmed | **Incomplete** — two of four comparison names (NXPI, ASML) were never actually pulled for the specific date | N/A — data was never retrieved | No control total — this was never a reconciled figure, it's an inference | N/A | **Needs review** — currently mis-stated as "inferred" in `STM.md`; on reflection, this claim probably belongs closer to "cannot claim" until the missing two names are actually checked, given genuinely half the comparison set is missing | [BLANK] |
| Q3 2026 gross margin (pending) | STM Q3 2026 press release — **does not exist yet** | N/A — no data to audit | N/A | N/A | N/A | **Cannot claim anything yet** — this entire line is a future data point, not current evidence | [BLANK — not applicable until the release happens] |

## Signal Audit

**N/A across the board.** No options-chain data has been pulled for STM, and no options thesis exists on this desk. There is no expiration window, no term structure, and no positioning-vs-noise question to screen, because no options claim was ever made. Flagging this explicitly rather than leaving it blank, since a blank signal section could be misread as "not checked" rather than "correctly not applicable."

## Causal claims that the evidence only supports as correlation

- **"the stock dropped because of margin pressure"** — the evidence establishes that margin pressure is real and disclosed (can say), and that the stock dropped 13% the same day (can say), but the *causal link between the two* is not established by anything retrieved. This is the same gap already flagged in `theses/STM.md` claim 5, now confirmed by this audit as more serious than "inferred" — see the Completeness cell above.

## What this audit actually changed

Doing this properly surfaced something the earlier, faster claim-audit missed: claim 5 was tagged "inferred" in Chapter 2 based on *half* the comparison set (AMD and Intel only). Auditing it against the actual completeness dimension shows that's not "inferred" so much as "an inference built on an incomplete comparison" — which is weaker than the earlier tag implied. This should be corrected in `theses/STM.md`, not left as-is.

**NEEDS HUMAN:** Whether this reclassification (inferred → cannot claim, pending the NXPI/ASML data) actually matters enough to revisit the still-open decision from earlier (whether closing that gap is worth the effort at all). This audit makes a slightly stronger case that it's worth closing than the earlier "probably not worth it" judgment did — but that's a judgment call, not a fact this audit can settle.
