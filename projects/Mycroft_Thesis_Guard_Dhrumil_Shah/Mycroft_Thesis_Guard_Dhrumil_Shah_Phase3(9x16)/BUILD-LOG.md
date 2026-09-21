# Build log — Mycroft Phase 3 video

## 1. Reading Phase 3

Read every cell of the Phase 3 section (`Mycroft_Dhrumil2.ipynb`, cells 100–127 = A1–A13) before writing narration: the framework classes, the data loader, the five agents, the orchestrator, the aggregation, the validation suite, and every printed output.

Three findings shaped the film:

- **The architecture is the story.** Phase 3's contribution is a framework — shared context, a base agent contract, standardised results and traceable events — with five specialised analysts on top, not a new model.
- **Some saved outputs are stale.** Cell A9 shows `PeerCohortBenchmarkAgent` and `TailRiskLiquidityAgent` failing with `AttributeError: cohort_outlier_percentile` and `KeyError: 'tail_risk'`. Those errors came from an older `AgentConfig`; the later orchestrated run in Cell A11 runs all five agents successfully. The video reports the successful run and `FACTCHECK.md` records the discrepancy.
- **The honest result is mixed.** Overall reliability clears 0.50, but all 120 tickers end up labelled `uncertain`, and the largest regime segment is uncertain too. The narration says so.

## 2. Assets available

Five of the ten Phase 3 charts were exported (`agent1_01`, `agent1_02`, `agent2_01`, `agent5_01`, `agent5_02`). The cohort and tail-risk figures were not. Rather than fabricate them, beats B06 and B07 use the real thresholds, formulas and pipeline structure, plus one schematic that is captioned as a schematic on screen.

## 3. Design reuse

`phase3_video.py` reuses cells 2, 3, 5 and 7 of the Phase 2 generator (`_phase2_helpers.py`) for the canvas, safe area, palette, text and card primitives, code panels and bar charts, then defines its own Phase 3 data, narration, visual helpers and eleven scenes. One design system across both films, without copying code by hand.

New visual components written for Phase 3: the agent ring, the labelled flow chain with sub-captions, the peer-decoupling schematic, the three-stage orchestration diagram, the review-queue table, the tier-threshold table, and the validation checklist.

## 4. Script

Eleven beats following the requested structure, 425 words at about 150 words per minute — inside the 140–155 target and the 2–3 minute limit, finishing at 2:57. The opening sentence is used verbatim as requested. Abbreviations are respelled for the speech engine only, so captions keep the code spelling.

## 5. Layout pass

The first `sheet` pass put four panels too low, where they would have collided with the caption band at y 2830: the Agent 5 code panel, the review-queue code, and the Agent 3 and Agent 4 panels. Fixes: an optional label chip under code panels, tighter figure heights on B08, a reordered B10, and a smaller, repositioned schematic on B06. After the fix, the safe-area tracker reported no violations.

## 6. Render

5,301 frames at 2160 × 3840, encoded with PyAV (libx264 CRF 16 + AAC 256 kbps, faststart), since local group policy blocks `ffmpeg.exe`. Audio is assembled on the beat timeline and peak-normalised to −1 dBFS; if `assets/background_music.mp3` exists it is looped and mixed at 0.07 gain.

## 7. Checks

Eighteen automated checks run at the end of every render: ten on format, sync, captions and safe area, eight on the Phase 3 facts. Results are in `FINAL-QA.md`.

## 8. Possible next steps

- Export the five missing Phase 3 charts and re-render to give Agents 3 and 4 their real visuals.
- Add a licensed music bed.
- Record the narration in your own voice (`narration/scene_XX_user.wav`).
- Produce a 16:9 cut, as was done for Phase 2, by re-laying out the eleven beats on a two-column landscape grid.
