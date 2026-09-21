# Final QA — mycroft_phase3_4k_9x16.mp4

Run: `python phase3_video.py full`, 2026-09-20. Full output in `outputs/render_log.txt`.
Render: 5,301 frames in 7.1 minutes, 27.9 MB.

## Format, sync and layout

| Check | Result |
|---|---|
| Resolution 2160 × 3840 (true 4K portrait) | PASS |
| Aspect ratio 9:16 | PASS |
| Frame rate 30 FPS | PASS |
| Duration inside 2–3 minutes (176.70 s) | PASS |
| Frame count matches the beat timeline (5,301) | PASS |
| Audio stream present (AAC 48 kHz stereo) | PASS |
| Audio and video durations within 0.1 s (176.70 / 176.70) | PASS |
| Captions end before the video ends | PASS |
| No caption longer than 42 characters | PASS |
| Nothing drawn outside the mobile-safe area | PASS |

## Content accuracy (checked automatically at render time)

| Check | Result |
|---|---|
| 9,636 anomaly events (3,972 / 3,397 / 2,267) | PASS |
| Market state `normal`, 12 stress windows | PASS |
| Overall reliability 0.516 [0.505, 0.526] | PASS |
| Bull / high-volatility segment 0.774 | PASS |
| All 120 tickers labelled `uncertain` | PASS |
| Five agents with the statuses from the orchestrated run | PASS |
| Validation suite 33/33 | PASS |
| `human_decision` left empty in the aggregation code shown | PASS |

18 of 18 checks pass.

## Manual review

Checked against `outputs/contact_sheet.jpg` and the eleven stills in `scenes/`:

- Every class name on screen matches the notebook: `AgentConfig`, `SharedContext`, `BaseAgent`, `AgentResult`, `AgentEvent`, `MycroftData`, the five agents, `MycroftOrchestrator`, `run_validation_suite`.
- Code panels hold 4–7 lines each and stay legible at phone size; the smallest type in the film is 28 px at 4K.
- Captions never overlap content, which stops at y 2660.
- The three notebook figures with fine detail (cohesion timeline, event timeline, reliability forest) are shown large with their own captions, not shrunk beside text.
- The peer-cluster graphic carries its "schematic - illustrates the method, not notebook data" label on screen.
- The advisory boundary appears in full in B10 and again in the closing beat.
- No frame implies autonomous trading or an investment recommendation.

## Fixed during production

| Issue | Fix |
|---|---|
| Agent 5, review-queue, Agent 3 and Agent 4 code panels sat low enough to collide with the caption band | Optional label chips, tighter figure heights, reordered B10, smaller repositioned schematic |
| The peer schematic's label sat on top of the moving node | Node path and labels repositioned, with a connector line to the cluster |

## Known gaps (stated, not hidden)

- Five Phase 3 charts were not exported, so Agents 3 and 4 appear without their notebook figures. See `ASSETS.md` for the file names and how to add them.
- Cohort counts and risk-tier counts are not quoted, because the successful orchestrated run does not print them.

## Re-verifying

```bash
python phase3_video.py full      # reprints all 18 checks
python make_project_data.py      # re-probes the MP4 and rewrites the JSON docs
```
