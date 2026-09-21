# Shot list — Mycroft Phase 2, 16:9 cut (3840 × 2160, 30 FPS, 16 beats)

Frame furniture on every beat: progress bar at y = 150, section label ("CELL n · TOPIC · nn/16") at y = 196, "Dhrumil Shah" top right, scene title at y = 262 (104 px), content band y = 470 → 1700, subtitles centred at y = 1900. Beats fade in over 0.35 s and out over 0.30 s; elements rise 50 px (cubic ease-out); the camera is locked, with slow 3.5 % zooms on notebook figures.

**Grid:** two columns of 1680 px with a 120 px gutter — left column at x = 180, right column at x = 1980. Beats that need width (the fold timeline, the diagnostics gallery, the architecture) span the full 3480 px content width.

| Beat | Time | Title | Layout | Left / full width | Right |
|---|---|---|---|---|---|
| B01 | 0:00–0:12.6 | Mycroft Phase 2 | Centred | MYCROFT wordmark, subtitle, name card, five chips in one row | — |
| B02 | 0:12.6–0:21.0 | Up or down in 5 trading days? | Full + two columns | Question card with `target_up_5d`, then the low-signal card | The honest-measurement card |
| B03 | 0:21.0–0:32.2 | Built on Mycroft Phase 1 | Three columns + full width | 184,138 rows / 120 tickers / 2020-2026 stat cards | Phase 1 agent chain drawn as a horizontal flow beneath |
| B04 | 0:32.2–0:45.2 | 18 new causal features | Two columns | 18 feature chips in two sub-columns | Feature equation and the MACD code panel (callout on `macd`) |
| B05 | 0:45.2–0:54.5 | Market regime detector | Two columns | `MarketRegimeDetector.fit()` with a callout on the training-date slice | Days-per-regime bars (968 / 429 / 100 / 23) |
| B06 | 0:54.5–1:06.4 | Purged walk-forward validation | Full + split row | Fold timeline across the full width; 154,378 and 27,600 cards below | Purge code with a callout on the `target_date` line |
| B07 | 1:06.4–1:19.0 | Nine models, one pipeline | Two columns | 3 × 3 model cards with real hyperparameters | `linear_svm_sgd` pipeline code, callout on the SGD arguments |
| B08 | 1:19.0–1:29.5 | Stability across folds | Two columns | Mean walk-forward ROC-AUC bars, leader legend | Notebook figure 02 with a slow zoom |
| B09 | 1:29.5–1:37.4 | Three ensembles, no leakage | Two columns | Weight bars (0.371 / 0.267 / 0.267 / 0.095) and three method cards | Weighting code, callout on the formula |
| B10 | 1:37.4–1:55.3 | The untouched holdout | Two columns | 12-model leaderboard with bootstrap whiskers | Figure 01 fading in at 60 %, summary card beneath |
| B11 | 1:55.3–2:06.3 | Probabilities you can trust | Two columns | Calibration-error bars (0.0365 → 0.0294 / 0.0280) | Figure 03 whole, then ROC, PR and calibration panels |
| B12 | 2:06.3–2:21.0 | Regime matters | Two columns | Figure 04 regime timeline with a slow zoom | AUC-by-regime bars with n labels, crossfading to figure 05 |
| B13 | 2:21.0–2:29.1 | Three more views | Centred full width | Figures 06 → 07 → 08 in sequence; figure 08 fits whole in 16:9 | — |
| B14 | 2:29.1–2:37.9 | The honest verdict | Two columns | Verdict card, 95 % interval on a number line, quoted verdict | Four stat cards in a 2 × 2 block |
| B15 | 2:37.9–2:44.6 | The Phase 2 workflow | Centred | Nine-level workflow, compact nodes, dashed regime feed | — |
| B16 | 2:44.6–2:56.2 | Evidence you can trust | Centred | Six summary chips in two columns, name, thanks, advisory note | — |

## Code panels

Real notebook code, re-wrapped to the 1680 px column, with a moving amber callout.

| Beat | Notebook source | Highlighted |
|---|---|---|
| B04 | Cell 4 — EMA / MACD block | the `work["macd"]` assignment |
| B05 | Cell 5 — `MarketRegimeDetector.fit()` | the training-date slice |
| B06 | Cell 6 — `walk_forward_folds()` | the `target_date < train_end - embargo` purge |
| B07 | Cell 7 — `build_phase2_models()` | the `SGDClassifier` arguments |
| B09 | Cell 10 — `build_ensembles()` | `mean_roc_auc - 0.5` weighting |

## What changed from the 9:16 cut

- **Two columns instead of stacking.** Charts and figures sit beside their explanation, so both are larger than in portrait.
- **Figure 08 is shown whole.** Its 2.8:1 shape fits the landscape frame, so the portrait cut's split panels are unnecessary.
- **The agent chain runs left to right** with arrows between agents, rather than top to bottom.
- **The architecture diagram uses compact nodes** (118 px tall) to fit nine levels in the shorter frame, centred at 2600–3200 px wide.
- **The intro chips form a single row** rather than a vertical stack.
- **Subtitles sit at y = 1900,** clear of the content band but higher in the frame than in portrait.

## Architecture diagram (B15)

```
Phase 1 engineered features (184,138 rows · 120 tickers)
                     ↓
        +18 causal features → 44 model features
                     ↓
   ┌───────────────────────────┬──────────────────────────────┐
Market regime detector          Purged + embargoed splits
(KMeans k=4, train only)        (4 walk-forward folds + holdout)
   ┆                                        ↓
   ┆                           9-model zoo (fitted per fold)
   ┆                                        ↓
   ┆                   Out-of-fold predictions → 3 ensembles
   ┆                                        ↓
   ┆                     Validation selection (linear_svm_sgd)
   ┆                                        ↓
   ┆              Untouched holdout (27,600 rows, bootstrap CI)
   ┆                                        ↓
   └┄┄→ Regime performance | Calibration | 8 figures
                                            ↓
                              signal_diagnostic.json
```
