# Consolidated video-generation prompt — Mycroft Phase 3 (16:9)

Reusable brief that reproduces this film. Paste it wherever the video is rebuilt, or adapt it for a later phase. It is descriptive of what was actually built, so anything it claims can be checked against `FACTCHECK.md`.

---

## Brief

Create a professional 16:9 landscape technical demonstration video, 3840 × 2160, 30 FPS, H.264 + AAC, 2–3 minutes, covering **only** the Phase 3 section of `Mycroft_Dhrumil2.ipynb` — "Mycroft_Dhrumil_Shah_Phase_3 (Building more AI agents)", cells A1–A13. Earlier phases appear only where Phase 3 consumes their outputs: the Phase 1 cleaned price panel, `latest_company_predictions.csv`, `test_predictions.csv.gz`, and the Phase 2 regime labels.

**Open with, word for word:** "Hi, I am Dhrumil Shah, and this video is about Phase 3 of my Mycroft project, where I expanded the system by building a modular multi-agent financial analytics architecture for market structure analysis, anomaly detection, peer benchmarking, tail-risk and liquidity analysis, and prediction reliability." Then show the title card **MYCROFT — PHASE 3 / Building More AI Agents** with the five agents forming around a central Mycroft / SharedContext hub.

**Cover, in this order, using the exact class names:** `AgentConfig`, `SharedContext`, `BaseAgent`, `AgentResult`, `AgentEvent` (B02); `MycroftData` and the loading and validation workflow (B03); `MarketStructureAgent` (B04); `AnomalyEventAgent` (B05); `PeerCohortBenchmarkAgent` (B06); `TailRiskLiquidityAgent` (B07); `PredictionReliabilityAgent` (B08); `MycroftOrchestrator` and its three stages (B09); the aggregated human-review queue (B10); `run_validation_suite` and the closing summary (B11).

**Close with:** "Phase 3 expands Mycroft into a modular, explainable multi-agent analytics system where specialised agents produce structured evidence for human review. I'm Dhrumil Shah. Thank you for watching."

## Accuracy rules

1. Read every Phase 3 cell before writing a word of narration.
2. Use only classes, thresholds, formulas, statuses and figures that exist in the notebook.
3. Take numbers from executed notebook output, never from estimation: mean correlation 0.148, PC1 share 19.7 %, market state `normal` on 2026-02-11, 12 stress windows, 9,636 anomaly events (3,972 idiosyncratic / 3,397 market-wide / 2,267 sector-wide), overall reliability 0.5158 [0.5054, 0.5263], bull / high-volatility 0.7737 on 720 rows, all 120 tickers labelled `uncertain`, agent statuses and durations from the orchestrated run, 33/33 validation checks.
4. Where the notebook prints no number (cohort counts, risk-tier counts), show the method and the documented thresholds instead of inventing totals.
5. Mark any illustrative graphic as a schematic on screen.
6. Report degraded, uncertain and `insufficient_sample` outcomes honestly; never crop a chart to hide them.
7. Describe deterministic statistics as statistics — eigenvalues, medians and MADs, quantiles, percentile ranks, bootstrap intervals — and never as a language model.
8. Frame the system as analytical decision support: "the agents generate structured evidence and risk signals for human review". Never suggest it decides trades.
9. Keep the advisory boundary on screen: "Educational research output from Mycroft. Not personalized financial advice or an investment recommendation."
10. If a saved notebook output is stale (an earlier cell that failed against an older config), use the later successful run and say which one was used.

## Visual specification

Dark AI / FinTech interface: background gradient #080E1C → #101A30 with a faint grid; teal #2DD4BF primary, blue #388BFD, violet #A78BFA, amber #FBBF24 for callouts and flags, red #F87171 for risk, green #4ADE80 for passing checks. DejaVu Sans for text, DejaVu Sans Mono for code. Two-column grid: charts and figures beside their explanation, short labels, one full-width table only where it fits comfortably.

Safe area: content between x 180–3660 and y 470–1700 on a two-column grid (1680 px columns, 120 px gutter); frame furniture at y 150–390; captions centred at y 1900.

Motion: 0.35 s fade in, 0.30 s fade out per beat; elements rise 50 px on a cubic ease-out; chains reveal node by node; bars and tables grow with the narration; notebook figures get a 3.5 % Ken-Burns zoom; paired panels crossfade over 0.5 s. No spins, bounces or flying text.

Code panels: 4–7 real lines each, syntax-highlighted, auto-sized to the column, with an animated callout on the line under discussion and a short plain-English label ("Shared communication layer", "Detecting abnormal market events", "Benchmarking against peer cohorts", "Measuring downside tail risk", "Testing model reliability by segment", "Coordinating specialized agents").

## Audio and captions

Professional male English voice at 140–155 words per minute, confident and conversational (edge-tts `en-US-AndrewNeural` at +25 % here). Narration peak-normalised to −1 dBFS. Optional subtle futuristic instrumental bed at about −23 dB, looped and faded out. Burned-in captions of one line, 40 characters maximum, matching the narration word for word, plus an SRT sidecar.

## Delivery

`mycroft_phase3_4k_16x9.mp4` (3840 × 2160, 30 FPS, CRF 16, AAC 256 kbps, faststart), its SRT, per-beat stills, a contact sheet, the code-panel PNGs, and a documentation set: README, script, storyboard, code snippets, fact check, assets, specifications, QA, build log, plus `beat_sheet.json`, `captions/cues.json`, `audio/timings.json`, `data/phase3_results.json`, `config/video-config.json` and `video_manifest.json`.

## Quality gate before publishing

Resolution 3840 × 2160; aspect 16:9; 30 FPS; duration 2–3 minutes; audio and video within 0.1 s; captions end before the video does and never exceed 42 characters; nothing drawn outside the safe area; every spoken number matched against notebook output; class and agent names spelled exactly as in the code; the human-review boundary visible.
