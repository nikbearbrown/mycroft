# Final QA — mycroft_phase3_4k_16x9.mp4

Run: `python render_16x9.py full`, 2026-09-20. Full output in `outputs/render_log.txt`.
Render: 5,301 frames in 9.7 minutes, 31.6 MB.

## Format, sync and layout

| Check | Result |
|---|---|
| Resolution 3840 × 2160 (4K UHD landscape) | PASS |
| Aspect ratio 16:9 | PASS |
| Frame rate 30 FPS | PASS |
| Duration inside 2–3 minutes (176.70 s) | PASS |
| Same runtime as the 9:16 cut (within 0.05 s) | PASS |
| Frame count matches the beat timeline (5,301) | PASS |
| Audio stream present (AAC 48 kHz stereo) | PASS |
| Audio and video durations within 0.1 s (176.70 / 176.70) | PASS |
| Captions end before the video ends | PASS |
| No caption longer than 42 characters | PASS |
| Nothing drawn outside the safe area | PASS |

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

19 of 19 checks pass.

## Manual review

Checked against `outputs/contact_sheet.jpg` and the eleven landscape stills in `scenes/`:

- Both columns hold their 1680 px width on every beat; no panel crosses the gutter.
- Charts and code are larger than in the portrait cut, since they no longer share vertical space.
- Class names on screen match the notebook exactly, including `MycroftOrchestrator`, `PeerCohortBenchmarkAgent` and `PredictionReliabilityAgent`.
- The review-queue table regains its Sector column and still fits the content width.
- Captions at y 1900 never touch content, which ends at y 1700.
- The peer-cluster graphic keeps its "schematic - illustrates the method, not notebook data" label.
- The advisory boundary appears in B10 and again in the closing beat.

## Parity with the 9:16 cut

| Item | Status |
|---|---|
| Narration text | Identical (425 words, 11 beats) |
| Voiceover audio | The same MP3 files |
| Beat timings | Identical to the millisecond |
| Caption cues | 93 cues, identical text and timings |
| Numbers on screen | Identical, from the same notebook data |
| Layout | Re-composed for landscape (see `STORYBOARD.md`) |

## Known gaps (stated, not hidden)

- Five Phase 3 charts were never exported, so Agents 3 and 4 appear without notebook figures. `ASSETS.md` lists the filenames and how to add them.
- Cohort counts and risk-tier counts are not quoted, because the successful orchestrated run does not print them.

## Re-verifying

```bash
python render_16x9.py full       # reprints all 19 checks
python make_project_data.py      # re-probes the MP4 and rewrites the JSON docs
```
