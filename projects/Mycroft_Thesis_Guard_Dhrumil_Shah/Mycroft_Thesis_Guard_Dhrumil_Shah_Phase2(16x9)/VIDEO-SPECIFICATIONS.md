# Video specifications — 16:9 cut

## Delivered file

| Property | Value |
|---|---|
| File | `outputs/mycroft_project_4k_16x9.mp4` |
| Resolution | 3840 × 2160 (4K landscape, UHD) |
| Aspect ratio | 16:9 |
| Frame rate | 30 FPS (constant), 5,286 frames |
| Duration | 176.20 s (2:56) — identical to the 9:16 cut |
| Video codec | H.264 (libx264), High profile, level 5.2, CRF 16, yuv420p |
| Audio codec | AAC, 48 kHz, stereo, 256 kbps |
| Size | 34.0 MB |
| Streaming | `faststart` (moov atom at the front) |
| Subtitles | Burned in; sidecar `subtitles/mycroft_project_4k_16x9.srt` (85 cues, same text as the portrait cut) |

3840 × 2160 is 4K **landscape**. The portrait counterpart, 2160 × 3840, lives in `Mycroft_Dhrumil_2_Project(9x16)`.

## Safe area and grid

| Region | Pixels |
|---|---|
| Left / right margins | 180 each |
| Content width | 3480 (x 180 → 3660) |
| Frame furniture | progress bar y 150, section label y 196, title y 262 |
| Content band | y 470 → 1700 |
| Subtitle band | centred at y 1900 |
| Lower limit for any element | y 2040 |
| Two-column grid | columns of 1680 px, 120 px gutter; left x 180, right x 1980 |

Margins of 180 px (4.7 % of width) and 140 px top keep titles inside the title-safe area used for broadcast and presentation displays. The renderer records anything drawn outside the safe area and fails QA if the list is non-empty. The final render reported none.

## Design system

Shared with the portrait cut, with type scaled for viewing distance:

- **Typography:** DejaVu Sans and DejaVu Sans Mono. Titles 104 px, section labels 44 px, subtitles 66 px bold, code 34–46 px chosen per panel, model cards 32/28 px.
- **Palette:** navy gradient background (#080E1C → #101A30) with a faint grid; teal #2DD4BF primary, blue #388BFD, violet #A78BFA, amber #FBBF24 for the 0.50 reference and callouts, red #F87171 for below-chance and purge markers, green #4ADE80 for the verdict.
- **Motion:** 0.35 s fade in, 0.30 s fade out, 50 px element rise, cubic ease-out, 3.5 % Ken-Burns zoom on notebook figures. Charts animate in time with the narration.
- **Subtitles:** one line, 40 characters maximum, black rounded plate at 69 % opacity.

## Platform notes

| Platform | Fit |
|---|---|
| YouTube (standard) | Yes. 4K UHD 16:9 at 30 FPS is the native format; upload the SRT for toggleable captions |
| LinkedIn (desktop feed) | Yes. Landscape plays well in-feed and on desktop |
| Conference or class slides | Yes. 16:9 matches slide masters; the file can be embedded directly |
| Portfolio site | Yes. `faststart` allows playback before the file finishes downloading |
| Shorts / Reels / TikTok | Use the 9:16 cut instead |

The MP4 has burned-in captions only, with no separate subtitle track. Upload `mycroft_project_4k_16x9.srt` alongside the video where switchable captions matter.

## Render environment

| Item | Value |
|---|---|
| Renderer | PyAV 18.1.0 (FFmpeg libraries in-process; no `ffmpeg.exe`, which local policy blocks) |
| Python | 3.14.7 on Windows 11 |
| Frame drawing | Pillow, NumPy background, Pygments code highlighting |
| Voiceover | edge-tts `en-US-AndrewNeural`, rate +27 % — the same MP3s as the portrait cut |
| Render time | 10.5 minutes for 5,286 frames (~0.12 s per 4K frame) |
| Generator | `render_16x9.py`, reusing Cells 2–9 of `video_generation.py` with landscape geometry |

## Known format limitations

- No soft subtitle track inside the MP4; the SRT covers that.
- No background music. Add `assets/background_music.mp3` and re-render to mix one in.
- Charts and figures are laid out for this exact frame. A different aspect ratio needs a new layout pass, not a rescale.
