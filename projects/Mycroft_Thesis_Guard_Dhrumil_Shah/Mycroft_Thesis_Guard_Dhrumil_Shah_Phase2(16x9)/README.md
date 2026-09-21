# Mycroft Phase 2 — 4K 16:9 technical demonstration video

**Deliverable:** `outputs/mycroft_project_4k_16x9.mp4` — 3840 × 2160 (4K landscape, 16:9), 30 FPS, 2:56 (176.20 s), 34.0 MB, H.264 + AAC, burned-in subtitles.
**Author / presenter:** Dhrumil Shah
**Source of every claim:** `Mycroft_Dhrumil1.ipynb`, section **"New Code – Mycroft"** (code cells 49–63 of the notebook = Phase 2 Cells 1–15).

This is the landscape cut of the Mycroft Phase 2 film. It carries the same script, the same voiceover, the same 85 subtitle cues and the same 16 beats as the portrait version in `Mycroft_Dhrumil_2_Project(9x16)`, re-composed for a wide frame.

Opening line:

> "Hi, I am Dhrumil Shah, and this video is about how I extended Mycroft with a Phase 2 pipeline that stress-tests nine machine-learning models and three ensembles on 120 stocks, with purged walk-forward validation and market regimes."

## 16:9 versus 9:16

| | 16:9 (this folder) | 9:16 |
|---|---|---|
| Resolution | 3840 × 2160 | 2160 × 3840 |
| Size | 34.0 MB | 31.1 MB |
| Runtime, voiceover, subtitles | identical (176.20 s, 85 cues) | identical |
| Layout | Two columns: charts and figures beside text and code | Single column stacked vertically |
| Figure 03 (ROC / PR / calibration) | Shown whole, then panel by panel | Same, in a narrower frame |
| Figure 08 (disagreement) | Fits whole — no splitting needed | Split into two stacked panels |
| Architecture diagram | Compact nodes, centred column | Taller nodes, full width |
| Best for | YouTube, LinkedIn feed and desktop, conference slides, portfolio site | Shorts, Reels, TikTok, mobile |

## What is in this folder

| Path | Contents |
|---|---|
| `outputs/` | The final MP4, its SRT, both contact sheets, the render log |
| `narration/` | The 16 voiceover MP3s shared with the portrait cut, plus `narration_full.wav` |
| `subtitles/` | `mycroft_project_4k_16x9.srt` (same text and timings as the 9:16 SRT) |
| `scenes/` | One full-resolution landscape still per beat |
| `charts/` | Animated charts drawn for this cut (leaderboard, walk-forward timeline) |
| `architecture/` | The landscape Phase 2 workflow diagram, 4K plus preview |
| `code_screenshots/` | Five highlighted code panels, re-rendered at landscape column width |
| `agent_visualizations/` | Phase 1 agent chain, horizontal version |
| `assets/mycroft_phase2_outputs/figures/` | Your eight original notebook figures |
| `video_generation.py` | The shared generator (Cells 2–9 are reused by the landscape renderer) |
| `render_16x9.py` | The landscape renderer |
| `make_project_data.py` | Regenerates every JSON file here from the real render data |

## Documentation

| File | Purpose |
|---|---|
| `README.md` | This overview |
| `script.md` | Narration for all 16 beats with timings (identical in both cuts) |
| `SHOTLIST.md` | Landscape layout, beat by beat |
| `VIDEO-SPECIFICATIONS.md` | Format, safe areas, two-column grid, platform notes |
| `FACTCHECK.md` | Every spoken claim traced to the notebook output |
| `FINAL-QA.md` | The 21 automated checks and their results |
| `ASSETS.md` | Asset provenance |
| `BUILD-LOG.md` | How the landscape cut was produced |
| `beat_sheet.json` | Machine-readable beat sheet with landscape layout notes |
| `captions/cues.json`, `audio/timings.json` | Subtitle cues and voiceover timings |
| `data/phase2_results.json` | Every Phase 2 number used in the video |
| `config/video-config.json` | Canvas, encoder, grid, palette, motion |
| `video_manifest.json` | Probe results, SHA-256 of the MP4, file inventory |

## Re-rendering

```bash
python render_16x9.py full
```

Roughly 10 minutes for 5,286 frames. Other modes: `sheet` (stills plus contact sheet) and `bench` (frame timing). After a re-render, run `python make_project_data.py` to refresh the JSON docs.

The renderer patches the canvas constants of `video_generation.py` to landscape and reuses its helpers, so a change to the script or data flows into both cuts. Delete the matching `narration/scene_XX.mp3` after editing narration so the voice is regenerated, and keep both folders in step by copying the new MP3s across.

## Facts and limits

- Every figure on screen is one your notebook produced.
- All 10 numeric claims are re-checked against the notebook data at render time; all pass.
- Phase 2 adds **no AI agents**; the five shown are Phase 1's and are labelled as such.
- Headline result: holdout ROC-AUC 0.521, 95 % interval 0.510–0.533 — "weak but measurable ranking signal."
- Educational research output, not financial advice.
