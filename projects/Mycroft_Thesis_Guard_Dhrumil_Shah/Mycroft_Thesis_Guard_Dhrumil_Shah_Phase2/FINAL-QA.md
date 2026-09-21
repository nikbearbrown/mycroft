# Final QA — mycroft_project_4k_9x16.mp4

Run: `python render_local.py full`, 2026-09-19. Probe and checks are printed in `outputs/render_log.txt` and were re-confirmed against the copy in this folder.

## Format and synchronisation

| Check | Result |
|---|---|
| Resolution 2160 × 3840 | PASS |
| Aspect ratio 9:16 | PASS |
| Frame rate 30 FPS | PASS |
| Frame count matches the beat timeline (5,286) | PASS |
| Audio stream present (AAC 48 kHz stereo) | PASS |
| Audio and video durations within 0.1 s (176.20 / 176.20) | PASS |
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

20 of 20 checks pass.

## Manual review

Checked on the contact sheet (`outputs/contact_sheet.jpg`) and the full-resolution stills in `scenes/`:

- Charts and code panels are legible at phone size; the smallest type on screen is 30 px at 4K (about 15 px on a 1080-wide phone).
- No overlapping elements; subtitles never cover content, which stops at y 2660.
- Notebook figures keep their aspect ratio. Wide figures (03, 08) are shown panel by panel rather than squeezed.
- Model names, feature names and agent names on screen match the notebook spelling exactly.
- Fades and crossfades land within each beat, so no transition cuts a sentence.

## Fixed during production

| Issue | Fix |
|---|---|
| Bar labels counted up with the animation and briefly showed numbers the notebook never produced (for example "938 days") | Labels now always display the final real value |
| First voiceover ran 3:48, over the Shorts limit | Script tightened to 435 words and voice rate raised to +27 %, giving 2:56 |
| Figure 03's three panels were cropped at estimated thirds, risking cut axis labels | Crop boundaries measured from the actual image (0.335 / 0.665) |

## Re-verifying

```bash
python render_local.py full
```

The run reprints all 20 checks. To re-verify without re-rendering, `python make_project_data.py` re-probes the MP4 and rewrites `video_manifest.json`, including the SHA-256 of the file.
