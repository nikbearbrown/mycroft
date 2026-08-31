# Chapter 5, Exercise 5 — Validation Record

**Artifact validated:** `theses/evidence-audit-STM.md`

## Validation Checklist Results

| Check | Result | Reasoning |
|---|---|---|
| Correctness | Pass | Completeness/freshness/control-total checks match the actual underlying sources. |
| Completeness | Pass | Every metric audited, including pending (Q3) and N/A (signals) items, both explicitly marked rather than silently skipped. |
| Scope | Pass | No adequate/material/real-signal call made — all left blank. |
| Signal vs noise | Pass (trivially) | Correctly states no options signal exists to screen, rather than fabricating one. |
| Causal check | Pass | Cleanly separates "margin pressure is real" and "stock dropped" (both can-say) from "margin pressure caused the drop" (not established). |
| Failure-mode check | Pass, with a real catch | This audit found that claim 5 in `theses/STM.md` was tagged more confidently ("inferred") than the actual evidence supported, and corrected it to "cannot claim." |

**Verdict:** Passes. This is the first exercise in the series to materially correct a prior chapter's output rather than just extend it — exactly what an adequacy audit is supposed to do.

**AI Use Disclosure:** The AI ran the six-dimension adequacy check against each metric and surfaced a completeness gap in claim 5 that a faster read had missed. The AI could not determine whether that correction is enough reason to actually close the NXPI/ASML gap now — that remains the human's call, logged as still-open-but-somewhat-more-worth-doing in `theses/human-card-STM.md`.
