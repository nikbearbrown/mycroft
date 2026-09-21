# Mycroft Phase 2 — 4K 9:16 technical demonstration video

**Deliverable:** `outputs/mycroft_project_4k_9x16.mp4` — 2160 × 3840 (4K portrait, 9:16), 30 FPS, 2:56 (176.20 s), 31.1 MB, H.264 + AAC, burned-in subtitles.
**Author / presenter:** Dhrumil Shah
**Source of every claim:** `Mycroft_Dhrumil1.ipynb`, section **"New Code – Mycroft"** (code cells 49–63 of the notebook = Phase 2 Cells 1–15).

The video explains the Phase 2 extension of the Mycroft project: 18 new causal features, KMeans market-regime detection, purged and embargoed walk-forward validation, a nine-model zoo with three ensembles, holdout scoring with ticker-clustered bootstrap intervals, probability calibration, performance by market regime, and an automated signal diagnostic.

Opening line of the video:

> "Hi, I am Dhrumil Shah, and this video is about how I extended Mycroft with a Phase 2 pipeline that stress-tests nine machine-learning models and three ensembles on 120 stocks, with purged walk-forward validation and market regimes."

## What is in this folder

| Path | Contents |
|---|---|
| `outputs/` | The final MP4, its SRT, two contact sheets, the render log |
| `narration/` | 16 voiceover MP3s (one per beat) and `narration_full.wav` |
| `subtitles/` | `mycroft_project_4k_9x16.srt` — timed to the rendered voiceover |
| `scenes/` | One full-resolution still per beat (thumbnails, posts, QA) |
| `charts/` | Animated charts drawn for the video (leaderboard, walk-forward timeline) |
| `architecture/` | The Phase 2 workflow diagram, 4K plus preview size |
| `code_screenshots/` | Five highlighted code panels taken from the notebook |
| `agent_visualizations/` | Phase 1 five-agent chain diagram (shown for context) |
| `assets/mycroft_phase2_outputs/figures/` | The eight original notebook figures used in the video |
| `video_generation.ipynb` / `.py` | Colab generator (14 cells) |
| `render_local.py` | Windows generator (PyAV; no ffmpeg.exe needed) |
| `make_project_data.py` | Regenerates every JSON file in this folder from the real render data |

## Documentation

| File | Purpose |
|---|---|
| `README.md` | This overview |
| `script.md` | Full narration, beat by beat, with timings |
| `SHOTLIST.md` | Visuals, animation, assets and transitions per beat |
| `VIDEO-SPECIFICATIONS.md` | Format, safe areas, design system, platform notes |
| `FACTCHECK.md` | Every spoken claim traced to the notebook output |
| `ASSETS.md` | Asset provenance and licensing notes |
| `FINAL-QA.md` | The 20 automated checks and their results |
| `BUILD-LOG.md` | How the video was built, decisions, known limitations |
| `beat_sheet.json` | Machine-readable beat sheet (16 beats) |
| `captions/cues.json` | 85 subtitle cues with timings |
| `audio/timings.json` | Per-beat voiceover timings |
| `data/phase2_results.json` | Every Phase 2 number used in the video |
| `config/video-config.json` | Canvas, encoder, safe area, palette, motion settings |
| `video_manifest.json` | File inventory, SHA-256 of the MP4, probe results |

## Re-rendering

Windows (this machine, roughly 10 minutes):

```bash
python render_local.py full
```

Other modes: `python render_local.py sheet` (voiceover plus contact sheet, fast layout check) and `python render_local.py bench` (frame-time estimate).

Google Colab: upload `video_generation.ipynb` into the runtime where the Phase 2 cells ran, then run it top to bottom. It writes to `/content/mycroft_video/outputs/`.

To narrate the video yourself, drop `narration/scene_01_user.wav` … `scene_16_user.wav` into place and re-render. Those files take priority over the synthetic voice. For background music, add `assets/background_music.mp3`.

## Facts and limits

- Every figure on screen is one your notebook produced. No chart was invented or re-simulated.
- Every number spoken is checked against the notebook's printed output at render time. All 10 fact checks pass (see `FINAL-QA.md`).
- Phase 2 (cells 49–63) creates **no new AI agents**. The five agents shown briefly are Phase 1's, and the video says so.
- The headline result is deliberately modest: holdout ROC-AUC 0.521 with a 95% interval of 0.510 to 0.533, which the notebook calls "weak but measurable ranking signal."
- The video carries the same boundary as the notebook: educational research output, not financial advice.
