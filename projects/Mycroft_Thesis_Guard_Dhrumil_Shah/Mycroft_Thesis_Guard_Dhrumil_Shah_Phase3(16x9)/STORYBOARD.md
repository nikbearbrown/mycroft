# Storyboard — Mycroft Phase 3, 16:9 cut (3840 × 2160, 30 FPS, 11 beats, 2:57)

Frame furniture on every beat: progress bar y 150, section label ("CELL A4 · AGENT 2 · 05/11") y 196, "Dhrumil Shah" top right, scene title y 262 (104 px), content band y 470 → 1700, captions centred at y 1900. Beats fade in over 0.35 s and out over 0.30 s; elements rise 50 px (cubic ease-out); the camera is locked, with a 3.5 % Ken-Burns zoom on notebook figures only.

**Grid:** two columns of 1680 px with a 120 px gutter — left column x 180, right column x 1980. B01 and B10 use the full 3480 px width.

| Beat | Time | Title | Left column / full width | Right column |
|---|---|---|---|---|
| B01 | 0:00–0:16.2 | MYCROFT — PHASE 3 / Building More AI Agents | Title, subtitle, name; MYCROFT / SharedContext hub with the five agents in one row beneath, linked by lines | — |
| B02 | 0:16.2–0:35.0 | The multi-agent foundation | `AgentConfig` → `SharedContext` → `BaseAgent` → `AgentResult` → `AgentEvent`, each with its role | `publish` / `require` code, callout on `require` |
| B03 | 0:35.0–0:47.9 | One validated dataset | Market dataset → schema validation → price/return matrices → SharedContext | `load_mycroft_data()` code, callout on `fill_method=None` |
| B04 | 0:47.9–1:04.1 | MarketStructureAgent | Chart 1 (market cohesion) crossfading to chart 2 (sector correlation) at 62 % | Four stat cards: 0.148 · 19.7 % · `normal` (2026-02-11) · 12 stress windows |
| B05 | 1:04.1–1:21.4 | AnomalyEventAgent | `_robust_z` code, four signal chips, event-type bars (3,972 / 3,397 / 2,267) | Chart 3, captioned "9,636 events at \|modified z\| ≥ 4" |
| B06 | 1:21.4–1:33.0 | PeerCohortBenchmarkAgent | Stock → industry cohort (≥ 5) → percentile rank → laggard / decoupling flag | Labelled decoupling schematic above the `relative_strength_score` code |
| B07 | 1:33.0–1:45.8 | TailRiskLiquidityAgent | Daily returns → drawdown → tail loss → recovery → risk tier | Documented tier thresholds table, then the VaR / ES / Amihud code |
| B08 | 1:45.8–2:08.6 | PredictionReliabilityAgent | Chart 9 (reliability forest) crossfading to chart 10 (sector × regime heatmap) at 55 % | Label chips (reliable / uncertain / unreliable / insufficient_sample) above the labelling code |
| B09 | 2:08.6–2:20.4 | MycroftOrchestrator | Three-stage diagram with each agent's real status and duration | `self.stages` code and a "Degrade, don't stop" card |
| B10 | 2:20.4–2:35.7 | Human review queue | Full-width queue table (EL, HAL, COF, SPGI, NOW at priority 6); below left: field chips, human-decision card, advisory boundary | `review_priority` code |
| B11 | 2:35.7–2:56.7 | Thirty-three checks | 14 validation categories ticking off in two sub-columns | 33/33 score card, "Dhrumil Shah", "Thank you for watching", advisory line |

## Exact on-screen text

Identical wording to the 9:16 cut — see `../Mycroft_Dhrumil_3_Project(9x16)/STORYBOARD.md` for the full list. The only differences are placement and two landscape-only elements:

- **B09** adds a card: "Degrade, don't stop — BaseAgent.run catches the exception, returns a failed AgentResult, and the pipeline continues. The validation suite proves it with an empty-context run."
- **B10** shows a **Sector** column in the queue table, which the portrait cut drops for width.

## What changed from the 9:16 cut

- **Two columns instead of stacking.** Charts and code sit side by side, so both are larger than in portrait.
- **The title graphic is a row, not a ring.** The five agent chips sit in one line under the hub, which suits a wide frame and keeps every name readable.
- **The review table gains a column** (Sector) and spans the full content width.
- **The validation checklist is two sub-columns inside the left column,** with the score card and closing titles on the right, so the final beat reads as one screen.
- **Captions sit at y 1900,** clear of content that ends at y 1700.

## Transitions

Each beat fades to the background for 0.30 s and back in over 0.35 s. Within beats, paired panels crossfade over 0.5 s (B04 at 62 %, B08 at 55 %). No wipes, spins or 3-D moves.
