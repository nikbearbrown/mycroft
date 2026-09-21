# Mycroft Phase 3 — "Building More AI Agents" (4K 16:9 video)

**Deliverable:** `outputs/mycroft_phase3_4k_16x9.mp4` — 3840 × 2160 (4K landscape, 16:9), 30 FPS, 2:57, H.264 + AAC, burned-in captions.
**Author / presenter:** Dhrumil Shah
**Scope:** only the Phase 3 section of `Mycroft_Dhrumil2.ipynb` — *Mycroft_Dhrumil_Shah_Phase_3 (Building more AI agents)*, cells A1–A13 (notebook cells 100–127). Phase 1 and Phase 2 appear only where Phase 3 consumes their outputs.

This is the landscape cut of the Phase 3 film. Same script, same voiceover files, same 93 caption cues and the same 11 beats as `Mycroft_Dhrumil_3_Project(9x16)`, re-composed on a two-column grid.

Opening line:

> "Hi, I am Dhrumil Shah, and this video is about Phase 3 of my Mycroft project, where I expanded the system by building a modular multi-agent financial analytics architecture for market structure analysis, anomaly detection, peer benchmarking, tail-risk and liquidity analysis, and prediction reliability."

## 16:9 versus 9:16

| | 16:9 (this folder) | 9:16 |
|---|---|---|
| Resolution | 3840 × 2160 | 2160 × 3840 |
| Runtime, voiceover, captions | identical (176.7 s, 93 cues) | identical |
| Layout | Two columns — chart or diagram beside its explanation and code | Single column, stacked |
| Title graphic | Hub with the five agents in one row | Hub with the five agents in a ring |
| Review queue | Full-width table including the Sector column | Six columns, Sector dropped for width |
| Extra card | B09 "Degrade, don't stop" | — |
| Best for | YouTube, LinkedIn desktop, slides, portfolio | Shorts, Reels, TikTok, mobile |

## The eleven beats

B01 title and the five agents · B02 the framework (`AgentConfig` → `SharedContext` → `BaseAgent` → `AgentResult` → `AgentEvent`) · B03 `MycroftData` and validation · B04 `MarketStructureAgent` · B05 `AnomalyEventAgent` · B06 `PeerCohortBenchmarkAgent` · B07 `TailRiskLiquidityAgent` · B08 `PredictionReliabilityAgent` · B09 `MycroftOrchestrator` · B10 the aggregated human-review queue · B11 `run_validation_suite` and the close.

## Folder contents

| Path | Contents |
|---|---|
| `outputs/` | The MP4, its SRT copy, contact sheets, render log |
| `narration/` | The 11 voiceover MP3s shared with the portrait cut, plus `narration_full.wav` |
| `subtitles/` | `mycroft_phase3_4k_16x9.srt` (93 cues) |
| `scenes/` | One full-resolution landscape still per beat |
| `code_screenshots/` | The nine code panels, re-rendered at landscape column width |
| `assets/phase3_figures/` | The five exported Phase 3 charts used in the film |
| `render_16x9.py` | The landscape generator |
| `phase3_video.py`, `_phase2_helpers.py` | The Phase 3 data/script source and the shared design system |
| `make_project_data.py` | Rebuilds every JSON file here from the real render data |

## Documentation

`README.md` · `script.md` · `STORYBOARD.md` (landscape layout) · `CODE-SNIPPETS.md` · `CAPTIONS.md` · `FACTCHECK.md` · `VIDEO-SPECIFICATIONS.md` · `ASSETS.md` · `FINAL-QA.md` · `BUILD-LOG.md` · `PROMPT.md`, plus `beat_sheet.json`, `captions/cues.json`, `audio/timings.json`, `data/phase3_results.json`, `config/video-config.json` and `video_manifest.json`.

## Re-rendering

```bash
python render_16x9.py full
```

About 9 minutes for 5,301 frames; `sheet` and `bench` modes work as in the portrait cut. Run `python make_project_data.py` afterwards to refresh the JSON docs. A narration change in `phase3_video.py` flows into both cuts — delete the affected `narration/scene_XX.mp3` in both folders and re-render each.

## Honest limits

- Agents 3 and 4 appear without notebook charts: five of the ten Phase 3 figures were not exported. Their beats use the real thresholds, formulas and a schematic labelled as such.
- All 120 tickers carry the `uncertain` trust label, and the strongest reliability segment (0.774) rests on 720 rows. Both are shown as found.
- Cell A9's saved failures are stale; the video reports the later successful orchestrated run.
- The system is analytical decision support. The agents produce structured evidence and risk signals; the human decides.
