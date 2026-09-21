# Fact check — Mycroft Phase 3 video (16:9 cut)

*Both cuts speak exactly the same words, so this table applies to each.*

Scope: the video covers **only** the Phase 3 section of `Mycroft_Dhrumil2.ipynb` — "Mycroft_Dhrumil_Shah_Phase_3 (Building more AI agents)", cells A1–A13 (notebook cells 100–127). Phase 1 and Phase 2 appear only where Phase 3 consumes their outputs.

## Class and agent names (exact, as in the code)

`AgentConfig` · `AgentEvent` · `AgentResult` · `SharedContext` · `BaseAgent` · `MycroftData` · `MarketStructureAgent` · `AnomalyEventAgent` · `PeerCohortBenchmarkAgent` · `TailRiskLiquidityAgent` · `PredictionReliabilityAgent` · `MycroftOrchestrator` · `run_validation_suite`

Every one appears on screen spelled exactly as in the notebook.

## Spoken and displayed claims

| # | Beat | Claim | Source in the notebook | Value |
|---|---|---|---|---|
| 1 | B02 | AgentConfig holds shared settings and thresholds | Cell A1 `@dataclass(frozen=True) class AgentConfig` | correlation window 60, step 5, stress percentile 90, anomaly lookback 120, z threshold 4.0, stress multiplier 1.25, idiosyncratic share 0.60, min cohort 5, decoupling drop 0.5, outlier percentile 20, tail lookback 252, VaR 95 %, ES 97.5 % |
| 2 | B02 | SharedContext is a namespaced blackboard with publish / require | Cell A1 `SharedContext` | append-only per key, keeps a history and an event trace |
| 3 | B02 | BaseAgent adds validation, timing and error isolation | Cell A1 `BaseAgent.run` | try/except builds a `failed` AgentResult instead of raising |
| 4 | B02 | AgentResult standardises results; AgentEvent keeps activity traceable | Cell A1 | statuses: complete, attention_required, degraded, failed; AgentEvent has the same 7 fields as Phase 1 |
| 5 | B03 | One validated dataset: prices, returns, close, metadata, features, regimes | Cell A2 `MycroftData`, `load_mycroft_data()` | schema check on 11 required columns, duplicate (Date, Ticker) removal, tz-normalised dates |
| 6 | B04 | Mean pairwise correlation and PC1 share over 60-day windows, expanding percentiles | Cell A3 `MarketStructureAgent` | PC1 share = largest eigenvalue ÷ number of tickers |
| 7 | B04 | 0.148 mean correlation · 19.7 % PC1 · state `normal` on 2026-02-11 | Cell A6 printed output | 0.14804, 0.19725, "normal", correlation percentile 7.8 |
| 8 | B04 | Twelve stress windows | Chart 1 legend, "stress windows (n=12)" | 12 |
| 9 | B05 | Four signals, rolling modified z-scores on medians | Cell A4 `SIGNALS`, `_robust_z` | return, volume, overnight gap, intraday range; MAD_SCALE 0.6745 |
| 10 | B05 | Events split into market, sector and company components | Cell A4 `_attribute`, `_classify` | idiosyncratic ≥ 0.60 share, else market_wide or sector_wide; `unclassified` when the share is not finite |
| 11 | B05 | 9,636 events: 3,972 / 3,397 / 2,267 | Cell A6 printed output | idiosyncratic 3,972, market_wide 3,397, sector_wide 2,267 |
| 12 | B06 | Industry cohorts with sector then universe fallback, minimum 5 names | Cell A7 `_assign_cohorts` | `INDUSTRY::`, `SECTOR::`, `UNIVERSE::all`, `cohort_level` recorded per ticker |
| 13 | B06 | Relative strength score and decoupling flags | Cell A7 | 0.5 / 0.2 / 0.2 / 0.1 weighting; laggard ≤ 20th percentile; decoupling when correlation change ≤ −0.5 |
| 14 | B07 | VaR, expected shortfall, drawdown, recovery, Amihud illiquidity | Cell A8 | historical 95 % VaR, 97.5 % ES, peak-to-trough drawdown, days to recovery, Amihud (2002) |
| 15 | B07 | Documented thresholds; the worst component decides the tier | Cell A8 `TIER_THRESHOLDS`, `_tier` | ES −3.0/−4.5/−6.5 %, drawdown −25/−40/−60 %, downside deviation 20/30/45 % |
| 16 | B08 | Agent 5 retrains nothing; it reads existing holdout predictions | Cell A10 `execute` | reads `test_predictions.csv.gz` from the Phase 1 output directory |
| 17 | B08 | Segments: sector, regime, volatility quintile, risk tier | Cell A10 | plus an overall row and a prior-baseline comparison |
| 18 | B08 | Labels: reliable, uncertain, unreliable, insufficient_sample | Cell A10 `_score_segment` | thresholds on the bootstrap interval versus 0.50; minimum segment 200 rows; 200 bootstrap samples |
| 19 | B08 | Overall 0.516; bull, high-volatility 0.774 | Cell A11 printed reliability matrix | overall 0.5158 [0.5054, 0.5263] reliable; Bull/High vol 0.7737 [0.7351, 0.8104] on 720 rows |
| 20 | B09 | Three stages; Stage 2 agents are independent; Stage 3 consumes risk tiers | Cell A11 `MycroftOrchestrator.stages` | exactly as listed |
| 21 | B09 | Statuses and durations shown per agent | Cell A11 printed output | complete 1.61 s; attention_required 1.95 / 0.22 / 0.49 / 13.23 s |
| 22 | B09 | A failed agent degrades the run instead of stopping it | Cell A1 `BaseAgent.run`, Cell A13 fallback check | the suite runs an agent with an empty context and asserts it fails cleanly |
| 23 | B10 | Queue fields and weighted priority | Cell A11 `aggregate()` | anomaly ×2, cohort outlier ×1, High tier ×2, uncertain/unreliable trust ×1 |
| 24 | B10 | Top of the queue: EL, HAL, COF, SPGI, NOW at priority 6 | Cell A11 printed output | all five with anomaly, cohort outlier, High tier, uncertain trust |
| 25 | B10 | Human decision and rationale stay empty | Cell A11 `aggregate()` and Cell A13 check | `human_decision = None`; `human_decision_left_empty` passes |
| 26 | B10/B11 | Advisory boundary wording | Cell A1 `ADVISORY_BOUNDARY` | quoted verbatim |
| 27 | B11 | 33 checks, all passed | Cell A13 printed output | "Validation: 33/33 passed" |

