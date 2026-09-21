# Mycroft Phase 3 — "Building More AI Agents" (4K 9:16 video)

**Deliverable:** `outputs/mycroft_phase3_4k_9x16.mp4` — 2160 × 3840 (true 4K portrait, 9:16), 30 FPS, 2:57, H.264 + AAC, burned-in captions.
**Author / presenter:** Dhrumil Shah
**Scope:** only the Phase 3 section of `Mycroft_Dhrumil2.ipynb` — *Mycroft_Dhrumil_Shah_Phase_3 (Building more AI agents)*, cells A1–A13 (notebook cells 100–127). Phase 1 and Phase 2 appear only where Phase 3 consumes their outputs.

Opening line:

> "Hi, I am Dhrumil Shah, and this video is about Phase 3 of my Mycroft project, where I expanded the system by building a modular multi-agent financial analytics architecture for market structure analysis, anomaly detection, peer benchmarking, tail-risk and liquidity analysis, and prediction reliability."

## What the video covers (11 beats)

| Beat | Subject |
|---|---|
| B01 | Title card; the five agents forming around a Mycroft / SharedContext hub |
| B02 | The framework: `AgentConfig` → `SharedContext` → `BaseAgent` → `AgentResult` → `AgentEvent` |
| B03 | `MycroftData` and the Phase 3 loading and validation workflow |
| B04 | `MarketStructureAgent` — correlation and PC1 share, expanding percentiles, 12 stress windows |
| B05 | `AnomalyEventAgent` — four signals, modified z-scores, attribution into 3 event types, 9,636 events |
| B06 | `PeerCohortBenchmarkAgent` — industry cohorts with fallbacks, relative strength, decoupling |
| B07 | `TailRiskLiquidityAgent` — VaR, expected shortfall, drawdown and recovery, Amihud illiquidity, risk tiers |
| B08 | `PredictionReliabilityAgent` — segment reliability with ticker-clustered bootstrap intervals |
| B09 | `MycroftOrchestrator` — three stages, real statuses and durations, degrade-don't-stop |
| B10 | The aggregated human-review queue and the governance boundary |
| B11 | `run_validation_suite` — 33 checks, all passed — and the closing summary |

## Folder contents

| Path | Contents |
|---|---|
| `outputs/` | The MP4, its SRT copy, contact sheets, render log |
| `narration/` | 11 voiceover MP3s and `narration_full.wav` |
| `subtitles/` | `mycroft_phase3_4k_9x16.srt` (93 cues) |
| `scenes/` | One full-resolution still per beat |
| `code_screenshots/` | The nine code panels as PNGs |
| `assets/phase3_figures/` | The five exported Phase 3 charts used in the film |
| `phase3_video.py` | The generator (data, script, scenes, render, QA) |
| `_phase2_helpers.py` | Shared design system reused from the Phase 2 generator |
| `make_project_data.py` | Rebuilds every JSON file here from the real render data |

## Documentation

| File | Purpose |
|---|---|
| `script.md` | Final narration with timestamps and tone rules |
| `STORYBOARD.md` | Beat-by-beat visuals, on-screen text, animation, transitions |
| `CODE-SNIPPETS.md` | The nine snippets and what each demonstrates |
| `FACTCHECK.md` | Every claim traced to notebook code or printed output |
| `VIDEO-SPECIFICATIONS.md` | Export settings, safe area, design system, music guidance |
| `ASSETS.md` | Asset provenance, including the five figures not available |
| `FINAL-QA.md` | Automated checks and manual review |
| `BUILD-LOG.md` | How it was built and what changed during production |
| `PROMPT.md` | Consolidated, reusable video-generation brief |
| `beat_sheet.json`, `captions/cues.json`, `audio/timings.json`, `data/phase3_results.json`, `config/video-config.json`, `video_manifest.json` | Machine-readable versions |

## Re-rendering

```bash
python phase3_video.py full
```

About 7 minutes for 5,301 frames. `sheet` renders stills and a contact sheet for a fast layout check; `bench` estimates frame time. After any re-render, run `python make_project_data.py` to refresh the JSON docs.

To use your own voice, add `narration/scene_01_user.wav` … `scene_11_user.wav`. For music, add `assets/background_music.mp3`.

## Honest limits

- **Agents 3 and 4 have no charts in this cut.** Their five figures were not exported with the others, so those beats use the real thresholds and formulas plus a schematic that says so on screen. Drop the PNGs into `assets/phase3_figures/` and re-render to include them.
- **Results are reported as the notebook found them:** all 120 tickers carry the `uncertain` trust label, most sector segments are uncertain, and the strongest segment (0.774) rests on 720 rows.
- **Cell A9's saved failures are stale.** They came from an older `AgentConfig`; the later orchestrated run has all five agents succeeding, and that is what the video shows.
- **The ERROR line in the validation output is deliberate** — the suite runs an agent against an empty context to prove it fails cleanly.
- The system is presented as analytical decision support. The agents produce structured evidence and risk signals; the human decides.
