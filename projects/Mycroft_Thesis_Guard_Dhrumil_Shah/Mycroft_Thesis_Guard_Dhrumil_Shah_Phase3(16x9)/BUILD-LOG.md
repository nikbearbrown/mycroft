# Build log — Mycroft Phase 3, 16:9 cut

## Starting point

The portrait cut was already finished: 2160 × 3840, 2:57, 18 of 18 checks passing, built from the Phase 3 section of `Mycroft_Dhrumil2.ipynb` (cells A1–A13). The landscape version had to carry identical content without becoming a second, diverging film.

## Approach: re-layout, not rescale

Landscape has roughly half the height and twice the width of the portrait frame, so scaling would leave pillarboxed bars and small text. Instead:

- `render_16x9.py` reads `phase3_video.py` and executes everything up to its scene code — the Phase 3 facts, the code snippets, the narration, the voiceover synthesis and the caption cues — with the canvas constants patched to landscape in memory (`W, H`, safe area, content band, caption line, output filenames).
- The portrait scene functions are **not** reused. Eleven new scene functions lay each beat out on a two-column grid: 1680 px columns with a 120 px gutter.
- The voiceover MP3s are copied from the portrait folder, so beat lengths, caption timings and total runtime match to the millisecond.

## Layout decisions

| Beat | Portrait | Landscape |
|---|---|---|
| B01 | Five agents in a ring around the hub | Hub above, five agent chips in one row |
| B02–B08 | Diagram or chart stacked above the code | Diagram or chart left, code right |
| B04 | Figure, then stat cards below | Figure left, four stat cards in a 2 × 2 block right |
| B05 | Code, chips, bars, then the figure | Code, chips and bars left; the figure right |
| B09 | Stage diagram, then code | Stage diagram left; code plus a "Degrade, don't stop" card right |
| B10 | Six-column queue table | Full-width table with the Sector column restored; governance cards left, code right |
| B11 | Checklist, score card, closing titles stacked | Checklist left; score card and closing titles right |

## Problems hit

1. **Caption collisions.** The first portrait pass had put several code panels low enough to reach the caption band; that fix (optional label chips, tighter figure heights) carried into this cut, and the landscape pass reported no safe-area violations on its first run.
2. **Quoting.** Two batch edits had to move from inline shell commands into script files, because PowerShell has no heredoc and mangles em-dashes in inline Python.

## Render

5,301 frames at 3840 × 2160 through PyAV (libx264 CRF 16 + AAC 256 kbps, faststart), since local group policy blocks `ffmpeg.exe`. Nineteen automated checks run at the end: eleven on format, sync, captions, safe area and runtime parity with the 9:16 cut, and eight on the Phase 3 facts.

## Keeping both cuts in step

1. Edit narration or facts in `phase3_video.py` (keep the copy in each folder identical).
2. Delete the affected `narration/scene_XX.mp3` in both folders.
3. Run `python phase3_video.py full` in the portrait folder and `python render_16x9.py full` here.
4. Run `python make_project_data.py` in both folders.

## Possible next steps

- Export the five missing Phase 3 charts and re-render both cuts so Agents 3 and 4 get their real visuals.
- Add a licensed music bed to `assets/background_music.mp3` in both folders.
- Record the narration in your own voice.
- A 1:1 square cut for LinkedIn would need another layout pass, most likely a hybrid of these two.
