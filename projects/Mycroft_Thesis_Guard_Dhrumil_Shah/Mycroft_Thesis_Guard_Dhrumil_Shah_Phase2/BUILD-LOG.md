# Build log — Mycroft Phase 2 video

## 1. Notebook review

Read `Mycroft_Dhrumil1.ipynb` (99 cells). Counting code cells only, cells 49–63 are exactly the section titled **"New Code – Mycroft"** (raw cells 70–99), which the notebook labels Phase 2 Cells 1–15. That section is the entire basis for the video.

What it contains: 18 new causal features, a KMeans market-regime detector fitted on training dates only, purged and embargoed splits with four expanding walk-forward folds, a nine-model zoo, out-of-fold ensembles, holdout scoring with ticker-clustered bootstrap intervals, sigmoid and isotonic calibration, performance by regime, an automated signal diagnostic, and eight figures.

Two findings shaped the script:
- Phase 2 creates **no AI agents**. The five agents in the project are Phase 1's, so the video shows them once, labelled as Phase 1's and unchanged.
- The result is weak by design of the honest evaluation: holdout ROC-AUC 0.521, 95 % interval 0.510–0.533. The story became "how to measure a weak signal honestly" rather than a performance boast.

## 2. Story and script

16 beats: problem → foundation → features → regimes → leakage control → models → walk-forward → ensembles → holdout → calibration → regimes in the holdout → diagnostics → verdict → architecture → outro, opening with the required introduction line.

First voiceover came out at 3:48, over the 3-minute Shorts limit. The script was tightened from 528 to 435 words with no fact removed, and the voice rate raised from +10 % to +27 %, giving 2:56.

## 3. Generator

`video_generation.py` (14 Colab cells) draws every frame with Pillow: a cached background, sprite-based text, cards, chips, stat cards, Pygments-highlighted code panels with animated callouts, animated bar and line charts, a fold timeline, and a nine-level architecture diagram. Notebook figures are placed in rounded white panels with a slow zoom. Subtitles are chunked from the narration and drawn per frame.

Design decisions:
- Sprites are built once per beat and composited per frame, so 4K stays fast (0.095 s per frame).
- A `put()` helper records anything drawn outside the safe area, turning layout errors into a QA failure instead of something you have to spot by eye.
- Scene length is derived from the real voiceover length, rounded up to a whole frame, so audio and video can't drift.
- Ten spoken numbers are re-checked against the data at render time.

## 4. Rendering on Windows

Google Colab was the original target, but rendering happened locally. Two obstacles:

1. **No Python at first.** Python 3.14.7 was then installed through Microsoft's Python Install Manager.
2. **Group policy blocks `.exe` files from user folders,** so `ffmpeg.exe`, `ffprobe.exe` and `edge-tts.exe` could not run even after installing FFmpeg through winget. Rather than work around the policy, the renderer moved to **PyAV**, which carries FFmpeg's libraries inside Python, and to `python -m edge_tts` for the voiceover.

`render_local.py` reuses Cells 2–10 of the Colab notebook unchanged and replaces only the encoding and probing layers. Both paths produce the same design from the same script.

## 5. Data available at render time

The eight figures were found in your Downloads folder and used as-is. The Phase 2 metric CSV and JSON files were not on this machine, so the generator fell back to the values printed in the notebook, which are stored in `video_generation.py` and mirrored in `data/phase2_results.json`.

One visible consequence: beat B08 shows mean walk-forward scores per model rather than an animated line per fold, because per-fold numbers live only in `walk_forward_fold_metrics.csv`. Your real figure 02 still shows the per-fold detail. Re-rendering inside the Colab session restores the animated version automatically.

## 6. Production fixes

| Issue | Fix |
|---|---|
| Animated bar labels displayed interpolated values mid-growth | Labels always show the final real value |
| Figure 03 panel crops were estimated | Boundaries measured from the image (0.335 / 0.665) |
| Runtime over the Shorts limit | Script tightened, voice rate raised |

## 7. Final render

5,286 frames in 9.9 minutes; 31.1 MB; 20 of 20 checks pass. Outputs: the MP4, the SRT, a contact sheet, 16 stills, the voiceover files, and this documentation set.

## 8. Possible next steps

- Add a licensed music bed at `assets/background_music.mp3` (it mixes in at −23 dB automatically).
- Re-record the narration in your own voice as `narration/scene_XX_user.wav`.
- Re-render inside Colab to pick up the live metric files and the per-fold animation.
- A 16:9 cut would need layout changes, since every position is tuned for portrait.
