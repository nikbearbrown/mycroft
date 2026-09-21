# Storyboard — Mycroft Phase 3 (9:16, 2160 × 3840, 30 FPS, 2:57)

Frame furniture on every beat: progress bar at y 405, section label ("CELL A4 · AGENT 2 · 05/11") at y 450, "Dhrumil Shah" top right, scene title at y 530, content between y 820 and 2660, captions centred at y 2830. Each beat fades in over 0.35 s and out over 0.30 s; elements rise 50 px with a cubic ease-out. The camera is locked; the only movement is a 3.5 % Ken-Burns zoom on notebook figures.

| # | Time | On-screen title | On-screen text and visuals | Animation | Code panel | Chart |
|---|---|---|---|---|---|---|
| B01 | 0:00–0:16.2 | MYCROFT — PHASE 3 / Building More AI Agents | Title, subtitle, "Dhrumil Shah"; five agent nodes around a MYCROFT / SharedContext hub | Title drops in; each agent node and its link fade in one at a time | — | — |
| B02 | 0:16.2–0:35.0 | The multi-agent foundation | `AgentConfig` → `SharedContext` → `BaseAgent` → `AgentResult` → `AgentEvent`, each with a one-line role | Chain reveals top to bottom with arrows; amber callout lands on `require()` | Cell A1 · `publish` / `require` | — |
| B03 | 0:35.0–0:47.9 | One validated dataset | Market dataset → schema validation → price/return matrices → SharedContext | Chain reveal; callout on `fill_method=None` | Cell A2 · `load_mycroft_data()` | — |
| B04 | 0:47.9–1:04.1 | MarketStructureAgent | Stat cards: 0.148 mean correlation · 19.7 % PC1 share · state `normal` on 2026-02-11 · 12 stress windows | Figure zooms slowly, crossfades to the sector chart at 62 %; stat cards stagger | — | Charts 1 and 2 |
| B05 | 1:04.1–1:21.4 | AnomalyEventAgent | Signal chips (daily return, volume, overnight gap, intraday range); event-type bars 3,972 / 3,397 / 2,267 | Callout on the median/MAD lines; bars grow; figure fades in and zooms | Cell A4 · `_robust_z` | Chart 3 |
| B06 | 1:21.4–1:33.0 | PeerCohortBenchmarkAgent | Stock → industry cohort (≥ 5 names) → percentile rank → laggard / decoupling flag; labelled schematic of one name leaving its cluster | Chain reveal; the amber node drifts away from the peer cluster | Cell A7 · `relative_strength_score` | — (schematic, marked as such) |
| B07 | 1:33.0–1:45.8 | TailRiskLiquidityAgent | Daily returns → drawdown → tail loss → recovery → risk tier; documented tier thresholds table | Chain reveal; threshold table fades in; callout on the quantile lines | Cell A8 · VaR / ES / Amihud | — |
| B08 | 1:45.8–2:08.6 | PredictionReliabilityAgent | Label chips: reliable · uncertain · unreliable · insufficient_sample | Forest plot zooms, crossfades to the sector × regime heatmap at 55 %; callout on the if/elif branch | Cell A10 · reliability labelling | Charts 9 and 10 |
| B09 | 2:08.6–2:20.4 | MycroftOrchestrator | Stage 1 MarketStructureAgent · Stage 2 AnomalyEvent + PeerCohortBenchmark + TailRiskLiquidity · Stage 3 PredictionReliability, each with its real status and duration | Stages build downward with connecting arrows | Cell A11 · `self.stages` | — |
| B10 | 2:20.4–2:35.7 | Human review queue | Queue table (EL, HAL, COF, SPGI, NOW — all priority 6); field chips; "Human decision · Human rationale" card; advisory boundary | Rows appear one by one; chips stagger; cards fade up | Cell A11 · `review_priority` | — |
| B11 | 2:35.7–2:56.7 | Thirty-three checks | 14 validation categories ticking off; 33/33 score card; "Dhrumil Shah", "Thank you for watching", advisory line | Checks tick in sequence; score card and closing titles fade up | — | — |

