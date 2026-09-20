# Sources — Mycroft ThesisGuard: Evidence Over Emotion (3-minute brief)

## Primary sources (evidence boundary)

Every figure spoken in this reel is copied from one of:

- `Mycroft-Project_Dhrumil.ipynb` — the recorded Cell 25 run output
  (`clean_rows`, `ticker_count`, split row counts, `validation_selected_model`,
  `selected_holdout_roc_auc`, `selected_holdout_brier_score`,
  `global_drift_severity`, `agent_report_count`, `agent_trace_event_count`,
  `human_decisions_created`), plus Cell 21 (the five agent classes and their
  returned status values) and Cells 50 / 69 (the rendered figure lists).
- `Mycroft_ThesisGuard_Project_Report_Dhrumil_Shah.docx` — Section 4 Outcomes
  table, which independently records the same values.
- `Dhrumil_Shah_Project_Proposal_Mycroft ThesisGuard.pdf` — the original
  design intent (five-agent workflow, thesis-drift framing).

Nothing is invented. No price, ticker, probability, performance, or drift
value appears that is not in one of those files.

## Figures spoken, and where each comes from

| Spoken | Value | Source |
|---|---|---|
| "one hundred eighty-four thousand rows" | 184,138 | Cell 25 `clean_rows`; Report Outcomes |
| "one hundred twenty tickers" | 120 | Cell 25 `ticker_count`; Report Outcomes |
| train / validate / held back | 127,858 / 26,880 / 27,600 | Cell 25 step 3; Report Outcomes |
| "logistic regression won" | logistic_regression | Cell 25 `validation_selected_model` |
| "zero point five one five eight" | 0.5158070034548209 | Cell 25 `selected_holdout_roc_auc` |
| Brier score | 0.24663154975271798 | Cell 25 `selected_holdout_brier_score` |
| "drift came back moderate" | moderate | Cell 25 `global_drift_severity` |
| 120 reports / 600 events / 0 decisions | 120 / 600 / 0 | Cell 25 agent counts |
| `not_assessed`, `needs_human_input` | verbatim | Cell 21 agent return values |

## Relationship to the reference reel

The supplied reference informed only the general production grammar: strong
editorial hierarchy, restrained color, one idea at a time, progressive
reveals, real evidence when a claim appears, and a concise title close. No
reference narration, exact wording, UI, screen capture, audio, scene code, or
creative asset is used. See [REFERENCE-ANALYSIS.md](REFERENCE-ANALYSIS.md).

## Current-render boundary

This 3-minute cut is the custom 180-second composition described by
[CURRENT-RENDER-MANIFEST.md](CURRENT-RENDER-MANIFEST.md). The opening gives
Dhrumil Shah's executive summary; the close gives a six-part reviewer scaffold
with claim, sources, disconfirmer, evidence date, uncertainty, and human
review. The retained JSON beat sheets are source/planning history, not this
render's implementation.
