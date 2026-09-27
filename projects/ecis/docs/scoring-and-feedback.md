# Scoring and feedback loops

After signals are pre-registered, the Scorecard grades them against the market and three agents update the system.

---

## Outcome resolver:

`src/ecis/scoring/outcome_resolver.py`

For each signal:

1. Fetch stock and sector-benchmark ETF prices at the transcript date (t0).
2. Fetch the same at t0 + 30, 90, and 180 calendar days.
3. Compute stock return, benchmark return, excess return.
4. Grade:
  - `raised` correct if excess return > 0
  - `lowered` correct if excess return < 0
  - `maintained` correct if excess return ≤ 2%

Results go to `outcomes.db`. The cache key includes `transcript_date` so a filing-date correction does not reuse the wrong prices. Schema: [db README](../src/ecis/db/README.md).

```bash
python -m ecis.main --resolve-outcomes
python -m ecis.main --resolve-outcomes --ticker TICKER
```

yfinance can include adjusted/look-ahead prices. A human point-in-time audit is still required before treating Scorecard numbers as final (see the architecture risk register).

---



## Metrics:

`src/ecis/scoring/metrics.py` and `src/ecis/scoring/scorer.py`


| Metric                   | Question it answers                                                  |
| ------------------------ | -------------------------------------------------------------------- |
| **Brier score**          | Mean squared error of confidence vs 0/1 outcome (0 is perfect)       |
| **Brier skill score**    | Improvement over the keyword baseline (positive = worth the compute) |
| **ECE**                  | Does “80% confident” actually win 80% of the time?                   |
| **Murphy decomposition** | Calibration error (fixable) vs resolution (skill at ranking)         |
| **Information ratio**    | Mean excess return / std — economic relevance                        |


`score_all_readers` scores keyword, FinBERT, LLM, triangulated, and an aggregate. `score_by_llm_model` splits on the `llm_model` alias (`llama` vs `mistral`).

```bash
python -m ecis.main --score
python -m ecis.main --score --horizon 90
```

---



## Recalibration:

`src/ecis/scoring/recalibrator.py`

- **Platt scaling** — two-parameter sigmoid on logits (better on small samples).
- **Isotonic regression** — monotonic map (better on large samples).

Raw and calibrated confidence are both stored.

```bash
python -m ecis.main --recalibrate platt
```

---



## Calibration watchdog:

`src/ecis/graphs/watchdog_graph.py`

Rolling window of resolved signals per reader:


| Condition                                      | Action                         |
| ---------------------------------------------- | ------------------------------ |
| ECE > 0.10                                     | Recalibrate (automatic)        |
| Negative skill for several consecutive windows | Propose `reduce_weight` (HITL) |


---



## Orchestration learning graph:

`src/ecis/graphs/learning_graph.py`

1. Load Category D rows from `chunk_classifications`.
2. Count **near-misses** (FinBERT confidence just below the skip threshold).
3. False-negative rate = near-misses / (logged signals + near-misses).
4. FN > 5% → **loosen** thresholds (more LLM).
5. FN < 2% → **tighten** (save compute).
6. If the proposed move is > 25%, queue HITL instead of applying.

```bash
python -m ecis.main --learn
```

---



## Vindication aggregation:

`src/ecis/extraction/vindication.py`

Win rates from `vindication_records` nudge keyword / FinBERT / LLM weights (core three renormalised to 0.85, agreement bonus held at 0.15). A single-reader move larger than 50% is treated as structural and goes to HITL.

```bash
python -m ecis.main --vindicate
```

The triangulator reads weights from SQLite on every chunk, so the next extract run uses the new mix.

---



## Human-in-the-loop:

`src/ecis/db/approvals.py` table `pending_approvals` ([db README](../src/ecis/db/README.md)).

Proposals include the action, the JSON payload, and evidence (ECE, FN rate, win rates). Resolve from:

- Dashboard **Approvals** tab
- `python -m ecis.main --approve <id>` / `--reject <id>`
- `POST /approvals/{id}/approve` or `/reject`

Rejecting logs the decision and leaves thresholds/weights unchanged.

---