## Exact on-screen text by beat

**B01** — MYCROFT — PHASE 3 · Building More AI Agents · Dhrumil Shah · node labels: MarketStructureAgent, AnomalyEventAgent, PeerCohortBenchmarkAgent, TailRiskLiquidityAgent, PredictionReliabilityAgent · hub: MYCROFT / SharedContext

**B02** — AgentConfig "shared settings, thresholds, output paths" · SharedContext "namespaced blackboard: publish / require" · BaseAgent "validate, execute, time, isolate failures" · AgentResult "payload + status + warnings" · AgentEvent "traceable agent activity" · label chip "Shared communication layer"

**B03** — Market dataset "Phase 1 cleaned panel · 120 tickers" · Schema validation "required columns, duplicates, tz-normalised dates" · Price / return matrices "close · returns · metadata · features · regimes" · SharedContext "published once, read by every agent" · label chip "One validated dataset for every agent"

**B04** — "0.148 mean pairwise correlation" · "19.7 % PC1 share of variance" · "normal — market state on 2026-02-11" · "12 stress windows flagged" · caption "Notebook chart 1 · market cohesion timeline (stress windows in red)" then "Notebook chart 2 · mean within-sector correlation"

**B05** — chips: daily return · volume · overnight gap · intraday range · bars: idiosyncratic 3,972 / market_wide 3,397 / sector_wide 2,267 · label chip "Detecting abnormal market events" · caption "Notebook chart 3 · 9,636 events at |modified z| ≥ 4"

**B06** — Stock "one row per ticker" · Industry cohort (≥ 5 names) "fallback: SECTOR:: then UNIVERSE::all" · Percentile rank vs peers "7 features ranked inside the cohort" · Laggard / decoupling flag "bottom 20 % or correlation drop ≥ 0.5" · "peer cohort", "decoupling name", "schematic - illustrates the method, not notebook data"

**B07** — Daily returns "252-day lookback" · Drawdown "peak to trough on adjusted close" · Tail loss "95 % VaR · 97.5 % expected shortfall" · Recovery "days back to the prior peak" · Risk tier "worst component decides the tier" · threshold table: 97.5 % expected shortfall −3.0 % | −4.5 % | −6.5 %; maximum drawdown −25 % | −40 % | −60 %; downside deviation (annual) 20 % | 30 % | 45 %

**B08** — chips: reliable · uncertain · unreliable · insufficient_sample · captions "Notebook chart 9 · segment reliability, 95 % ticker-clustered bootstrap" and "Notebook chart 10 · reliability by sector and market regime"

**B09** — STAGE 1 / STAGE 2 / STAGE 3 with MarketStructureAgent "complete · 1.61 s", AnomalyEventAgent "attention_required · 1.95 s", PeerCohortBenchmarkAgent "attention_required · 0.22 s", TailRiskLiquidityAgent "attention_required · 0.49 s", PredictionReliabilityAgent "attention_required · 13.23 s"

**B10** — table headers Ticker / anomaly / cohort / risk tier / model trust / priority · rows EL, HAL, COF, SPGI, NOW (yes, yes, High, uncertain, 6) · chips anomaly flag, cohort outlier, risk tier, model trust, market state, review priority · card "Human decision · Human rationale — Both fields are created empty. The agents rank the queue; the person decides." · card "Advisory boundary — Educational research output from Mycroft. Not personalized financial advice or an investment recommendation."

**B11** — data schema, duplicate records, positive prices, OHLC consistency, agent execution, event generation, output ranges, anomaly classifications, risk mathematics, ROC-AUC bounds, confidence intervals, small-segment suppression, inter-agent communication, human decision left empty · "33/33 validation checks passed" · "Dhrumil Shah" · "Thank you for watching"

## Transitions

Every cut is a 0.30 s fade to the background followed by a 0.35 s fade in, so beats read as separate cards without a hard cut. Within a beat, panels that share a slot crossfade over 0.5 s (B04 at 62 %, B08 at 55 %). No wipes, spins or 3-D moves.
