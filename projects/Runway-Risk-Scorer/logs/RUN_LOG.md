## 2026-08-21 — Week 2 sample run (step-split + JSON output)
- command: python scripts\runway_risk_score.py data\samples\sample_signals.json --json-out reports
- result: 4 companies scored. harbor-ai used 3 signals (1 distress, 93 days fresh);
  lumen-labs used 2 (0 distress, 1684 days fresh — stale); vela-systems used 3
  (0 distress, 37 days fresh); orphan-co used 0, dropped 1 unvalidated signal.
  JSON written to reports\ (4 files). All briefs halted at the human gate. Exit 0.
- steps confirmed: ingest -> validate_shape (drops unvalidated) -> score -> report(human + JSON).
- gate decision: acting-reviewer SOLO — run confirms the step-split produces the
  same briefs as Week 1 and the JSON carries full provenance. Adequate to mark SPECIFIED.
- could NOT verify (solo): real-world accuracy of the signals, whether the 5 metrics
  match actual procurement needs, independent adequacy review.
## 2026-08-28 — caught-up run (Rows 3-4 closed, Week 4 rigor added)
- OVERLAP_CHECK.md written: no runway recipe exists in the 100 Mycroft recipes.
- recipe bumped DRAFT -> SPECIFIED (step-split + JSON + logged run as evidence).
- Week 4 metrics added: trailing-window activity + signal-velocity delta.
- break tests: 7/7 pass. Caught a malformed-date crash; fixed with safe_date().
- audit_freshness: 5 stale signals flagged, 1 unvalidated, 0 hard problems.
- gate: acting-reviewer SOLO. Ready to advance to RUNNABLE-SAMPLE once Week 4 is committed.
- could NOT verify (solo): real-world signal accuracy, independent review.
