# Visual asset list — Phase 3 (9:16)

## Notebook figures used (real output, unmodified)

Exported from the Phase 3 run and stored in `assets/phase3_figures/`.

| File | Beat | Notebook source | Shown as |
|---|---|---|---|
| `agent1_01_market_cohesion_timeline.png` | B04 | Chart 1, `plot_market_cohesion_timeline` | Full figure with a slow zoom; red bands mark the 12 stress windows |
| `agent1_02_sector_internal_correlation.png` | B04 | Chart 2, `plot_sector_internal_correlation` | Crossfade at 62 % of the beat |
| `agent2_01_event_timeline.png` | B05 | Chart 3, `plot_event_timeline` | Full figure, captioned with the event count and threshold |
| `agent5_01_reliability_forest.png` | B08 | Chart 9, `plot_reliability_forest` | Forest plot with the 0.50 reference line |
| `agent5_02_sector_regime_heatmap.png` | B08 | Chart 10, `plot_sector_regime_heatmap` | Crossfade at 55 %; grey cells are the suppressed small segments |

## Notebook figures not available for this cut

These five were not exported alongside the others, so their beats use schematics and the real thresholds from the code instead. Drop the PNGs into `assets/phase3_figures/`, add them to the `FIG` dictionary in `phase3_video.py`, and re-render to include them.

`agent2_02_attribution_by_sector.png` · `agent3_01_cohort_position_map.png` · `agent3_02_cohort_dispersion.png` · `agent4_01_tail_risk_map.png` · `agent4_02_drawdown_recovery.png`

## Generated for the video

| Asset | Made by | Beat |
|---|---|---|
| Agent ring (hub + five agents) | `agent_ring()` | B01 |
| Framework chain (AgentConfig → … → AgentEvent) | `flow_chain()` | B02 |
| Data-layer chain | `flow_chain()` | B03 |
| Stat cards (0.148 · 19.7 % · normal · 12) | `stat_card()` | B04 |
| Event-type bars (3,972 / 3,397 / 2,267) | `hbar_spr()` | B05 |
| Cohort pipeline chain + peer schematic | `flow_chain()`, `peer_schematic()` | B06 |
| Risk chain + tier threshold table | `flow_chain()`, `tier_table()` | B07 |
| Reliability label chips | `chip()` | B08 |
| Three-stage orchestration diagram | `stage_diagram()` | B09 |
| Review-queue table + field chips + governance cards | `queue_table()`, `text_card()` | B10 |
| Validation checklist + 33/33 score card | `checklist()`, `stat_card()` | B11 |
| Code panels (9) | `code_spr()` with Pygments → `code_screenshots/*.png` | B02–B11 |
| Per-beat stills (11) | `render_frame()` → `scenes/still_*.png` | QA, thumbnails |
| Contact sheet | `contact_sheet()` → `outputs/contact_sheet.jpg` | QA |

The peer-cluster graphic in B06 is generated from a fixed random seed purely to illustrate the method, and carries the on-screen caption "schematic - illustrates the method, not notebook data".

## Audio

| Asset | Source |
|---|---|
| `narration/scene_01…11.mp3` | edge-tts, `en-US-AndrewNeural`, rate +25 % |
| `narration/narration_full.wav` | The 11 clips placed on the beat timeline, peak-normalised to −1 dBFS |
| Background music | Not included; add `assets/background_music.mp3` and re-render (see `VIDEO-SPECIFICATIONS.md`) |

## Fonts

DejaVu Sans and DejaVu Sans Mono, bundled with matplotlib, under a permissive licence that allows redistribution and embedding.

## Software

PyAV (FFmpeg bindings), Pillow, NumPy, Pygments, edge-tts, matplotlib (fonts only). All open-source packages from PyPI.

## Provenance summary

Nothing in the video came from stock libraries, external datasets or generated imagery. Charts are your notebook's own output; every number on screen traces to a printed notebook result (see `FACTCHECK.md`); every code panel quotes cells A1–A13.
