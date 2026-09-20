# Films — 9:16 vertical recomposition

10 scenes ("films"), one React component each, all in the single composition
source file `../src/MycroftThesisGuardBrief9x16.tsx`. This mirrors the
approved 16:9 project's actual convention: one TSX file containing all scene
components, not one file per scene. The frame ranges below are computed from
the same 16 narration-beat durations as the 16:9 master and are identical to
it — see `../config/films-manifest.json` for the machine-readable version of
this table.

## Film 01 — Executive summary
- **Purpose:** Introduce Dhrumil Shah and the film's review question in the
  cold open.
- **Duration:** 337 frames / 14.04 s (audio beat B00)
- **Narration:** "Hi, I'm Dhrumil Shah. A three-minute evidence review of
  what Mycroft ThesisGuard does..."
- **Visuals:** Title card, "THE REVIEW QUESTION" card, 4-step review chain
  (Claim → Evidence → Uncertainty → Human).
- **Animations:** Spring-in title, staggered card reveal, staggered chain
  reveal with down-arrow connectors.
- **Assets:** None (text/graphics only).
- **16:9 source film:** `OpeningScene` in `../src/MycroftThesisGuardBrief.tsx`.
- **9:16 layout changes:** The 4-step chain was a horizontal row with
  right-arrows in 16:9; here it is a vertical stack with down-arrows.

## Film 02 — The problem and the review frame
- **Purpose:** Explain "thesis drift" and introduce the presenter's CLEAR
  review framework.
- **Duration:** 498 frames / 20.75 s (beats B01–B02)
- **Narration:** Covers thesis drift and the CLEAR framework.
- **Visuals:** Headline, evidence image, illustrative-example pair, CLEAR
  5-letter grid.
- **Animations:** Staggered reveals; CLEAR grid gated on frame 270–315.
- **Assets:** `report-problem-boundary.png`.
- **16:9 source film:** `ProblemFrameworkScene`.
- **9:16 layout changes:** Evidence image moved below the headline
  (was beside it). Illustrative/facts pair stacked top-to-bottom with a down
  arrow (was side-by-side with a right arrow). CLEAR grid changed from one
  5-across row to a 3+2 grid.

## Film 03 — Validated inputs and causal features
- **Purpose:** Show the real data scale and the no-lookahead rule.
- **Duration:** 500 frames / 20.83 s (beats B03–B04)
- **Narration:** Data validation and causal-feature discussion.
- **Visuals:** Evidence image, 4-stat 2×2 grid, features card.
- **Animations:** Staggered stat reveals.
- **Assets:** `notebook-features.png`.
- **16:9 source film:** `DataScene`.
- **9:16 layout changes:** Evidence image and stat grid were two side-by-side
  columns; now a single full-width stack (image → stats → features card).

## Film 04 — Chronological evaluation
- **Purpose:** Explain the time-based train/validate/holdout split and the
  five benchmarked models.
- **Duration:** 390 frames / 16.25 s (beats B05–B06)
- **Narration:** Split methodology and baseline benchmarking.
- **Visuals:** Evidence image, proportional split bar, 5-model list.
- **Animations:** Staggered reveals down the model list.
- **Assets:** `notebook-time-split.png`.
- **16:9 source film:** `MethodScene`.
- **9:16 layout changes:** 5-model row (horizontal cards) became a
  single-column stacked list. Split bar kept horizontal (it is inherently a
  proportion bar and still reads correctly at portrait width).

## Film 05 — The worked result
- **Purpose:** Present the honest, weak result as a finding, not a failure to
  hide.
- **Duration:** 570 frames / 23.75 s (beats B07–B08)
- **Narration:** ROC AUC, Brier score, and drift discussion.
- **Visuals:** Outcomes-table evidence image, 4-stat 2×2 grid, summary card.
- **Animations:** Staggered stat reveals.
- **Assets:** `report-and-run-outcomes.png`.
- **16:9 source film:** `ResultsScene`.
- **9:16 layout changes:** Evidence image and stat grid stacked full-width
  instead of side-by-side; image given a taller crop window to keep the
  table's numbers legible.

## Film 06 — Falsifiability: the system may stop
- **Purpose:** Show the system refusing to guess when a thesis/source is
  missing.
- **Duration:** 403 frames / 16.79 s (beat B08b)
- **Narration:** Discusses `needs_human_input` and unassessed bias.
- **Visuals:** Evidence image, 3-stat vertical stack, "NO SOURCE · NO
  VERDICT" line.
- **Animations:** Staggered stat reveals.
- **Assets:** `notebook-agent-classes.png`.
- **16:9 source film:** `StopScene`.
- **9:16 layout changes:** 3-stat column widened to the full safe-area width.

## Film 07 — Agent workflow and human gate
- **Purpose:** Show the five-agent pipeline ending in a mandatory human gate.
- **Duration:** 508 frames / 21.17 s (beats B09–B10)
- **Narration:** Walks the five agents and the run's totals.
- **Visuals:** 5-agent vertical chain, 3-stat outcome row.
- **Animations:** Staggered chain reveal with down-arrows; outcome row gated
  on frame 230–265.
- **Assets:** None (text/graphics only).
- **16:9 source film:** `AgentsScene`.
- **9:16 layout changes:** 5-agent horizontal chain (right-arrows) became a
  vertical chain (down-arrows). Outcome row kept as a 3-column grid.

## Film 08 — Evidence boundary
- **Purpose:** Draw the line between market evidence and decision evidence.
- **Duration:** 223 frames / 9.29 s (beat B11)
- **Narration:** "No source, no verdict."
- **Visuals:** Available vs. not-supplied comparison, returned-status card.
- **Animations:** Staggered card reveals.
- **Assets:** None (text/graphics only).
- **16:9 source film:** `EvidenceBoundaryScene`.
- **9:16 layout changes:** Two-column comparison became a top/bottom stack.

## Film 09 — The auditable loop
- **Purpose:** Show the full pipeline as a chain of inspectable artifacts.
- **Duration:** 251 frames / 10.46 s (beat B12)
- **Narration:** Walks the six pipeline stages and the visualization record.
- **Visuals:** 6-stage vertical chain, evidence image, description card.
- **Animations:** Staggered chain reveal with down-arrows.
- **Assets:** `notebook-visualization-scope.png`.
- **16:9 source film:** `LoopScene`.
- **9:16 layout changes:** 6-stage horizontal chain became a vertical chain.
  Evidence image and its description card, previously side-by-side, are now
  stacked.

## Film 10 — Your turn and close
- **Purpose:** Hand the viewer a reusable review scaffold, then close on the
  title.
- **Duration:** 640 frames / 26.67 s (beats B12b–B13)
- **Narration:** The 6-row CLEAR scaffold, then the title restate.
- **Visuals:** 6-row numbered scaffold list, crossfade to centered title card.
- **Animations:** Staggered row reveal, crossfade from scaffold to outro at
  the B12b/B13 boundary.
- **Assets:** None (text/graphics only).
- **16:9 source film:** `YourTurnCloseScene`.
- **9:16 layout changes:** The scaffold list was already vertical in 16:9;
  widened to the portrait safe-area column with reduced font sizes. Title
  card kept centered with reduced font sizes to fit the narrower canvas.