## Accuracy decisions worth stating

- **All 120 tickers carry the `uncertain` trust label** (Cell A11: `{'uncertain': 120}`). The video shows `uncertain` in the queue rather than implying any name is model-trusted.
- **Sector segments are mostly uncertain.** Only Consumer Cyclical clears 0.50 on its whole interval. The forest plot on screen shows this directly rather than being cropped to the favourable rows.
- **The 0.774 bull / high-volatility figure rests on 720 rows.** The figure caption keeps the n label visible.
- **Cohort and tail-risk counts are not quoted.** In the successful orchestrated run the notebook prints statuses but not cohort or tier counts, so the video shows the method and thresholds instead of invented totals.
- **Agents 3 and 4 have no charts in this cut.** Their five figures were not exported alongside the other five, so those beats use labelled schematics and real thresholds. The peer-cluster graphic is captioned "schematic - illustrates the method, not notebook data".
- **A stale failure in the notebook was not used.** Cell A9's saved output shows Agents 3 and 4 failing against an older `AgentConfig`; the later orchestrated run in Cell A11 runs all five agents successfully, and that is what the video reports.
- **The ERROR line in Cell A13's output is deliberate.** It is the fallback test running an agent with an empty context; the suite still reports 33/33.
- **No component is described as an LLM.** Everything shown is deterministic statistics: eigenvalues, medians and MADs, quantiles, percentile ranks, bootstrap intervals.
- **No autonomous trading claims.** The narration says the agents produce structured evidence and risk signals for human review.
