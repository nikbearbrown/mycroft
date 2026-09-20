# Optional screen-recording plan

The current master deliberately uses only supplied static evidence because the
project inventory did not provide a runnable Mycroft app, dataset, or verified
output directory. Do **not** substitute a mocked terminal/UI for a recording.

If Dhrumil runs the original notebook in a verified environment later, capture
these short inserts and replace only the matching evidence panels:

| Insert | Window / action | Expected authentic evidence | Use only if it really appears |
|---|---|---|---|
| Data and feature receipt | Open `Mycroft-Project_Dhrumil.ipynb`; scroll to Cells 5 and 13; run only with the original data already configured | Feature definitions and chronological split output | Scene 03 / 04 |
| Evaluation receipt | Open Cell 25; execute using the original environment; wait for completion | The exact recorded results: selected model, 0.5158 AUC, 0.2466 Brier, drift, counts | Scene 05 / 07 |
| Agent boundary | Open Cell 21; show the agent class/status return, not a hand-edited output | `needs_human_input`, `not_assessed`, `human_review_required` as actually returned | Scene 06 / 08 |
| Figure evidence | Open the actual output directory only if the nine chart files exist | The actual rendered plots and filenames | Scene 09 |

For each capture: use a 4K desktop, hide notifications/private data, keep the
notebook cell header and output visible, do not type invented values, pause
two seconds on the relevant result, and record losslessly or at 4K/24–30 fps.
Cursor movement should merely point to the relevant cell/output. If the source
does not run or differs from the supplied record, label the discrepancy rather
than editing the evidence to match.

