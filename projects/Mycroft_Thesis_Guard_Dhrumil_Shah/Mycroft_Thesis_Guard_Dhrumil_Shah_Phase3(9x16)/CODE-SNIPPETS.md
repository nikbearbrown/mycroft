# Code shown on screen — and what each snippet demonstrates

Every panel quotes real Phase 3 code from `Mycroft_Dhrumil2.ipynb`. Lines were re-wrapped to fit the 1780 px portrait column; no name, argument or value was changed. Each panel shows 4–7 lines with syntax highlighting and an animated amber callout on the lines being discussed. PNGs of all panels are in `code_screenshots/`.

---

### B02 · Cell A1 — `SharedContext` — label: "Shared communication layer"

```python
def publish(self, agent: str, key: str, value: Any) -> None:
    self._store.setdefault(agent, {})[key] = value

def require(self, agent: str, key: str) -> Any:
    if agent not in self._store or key not in self._store[agent]:
        raise KeyError(f"Required context '{agent}.{key}' is missing.")
    return self._store[agent][key]
```

**Demonstrates:** the blackboard pattern that makes the system modular. Agents never call each other directly; they write under their own namespace and read through `get` (soft dependency, with a default) or `require` (hard dependency that fails loudly). The callout lands on `require`, because failing with a clear message is what makes a missing dependency debuggable instead of silent.

### B03 · Cell A2 — `load_mycroft_data()` — label: "One validated dataset for every agent"

```python
close = prices.pivot(index="Date", columns="Ticker",
                    values="Adj_Close").sort_index()
# fill_method=None keeps genuine gaps as NaN
returns = close.pct_change(fill_method=None)
```

**Demonstrates:** the single shared data layer. Every agent works from the same validated panel instead of rebuilding its own. The callout highlights `fill_method=None`: pandas would otherwise carry the last price forward across a genuine gap and invent returns that never happened.

### B05 · Cell A4 — `AnomalyEventAgent._robust_z` — label: "Detecting abnormal market events"

```python
median = series.rolling(window, min_periods=minimum).median()
deviation = (series - median).abs()
mad = deviation.rolling(window, min_periods=minimum).median()
mad = mad.replace(0.0, np.nan)
return self.MAD_SCALE * (series - median) / mad
```

**Demonstrates:** the modified z-score (Iglewicz & Hoaglin), `0.6745 × (x − median) / MAD`, over a 120-day rolling window. The design decision on screen is median and MAD instead of mean and standard deviation: one large move inflates a standard deviation and hides the very event being looked for. A zero MAD becomes NaN rather than a divide-by-zero.

### B06 · Cell A7 — `PeerCohortBenchmarkAgent` — label: "Benchmarking against peer cohorts"

```python
scorecard["relative_strength_score"] = (
    0.5 * scorecard["pct_return_20d"] + 0.2 * scorecard["pct_return_5d"]
    + 0.2 * scorecard["pct_drawdown_60d"]
    + 0.1 * (100 - scorecard["pct_volatility_20d"]))
```

**Demonstrates:** how relative strength is composed from percentile ranks *within the cohort*: medium-term momentum carries half the weight, short-term momentum and drawdown a fifth each, and volatility enters inverted so a calmer name scores higher. Every input is a within-cohort percentile, so the score compares like with like.

### B07 · Cell A8 — `TailRiskLiquidityAgent` — label: "Measuring downside tail risk"

```python
value_at_risk = float(np.quantile(returns, var_q))
tail = returns[returns <= np.quantile(returns, es_q)]
expected_shortfall = float(tail.mean()) if len(tail) else float("nan")
amihud = float(amihud_input.dropna().mean() * 1e9)
```

**Demonstrates:** historical, non-parametric tail risk. VaR is an empirical quantile of realised returns at 95 %; expected shortfall is the mean of the worst 2.5 % (the Basel FRTB 97.5 % convention), so the shape of the tail matters, not a normality assumption. Amihud (2002) illiquidity is mean(|return| / dollar volume), scaled only for readability.

### B08 · Cell A10 — `PredictionReliabilityAgent` — label: "Testing model reliability by segment"

```python
low, high = self._bootstrap_auc(actual, probability, tickers)
if low > 0.50:
    reliability = "reliable"
elif high < 0.50:
    reliability = "unreliable"
else:
    reliability = "uncertain"
```

**Demonstrates:** the core idea of Agent 5. A segment is judged by where its whole ticker-clustered bootstrap interval sits relative to 0.50 — not by the point estimate. Segments under 200 rows, or with one outcome class, return `insufficient_sample` and no AUC at all, because a number there would look more authoritative than the evidence deserves.

### B09 · Cell A11 — `MycroftOrchestrator` — label: "Coordinating specialized agents"

```python
self.stages: list[list[BaseAgent]] = [
    [MarketStructureAgent(config)],
    [AnomalyEventAgent(config), PeerCohortBenchmarkAgent(config),
     TailRiskLiquidityAgent(config)],
    [PredictionReliabilityAgent(config)],
]
```

**Demonstrates:** the dependency structure as data. Stage 2's three agents are independent of one another, so they form one stage and could run in parallel; Stage 3 is separate because `PredictionReliabilityAgent` consumes the risk tiers Stage 2 publishes. `BaseAgent.run` catches exceptions per agent, so a failure degrades the run instead of ending it.

### B10 · Cell A11 — `aggregate()` — label: "Prioritising work, not deciding it"

```python
frame["review_priority"] = (frame["anomaly_flag"].astype(int) * 2
                            + frame["cohort_outlier_flag"].astype(int)
                            + frame["risk_tier"].eq("High").astype(int) * 2
                            + frame["model_trust"].isin(
                                ["uncertain", "unreliable"]).astype(int))
frame["human_decision"] = None
```

**Demonstrates:** the governance boundary in code. Priority is a transparent weighted count — anomalies and a High risk tier count double — and the very next line creates `human_decision` empty. The system ranks work; it does not take a position.

### B11 · Cell A13 — `run_validation_suite()` — label: "33 checks across the whole pipeline"

```python
check("expected_shortfall_worse_than_var",
      bool((profiles["expected_shortfall_975"]
            <= profiles["var_95_daily"] + 1e-9).all()))
check("small_segments_suppressed", ...)
check("human_decision_left_empty",
      bool(aggregate["human_decision"].isna().all()))
```

**Demonstrates:** three kinds of check in one view — a mathematical invariant (97.5 % expected shortfall must be at least as bad as 95 % VaR), a statistical-honesty rule (small segments must be suppressed), and a governance rule (the human decision column must still be empty). The suite also runs an agent against an empty context on purpose, to prove it fails cleanly rather than crashing the pipeline.

---

## Snippets deliberately not shown

`AgentConfig`'s full field list, `BaseAgent.run`'s try/except, the attribution decomposition, and the drawdown profile are described in narration and diagrams rather than shown as code, to keep every panel within 4–7 readable lines at portrait width.
