# Final QA — mycroft_project_4k_16x9.mp4

Run: `python render_16x9.py full`, 2026-09-20. Full output in `outputs/render_log.txt`.

## Format and synchronisation

| Check | Result |
|---|---|
| Resolution 3840 × 2160 | PASS |
| Aspect ratio 16:9 | PASS |
| Frame rate 30 FPS | PASS |
| Frame count matches the beat timeline (5,286) | PASS |
| Audio stream present (AAC 48 kHz stereo) | PASS |
| Audio and video durations within 0.1 s (176.20 / 176.20) | PASS |
| Same runtime as the 9:16 cut (within 0.05 s) | PASS |
| Subtitles end before the video ends | PASS |
| No subtitle cue longer than 42 characters | PASS |
| Nothing drawn outside the safe area | PASS |

## Content accuracy (checked automatically at render time)

| Check | Result |
|---|---|
| 184,138 rows / 120 tickers | PASS |
| 18 new features, 44 total | PASS |
| 27,600 holdout rows from March 2025 | PASS |
| Selected model = linear SVM (`linear_svm_sgd`) | PASS |
| Walk-forward mean ROC-AUC 0.513 | PASS |
| Holdout 0.521 [0.510, 0.533] | PASS |
| Logistic regression 0.5335, twelve candidates | PASS |
| Calibration error about 0.037 → under 0.03 | PASS |
| Bull / high-volatility 0.62 on 720 observations | PASS |
| Bull / low-volatility 0.497, largest regime | PASS |
| Confidence interval excludes 0.50 | PASS |

21 of 21 checks pass.

## Manual review

Checked on `outputs/contact_sheet.jpg` and the landscape stills in `scenes/`:

- Two-column layouts hold on every beat; no column overruns its 1680 px width.
- Charts and figures are larger than in the portrait cut, since they no longer share vertical space with text.
- Figure 08 is shown whole, which is how the notebook drew it.
- Subtitles at y 1900 never collide with content, which ends at y 1700.
- Model, feature and agent names match the notebook spelling exactly.
- Crossfades (B10 figure 01, B12 figure 05, B11 panels, B13 gallery) land inside their beats.

## Parity with the 9:16 cut

| Item | Status |
|---|---|
| Narration text | Identical (435 words, 16 beats) |
| Voiceover audio | The same MP3 files |
| Beat timings | Identical to the millisecond |
| Subtitle cues | 85 cues, identical text and timings |
| Numbers on screen | Identical, from the same data |
| Layout | Re-composed for landscape (see `SHOTLIST.md`) |

## Production note

During the first `sheet` pass, the architecture PNG was still being written with the portrait node geometry inherited from the shared cells. The landscape renderer now overwrites it with the correct diagram. No other layout issues were reported.

## Re-verifying

```bash
python render_16x9.py full
```

Reprints all 21 checks. To re-verify without re-rendering, `python make_project_data.py` re-probes the MP4 and rewrites `video_manifest.json`, including its SHA-256.
