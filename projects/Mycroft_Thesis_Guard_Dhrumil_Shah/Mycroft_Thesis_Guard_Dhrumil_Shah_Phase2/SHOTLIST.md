# Shot list — Mycroft Phase 2 (2160 × 3840, 30 FPS, 16 beats)

Every beat shares the same frame furniture: a progress bar at y = 405, a section label ("CELL n · TOPIC · nn/16") at y = 450, "Dhrumil Shah" at the top right, a scene title at y = 530, content between y = 820 and 2660, and the subtitle band centred at y = 2830. Each beat fades in from the background over 0.35 s and out over 0.30 s; elements rise 50 px as they appear (cubic ease-out). The camera is locked; the only movement is a slow 3.5 % zoom on notebook figures.

| Beat | Time | Title | Visual | Animation | Chart / code | Assets |
|---|---|---|---|---|---|---|
| B01 | 0:00–0:12.6 | Mycroft Phase 2 | MYCROFT wordmark, subtitle, name card, five capability chips | Wordmark drop-in, staggered chips | — | — |
| B02 | 0:12.6–0:21.0 | Up or down in 5 trading days? | Question card with `target_up_5d`, low-signal card, honest-measurement card | Cards rise in sequence | — | — |
| B03 | 0:21.0–0:32.2 | Built on Mycroft Phase 1 | 184,138 rows / 120 tickers / 2020-2026 stat cards; Phase 1 agent chain | Value count-up, chain reveal | — | `agent_visualizations/phase1_agent_chain.png` |
| B04 | 0:32.2–0:45.2 | 18 new causal features | 18 feature chips (2 columns), feature equation, MACD code panel | Chip cascade, amber callout on the `macd` line | Cell 4 `engineer_phase2_features()` | `code_screenshots/cell04_macd_features.png` |
| B05 | 0:45.2–0:54.5 | Market regime detector | `MarketRegimeDetector.fit()` code panel, days-per-regime bars | Callout on the training-window slice, bars grow | Cell 5 regime detector | `code_screenshots/cell05_regime_detector.png` |
| B06 | 0:54.5–1:06.4 | Purged walk-forward validation | Fold timeline (train / purge + embargo / validation / holdout), row cards, purge code | Fold bars extend along the date axis | Cell 6 `walk_forward_folds()` | `charts/purged_walk_forward_timeline.png`, `code_screenshots/cell06_purge_embargo.png` |
| B07 | 1:06.4–1:19.0 | Nine models, one pipeline | 3 × 3 model cards with real hyperparameters, `linear_svm_sgd` code | Cards pop in, callout on the SGD arguments | Cell 7 `build_phase2_models()` | `code_screenshots/cell07_model_zoo_svm.png` |
| B08 | 1:19.0–1:29.5 | Stability across folds | Mean walk-forward ROC-AUC bars, then notebook figure 02 | Bars grow, figure zooms | Figure 02 | `assets/.../02_walk_forward_stability.png` |
| B09 | 1:29.5–1:37.4 | Three ensembles, no leakage | Ensemble weight bars, three method cards, weighting code | Bars grow, cards stagger, callout on the formula | Cell 10 `build_ensembles()` | `code_screenshots/cell10_ensemble_weights.png` |
| B10 | 1:37.4–1:55.3 | The untouched holdout | 12-model leaderboard with bootstrap whiskers → notebook figure 01; summary card | Bars grow, whiskers snap in, crossfade at 66 % | Figure 01 | `charts/holdout_leaderboard_anim_final.png`, `assets/.../01_holdout_leaderboard.png` |
| B11 | 1:55.3–2:06.3 | Probabilities you can trust | Calibration-error bars; figure 03 whole, then ROC, PR and calibration panels | Bars grow, panels crossfade with zoom | Figure 03 (+ 3 crops) | `assets/.../03_roc_pr_calibration.png` |
| B12 | 2:06.3–2:21.0 | Regime matters | Figure 04 timeline above AUC-by-regime bars → figure 05 | Ken-Burns zoom, bars grow, crossfade at 70 % | Figures 04, 05 | `assets/.../04_regime_timeline.png`, `05_performance_by_regime.png` |
| B13 | 2:21.0–2:29.1 | Three more views | Figures 06, 07, then 08 split into two stacked panels | Sequential crossfades with zoom | Figures 06, 07, 08 | `assets/.../06…`, `07…`, `08_model_disagreement.png` |
| B14 | 2:29.1–2:37.9 | The honest verdict | Verdict card, 95 % interval on a number line against 0.50, four stat cards, quoted verdict | Interval bar extends, stats stagger | Holdout AUC interval | — |
| B15 | 2:37.9–2:44.6 | The Phase 2 workflow | Nine-level architecture diagram with branch arrows | Level-by-level build, arrows draw on | Architecture | `architecture/mycroft_phase2_architecture.png` |
| B16 | 2:44.6–2:56.2 | Evidence you can trust | Six summary chips, name card, thanks line, advisory note | Chips stagger, name fades up | — | — |

## Code panels on screen

Each panel shows real notebook code, re-wrapped (never reworded) to fit portrait width, with a moving amber callout bar on the lines under discussion.

| Beat | Notebook source | Highlighted lines |
|---|---|---|
| B04 | Cell 4 — EMA / MACD block | the `work["macd"]` assignment |
| B05 | Cell 5 — `MarketRegimeDetector.fit()` | the training-date slice fed to KMeans |
| B06 | Cell 6 — `walk_forward_folds()` | the `target_date < train_end - embargo` purge |
| B07 | Cell 7 — `build_phase2_models()` | the `SGDClassifier` arguments |
| B09 | Cell 10 — `build_ensembles()` | the weight formula, `mean_roc_auc - 0.5` |

## Architecture diagram (B15)

```
Phase 1 engineered features (184,138 rows · 120 tickers)
            ↓
+18 causal features → 44 model features
            ↓
   ┌────────────────────────┬──────────────────────────┐
Market regime detector       Purged + embargoed splits
(KMeans k=4, train only)     (4 walk-forward folds + holdout)
   │                                    ↓
   │                         9-model zoo (fitted per fold)
   │                                    ↓
   │                 Out-of-fold predictions → 3 ensembles
   │                                    ↓
   │                   Validation selection (linear_svm_sgd)
   │                                    ↓
   │             Untouched holdout (27,600 rows, bootstrap CI)
   │                                    ↓
   └──────→ Regime performance | Calibration | 8 figures
                                        ↓
                           signal_diagnostic.json
```

Every node maps to a cell in the notebook; the dashed line marks the regime labels feeding the regime-performance analysis.
