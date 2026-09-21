# Narration script — Mycroft Phase 2 (16:9 cut, 2:56)

Identical to the 9:16 cut: same words, same voiceover files, same beat timings.

Voice: edge-tts `en-US-AndrewNeural` at rate `+27%`. Each beat starts with 0.30 s of silence and ends with 0.45 s.
Subtitles reproduce this text word for word (85 cues, 40 characters maximum per cue).
Total: 435 spoken words over 176.20 s.

---

### B01 · Mycroft Phase 2 — 0:00.00 → 0:12.63

> Hi, I am Dhrumil Shah, and this video is about how I extended Mycroft with a Phase 2 pipeline that stress-tests nine machine-learning models and three ensembles on 120 stocks, with purged walk-forward validation and market regimes.

### B02 · Up or down in 5 trading days? — 0:12.63 → 0:21.03

> Can daily price and volume data predict whether a stock rises over the next five trading days? The signal is tiny, so the real challenge is measuring it honestly.

### B03 · Built on Mycroft Phase 1 — 0:21.03 → 0:32.17

> Phase 2 builds on Phase 1's 184,138 rows across 120 tickers. Phase 1's five review agents stay in place; Phase 2 focuses on the model layer beneath them.

### B04 · 18 new causal features — 0:32.17 → 0:45.23

> I added 18 new causal features, such as 60-day momentum, MACD, Bollinger position, ATR, distance to 52-week highs and lows, volume trends, and relative strength. The model now sees 44 features.

### B05 · Market regime detector — 0:45.23 → 0:54.53

> A MarketRegimeDetector runs KMeans on market momentum and volatility, fitted on training dates only, to label each day bull or bear, with high or low volatility.

### B06 · Purged walk-forward validation — 0:54.53 → 1:06.40

> Labels are purged and embargoed to block leakage. Four expanding walk-forward folds handle validation, and the final 27,600 rows, from March 2025, stay untouched as a holdout.

### B07 · Nine models, one pipeline — 1:06.40 → 1:18.97

> Nine models compete: logistic regression, a linear SVM trained with SGD, Naive Bayes, LDA, KNN, AdaBoost, histogram gradient boosting, LightGBM, and XGBoost.

### B08 · Stability across folds — 1:18.97 → 1:29.53

> Across the folds, the linear SVM ranked first, at a mean ROC-AUC of 0.513. Every model sits near 0.5: this is a hard problem.

### B09 · Three ensembles, no leakage — 1:29.53 → 1:37.40

> From out-of-fold predictions only, I built three ensembles: a soft vote, a skill-weighted average, and a stacked logistic-regression meta-learner.

### B10 · The untouched holdout — 1:37.40 → 1:55.27

> With selection fixed in advance, the linear SVM scored 0.521 on the holdout, with a 95% bootstrap interval of 0.510 to 0.533. Logistic regression reached 0.5335, but picked after the fact among twelve, it is optimistically biased.

### B11 · Probabilities you can trust — 1:55.27 → 2:06.30

> Calibration cut the selected model's expected calibration error from about 0.037 to under 0.03, and the ROC, precision-recall, and reliability curves show the full picture.

### B12 · Regime matters — 2:06.30 → 2:21.00

> Regime matters: in the bull, high-volatility regime, holdout ROC-AUC reached 0.62, but on only 720 observations. In the largest regime, bull and low volatility, it was 0.497, essentially random.

### B13 · Three more views — 2:21.00 → 2:29.07

> Three more views: new-feature correlations with the target, probability distributions by outcome, and consensus accuracy as the top models disagree.

### B14 · The honest verdict — 2:29.07 → 2:37.93

> The automated verdict: the confidence interval excludes 0.5, so there is weak but measurable ranking signal. Modest, but honest and reproducible.

### B15 · The Phase 2 workflow — 2:37.93 → 2:44.60

> Every model, metric, regime label, and figure is saved to disk, so the analysis can be audited and rerun.

### B16 · Evidence you can trust — 2:44.60 → 2:56.20

> This extension of Mycroft shows how feature engineering, rigorous validation, ensembles, and calibration turn raw market data into evidence you can trust, even when it is weak. I'm Dhrumil Shah. Thanks for watching.

---

## Pronunciation handling

The speech engine receives spelled-out forms of some abbreviations, while the subtitles keep the correct spelling:

| Written (subtitles) | Spoken to the engine |
|---|---|
| ROC-AUC | R O C A U C |
| SGD / LDA / KNN / SVM / ATR / MACD | letter by letter |
| KMeans | K-means |
| MarketRegimeDetector | Market Regime Detector |
| LightGBM / XGBoost | Light G B M / X G Boost |

## Editing the script

The narration lives in the `SCRIPT` list in `video_generation.py` (Cell 8). After editing, delete the matching `narration/scene_XX.mp3` so it is regenerated, then re-render. Cell 14 re-checks every spoken number against the notebook data and fails loudly if a claim no longer matches.
