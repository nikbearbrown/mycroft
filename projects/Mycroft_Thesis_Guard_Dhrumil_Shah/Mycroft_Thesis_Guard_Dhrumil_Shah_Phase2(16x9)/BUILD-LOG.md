# Build log — Mycroft Phase 2, 16:9 cut

## Starting point

The portrait cut (`Mycroft_Dhrumil_2_Project(9x16)`) was already finished: 2160 × 3840, 2:56, 20 of 20 checks passing, built from code cells 49–63 of `Mycroft_Dhrumil1.ipynb`. The landscape version had to carry the same content without becoming a second, diverging film.

## Approach: re-layout, not rescale

Scaling a portrait video into a 16:9 frame gives pillarboxing and small text. Landscape has roughly half the usable height and twice the width, so the content was re-composed:

- Cells 2–9 of `video_generation.py` (helpers, charts, architecture data, narration, subtitles) are reused unchanged. The renderer patches the canvas constants in memory — `W, H`, safe area, content band, subtitle line — before executing them, so every sprite helper adapts automatically.
- Cell 10 (the portrait scene layouts) is **not** reused. `render_16x9.py` defines its own 16 scene functions on a two-column grid: 1680 px columns with a 120 px gutter.
- The voiceover MP3s are copied from the portrait folder, so beat lengths, subtitle cues and total runtime match to the millisecond.

## Layout decisions

| Beat | Portrait | Landscape |
|---|---|---|
| B03 | Agent chain stacked vertically | Horizontal chain with arrows between agents |
| B04–B09 | Chips or charts above the code panel | Chips and charts left, code right |
| B10 | Leaderboard, then a crossfade to figure 01 | Leaderboard left, figure 01 fading in on the right |
| B11 | Figure 03 panels cycling below the bars | Bars left, panels cycling right |
| B13 | Figure 08 split into two stacked panels | Figure 08 shown whole |
| B15 | Nine levels at 150 px each, full width | Nine compact 118 px levels, centred at 2600–3200 px |
| B16 | Chips in a single column | Chips in two columns |

Consequence worth noting: charts and figures are larger here than in portrait, because they no longer share vertical space with text.

## Problems hit

1. **The architecture PNG was written with portrait geometry.** The shared Cell 6 saves that diagram as it executes, before the landscape layout exists. The renderer now overwrites it with the landscape version after defining `draw_architecture_16x9()`.
2. **The source folder had been renamed** to `Mycroft_Dhrumil_2_Project(9x16)` between sessions, so the first copy step failed. Paths were updated rather than assumed.
3. **Safe-area reporting fired during the `sheet` pass** for the stale portrait diagram. It clears before the real render, and the final run reported nothing outside the safe area.

## Render

5,286 frames in 10.5 minutes (~0.12 s per 4K frame) using PyAV, since local group policy blocks `ffmpeg.exe`. Output: 34.0 MB, H.264 CRF 16 with AAC 256 kbps, `faststart` enabled. All 21 checks pass, including a parity check that this cut's runtime matches the 9:16 one.

## Keeping the two cuts in step

1. Edit the narration or data in `video_generation.py` (this folder's copy and the portrait folder's copy should stay identical).
2. Delete the affected `narration/scene_XX.mp3` in both folders so the voice is regenerated.
3. Run `python render_16x9.py full` here and `python render_local.py full` in the portrait folder.
4. Run `python make_project_data.py` in both folders to refresh the JSON documentation.

## Possible next steps

- Add a licensed music bed at `assets/background_music.mp3` in both folders.
- Re-record the narration in your own voice and re-render both cuts.
- Re-render inside the Colab session where Phase 2 ran, to pick up the live metric CSV files and the per-fold walk-forward animation, which needs `walk_forward_fold_metrics.csv`.
- A 1:1 square cut for LinkedIn would need another layout pass, most likely a hybrid of these two.
