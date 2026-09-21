# Fact check — every claim in the video traced to the notebook

Source for all rows: `Mycroft_Dhrumil1.ipynb`, section **"New Code – Mycroft"** (code cells 49–63 = Phase 2 Cells 1–15), using the outputs printed in that notebook. The renderer re-checks the ten numeric claims marked **automated** on every run; all ten pass (`FINAL-QA.md`).

## Spoken claims

| # | Beat | Claim in the narration | Notebook source | Printed value | Status |
|---|---|---|---|---|---|
| 1 | B01 | "nine machine-learning models and three ensembles" | Cell 7 output; Cell 11 | 9 models listed; `soft_vote_ensemble`, `weighted_ensemble`, `stacking_ensemble` | Verified |
| 2 | B01 | "on 120 stocks" | Cell 3 output | "tickers: 120" | **Automated** |
| 3 | B01/B06 | "purged walk-forward validation" | Cell 6 | purge on `target_date`, embargo of 5 trading days, 4 expanding folds | Verified |
| 4 | B02 | "whether a stock rises over the next five trading days" | Cell 3; `Phase2Config.horizon_days = 5` | target `target_up_5d` | Verified |
| 5 | B03 | "184,138 rows across 120 tickers" | Cell 3 output | "Phase 1 rows: 184,138 \| tickers: 120" | **Automated** |
| 6 | B03 | "Phase 1's five review agents stay in place" | Phase 1 cell (notebook cell 21) | ThesisCapture, EvidenceRetrieval, ContradictionAndDriftDetection, BehavioralBiasReview, HumanDecisionGate | Verified — Phase 2 adds no agents |
| 7 | B04 | "18 new causal features … 44 features" | Cell 4 output | "Added 18 features \| total model features: 44" | **Automated** |
| 8 | B04 | Feature names spoken (60-day momentum, MACD, Bollinger position, ATR, 52-week distances, volume trends, relative strength) | Cell 4 `NEW_NUMERIC_FEATURES` | all 18 names shown on screen match the list | Verified |
| 9 | B05 | "KMeans on market momentum and volatility, fitted on training dates only" | Cell 5 `MarketRegimeDetector` | KMeans(k=4) on 20-day momentum and volatility; `fit_until` = validation start | Verified |
| 10 | B05 | Days per regime on screen: 968 / 429 / 100 / 23 | Cell 6 output | Bull-Low 968, Bear-Low 429, Bull-High 100, Bear-High 23 | Verified |
| 11 | B06 | "the final 27,600 rows, from March 2025" | Cell 6 output | "holdout rows: 27,600 \| holdout starts 2025-03-07" | **Automated** |
| 12 | B06 | On screen: 154,378 development rows; fold boundaries | Cell 6 output | development 154,378; folds ending 2022-04-21 / 2023-01-04 / 2023-09-19 / 2024-06-03 | Verified |
| 13 | B07 | The nine model names and their settings | Cell 7 output and source | matches `build_phase2_models()` exactly | Verified |
| 14 | B08 | "the linear SVM ranked first, at a mean ROC-AUC of 0.513" | Cell 9 walk-forward summary | `linear_svm_sgd` 0.5133 (top of table) | **Automated** |
| 15 | B08 | "Every model sits near 0.5" | Cell 9 summary | range 0.4993 – 0.5133 | Verified |
| 16 | B09 | "three ensembles … soft vote, skill-weighted average, stacked logistic-regression meta-learner" | Cell 10 | matches `build_ensembles()`; weights = mean AUC − 0.5, normalised | Verified |
| 17 | B09 | Weights on screen: 0.371 / 0.267 / 0.267 / 0.095 | Cell 10 output | same four values, recomputed at render time | Verified |
| 18 | B10 | "the linear SVM scored 0.521 on the holdout, 95 % interval 0.510 to 0.533" | Cell 11 / Cell 14 JSON | 0.5208, CI [0.5098, 0.5334] | **Automated** |
| 19 | B10 | "Logistic regression reached 0.5335 … among twelve" | Cell 11 table; Cell 14 `models_compared` | 0.5335; 12 candidates | **Automated** |
| 20 | B10 | "picked after the fact … optimistically biased" | Cell 14 `multiple_testing_note` | "the best holdout figure is an order statistic and is optimistically biased" | Verified |
| 21 | B11 | "calibration error from about 0.037 to under 0.03" | Cell 12 output | uncalibrated 0.0365 → sigmoid 0.0294, isotonic 0.0280 | **Automated** |
| 22 | B12 | "bull, high-volatility regime … 0.62 … only 720 observations" | Cell 13 output | 0.6225 on n = 720 | **Automated** |
| 23 | B12 | "the largest regime, bull and low volatility … 0.497" | Cell 13 output | 0.4968 on n = 20,880 (largest) | **Automated** |
| 24 | B14 | "the confidence interval excludes 0.5, so there is weak but measurable ranking signal" | Cell 14 `verdict` | quoted verbatim on screen | **Automated** (CI low 0.5098 > 0.5) |
| 25 | B14 | Stat cards: 0.513 ± 0.011, 0.521, 12 models, 56.4 % up-rate | Cell 14 JSON | 0.5133 ± 0.0114; 0.5208; 12; 0.5642 | Verified |
| 26 | B15 | "every model, metric, regime label, and figure is saved to disk" | Cells 6, 9, 11, 13, 14, 15 | `models/*.joblib`, `metrics/*.csv`, `regimes/*.csv`, `signal_diagnostic.json`, `figures/*.png` | Verified |

## Claims deliberately **not** made

- No claim that Phase 2 beats Phase 1. The two phases use different split rules (Phase 2 adds purging and an embargo), so their holdout numbers are not directly comparable.
- No claim of trading profitability, returns or a strategy. The notebook runs no backtest.
- No new AI agents are attributed to Phase 2, because cells 49–63 create none.
- No pattern is described in figures 06, 07 or 08 beyond what their axes show; the narration names what each chart plots and leaves interpretation on screen.
- No performance claim uses the best-after-the-fact model as if it were unbiased; the video states the opposite.

## Rounding rules used

| Spoken | Underlying value | Rule |
|---|---|---|
| 0.513 | 0.5133153… | 3 decimal places |
| 0.521 | 0.5208461… | 3 decimal places |
| 0.510 / 0.533 | 0.5098236… / 0.5333653… | 3 decimal places, interval endpoints |
| 0.5335 | 0.5335 (as printed) | 4 decimal places, to avoid an ambiguous third digit |
| "about 0.037" / "under 0.03" | 0.0365 / 0.0294, 0.0280 | hedged deliberately, since the fourth digit varies with the run |
| 0.62 | 0.6225 | 2 decimal places |
| 0.497 | 0.4968 | 3 decimal places |

## Data availability note

The metric CSV and JSON files from Phase 2 were not on the rendering machine, so the video used the values printed in the notebook (stored in `video_generation.py` as `FALLBACK_*` tables and reproduced in `data/phase2_results.json`). The eight figures are the real PNG files your notebook wrote. If you re-render inside the Colab session where Phase 2 ran, the generator reads the CSV and JSON files instead and re-verifies every number automatically.
