# Narration script — Mycroft Phase 3, "Building More AI Agents"

9:16 · 2160 × 3840 · 30 FPS · 2:57 (176.7 s) · 11 beats · 425 spoken words · ≈ 150 words per minute
Voice: edge-tts `en-US-AndrewNeural`, rate +25 %. Each beat opens with 0.30 s of silence and closes with 0.45 s.
Captions reproduce this text word for word (93 cues, ≤ 40 characters each).

---

### B01 · MYCROFT — PHASE 3 · 0:00.0 → 0:16.2

> Hi, I am Dhrumil Shah, and this video is about Phase 3 of my Mycroft project, where I expanded the system by building a modular multi-agent financial analytics architecture for market structure analysis, anomaly detection, peer benchmarking, tail-risk and liquidity analysis, and prediction reliability.

### B02 · The multi-agent foundation · 0:16.2 → 35.0

> Phase 3 begins with a reusable agent framework. AgentConfig holds shared settings and thresholds. SharedContext is a namespaced blackboard where agents publish and require each other's output. BaseAgent adds validation, timing and error isolation, AgentResult standardises results, and AgentEvent keeps every action traceable.

### B03 · One validated dataset · 35.0 → 47.9

> All agents read the same validated data. MycroftData holds the cleaned price panel, returns and close matrices, metadata, Phase 1 predictions and optional Phase 2 regime labels, after schema checks and duplicate removal.

### B04 · MarketStructureAgent · 47.9 → 64.1

> Agent one measures how tightly the 120 names move together: average pairwise correlation, and the share of variance explained by the first principal component, over sixty-day windows ranked with expanding percentiles so nothing looks ahead. Twelve stress windows were flagged, and the latest window reads normal.

### B05 · AnomalyEventAgent · 64.1 → 81.4

> Agent two scans returns, volume, overnight gaps and intraday range using rolling modified z-scores built on medians, not means. Each event is split into market, sector and company components, then labelled idiosyncratic, sector-wide or market-wide. It found nine thousand six hundred and thirty-six events.

### B06 · PeerCohortBenchmarkAgent · 81.4 → 93.0

> Agent three ranks every name inside its own industry cohort, falling back to sector or the whole universe when a cohort is too small, then scores relative strength and flags laggards that have decoupled from their peers.

### B07 · TailRiskLiquidityAgent · 93.0 → 105.8

> Agent four quantifies downside: historical value at risk, expected shortfall, maximum drawdown and recovery time, plus Amihud illiquidity. Documented thresholds assign a risk tier, and the worst component decides it.

### B08 · PredictionReliabilityAgent · 105.8 → 128.6

> Agent five retrains nothing. It takes the existing holdout predictions and asks where they can be trusted, segmenting by sector, regime, volatility quintile and risk tier. Every segment gets a ticker-clustered bootstrap interval and a label: reliable, uncertain, unreliable, or insufficient sample. Overall is 0.516, while bull, high-volatility days reach 0.774.

### B09 · MycroftOrchestrator · 128.6 → 140.4

> The orchestrator runs three stages: market structure first, then the three independent analysts, then prediction reliability, which consumes the risk tiers. A failed agent degrades the run instead of stopping it.

### B10 · Human review queue · 140.4 → 155.7

> Every verdict merges into one review queue: anomaly flag, cohort outlier, risk tier, model trust, market state and a review priority. Human decision and rationale stay empty by design. This is educational research output, not personalised financial advice.

### B11 · Thirty-three checks · 155.7 → 176.7

> A validation suite checks schema, duplicates, prices, agent execution, output ranges, risk mathematics, AUC bounds and inter-agent communication. Thirty-three checks, all passed. Phase 3 expands Mycroft into a modular, explainable multi-agent analytics system where specialised agents produce structured evidence for human review. I'm Dhrumil Shah. Thank you for watching.

---

## Pronunciation handling

The speech engine receives adjusted spellings; the captions keep the code spelling.

| Written | Spoken |
|---|---|
| AgentConfig, SharedContext, BaseAgent, AgentResult, AgentEvent, MycroftData | split into two words |
| ROC-AUC / AUC | letter by letter |
| Amihud | "Amihood" |

Numbers are written out where the engine would otherwise rush them ("nine thousand six hundred and thirty-six").

## Tone rules followed

- The agents "produce structured evidence and risk signals for human review". Nothing in the script suggests the system decides trades.
- Deterministic statistics are described as statistics, never as a language model: modified z-scores, eigenvalues, quantiles, bootstrap intervals.
- Weak and uncertain results are stated plainly: all 120 tickers carry the `uncertain` trust label, and the largest regime segment is uncertain.
- Phase 1 and Phase 2 appear only where Phase 3 consumes their outputs (cleaned panel, latest predictions, holdout predictions, regime labels).

## Editing

Narration lives in the `SCRIPT` list in `phase3_video.py`. After editing, delete the matching `narration/scene_XX.mp3` and re-run `python phase3_video.py full`.
