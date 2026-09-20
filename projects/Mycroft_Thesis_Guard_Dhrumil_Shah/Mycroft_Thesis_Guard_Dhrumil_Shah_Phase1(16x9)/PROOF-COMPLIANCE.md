# Feedback: “Mycroft ThesisGuard — 3-minute evidence review” — Dhrumil Shah, film 1

**Verdict:** clear-for-public. Teaching score **12/12**. Production gate
**PASS**.

This film teaches an evidence-first review method through a reusable framework
and worked Mycroft case. The final 4K master was checked at every primary beat,
including the full auditable loop and viewer scaffold; the framework precedes
results, sources remain on screen, and missing evidence visibly stops the
system.

## Rubric

| Criterion | What it means | This cut |
|---|---|---|
| Explicit framework | A structure is shown before examples | **2** — 00:00–00:14 shows Claim → Evidence → Uncertainty → Human; 00:14–00:35 adds the presenter-labelled review scaffold. |
| Reusable rubric | Viewer can apply the axes to a new case | **2** — 02:33–02:45 provides claim, linked sources, disconfirmer, evidence date, uncertainty, and human-review prompts. |
| Worked example | A case is walked through, not merely asserted | **2** — 01:12–01:36 shows the selected model, real holdout values, drift, and the reported weak conclusion. |
| Falsifiability / edge case | Method is stress-tested by ambiguity | **2** — 01:36–02:23 shows missing thesis/decision evidence leading to `needs_human_input` / human review. |
| Active task | Viewer does a structured action | **2** — 02:33–02:45 is an on-screen reviewer scaffold, not a generic AI prompt. |
| Friction | Viewer resolves a real tension | **2** — weak predictive performance and moderate drift are presented as governance signals, not success. |
| **Total** |  | **12/12** |

## Production gate

| Gate | Final-master evidence | Status |
|---|---|---|
| Evidence legible at moment of assertion | 12 encoded 4K stills inspected: executive summary, framework, data, method, results, stop condition, human gate, evidence boundary, completed loop, scaffold, and close. No clipped headline, source tag, card, or core artifact found. | PASS |
| Sources on screen, not just voiced | Every factual scene retains a persistent source tag and/or captured notebook/report artifact in the encoded master. | PASS |
| Side-by-side at moment of comparison | 02:14–02:23 holds Available vs Not Supplied together for 9.3 seconds; the encoded still confirms both columns and returned status remain readable. | PASS |

## Final technical and visual QA

- Master: `output/mycroft-thesisguard-brief-4k.mp4`
- Verified: 3840×2160, 24 fps, H.264/AAC, 180.011 seconds, 42.99 MiB.
- Visual review: ten scripted QA stills plus the completed-loop and
  completed-scaffold stills in `_qc/final/`.
- Result: no blocking visual or source-on-screen defect found.

## Known evidence limitation

Scene 09 uses the authentic Cell 50 record of nine figure filenames. The raw
plot assets were not supplied, so it explicitly does **not** present invented
diagnostic, calibration, or drift charts. This is PARTIAL visual-analytics
coverage, not a hidden failure.

## Compliance matrix

| PROOF requirement | Video scene / timestamp | Evidence displayed | Source | Status |
|---|---|---|---|---|
| Framework before examples | 01–02 / 00:00–00:35 | Claim/Evidence/Uncertainty/Human plus review scaffold | Presenter-labelled structure | PASS |
| Visible support for facts | 03–09 | Source tag plus notebook/report captures | `assets/evidence/*`; Cells 5, 13, 21, 25, 50, 69 | PASS |
| Worked example | 05 / 01:12–01:36 | Logistic Regression result, AUC 0.5158, Brier 0.2466, drift | Cell 25; Report §4 | PASS |
| Falsifiability / stop condition | 06–08 / 01:36–02:23 | Missing-evidence statuses and side-by-side boundary | Cell 21 | PASS |
| Active viewer task | 10 / 02:33–02:45 | Six-row reviewer scaffold | Presenter scaffold | PASS |
| Raw plot display | 09 / 02:23–02:33 | Figure-file creation record, not plots | Cell 50 | PARTIAL |
| Live UI / fresh execution | — | Not claimed | Supplied project inventory | NOT DEMONSTRATED |

## The problem

No blocking PROOF problem remains in the rendered cut. The only material
limitation is intentional and visible: the project supplied the record of
nine generated figure files, not the raw chart files themselves.

## Do X next week

1. **[RESHOOT/NEW SOURCE]** If the original output directory becomes
   available, replace the Scene 09 filename record with the actual plots while
   keeping the same provenance label.
2. **[EDIT]** Align the local Remotion package versions before a future
   rebuild to remove its non-blocking version warning.
3. **[RESHOOT/NEW SOURCE]** Capture a verified notebook rerun only when the
   original data/environment is available; never substitute a mock terminal.

## What works

The film's strongest choice is that it treats weak predictive performance and
missing decision evidence as the teaching moment. The result, stop condition,
and human gate stay aligned: Mycroft organizes evidence, then a person owns
the judgment.
