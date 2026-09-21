# Video specifications, design and export settings — Phase 3 (16:9)

## Export settings (as delivered)

| Property | Value |
|---|---|
| File | `outputs/mycroft_phase3_4k_16x9.mp4` |
| Resolution | 3840 × 2160 (4K UHD landscape) |
| Aspect ratio | 16:9 |
| Frame rate | 30 FPS constant, 5,301 frames |
| Duration | 176.7 s (2:57) — identical to the 9:16 cut |
| Video codec | H.264 (libx264), High profile, level 5.2, CRF 16, yuv420p |
| Audio codec | AAC-LC, 48 kHz, stereo, 256 kbps |
| Loudness | Narration peak-normalised to −1 dBFS |
| Streaming | `faststart` (moov atom first) |
| Captions | Burned in, plus `subtitles/mycroft_phase3_4k_16x9.srt` (93 cues) |

Equivalent re-encode elsewhere: `-c:v libx264 -preset medium -crf 16 -pix_fmt yuv420p -profile:v high -level:v 5.2 -r 30 -c:a aac -b:a 256k -movflags +faststart`. For H.265: `-c:v libx265 -crf 20 -tag:v hvc1`.

## Safe area and grid

| Region | Pixels |
|---|---|
| Left / right margins | 180 each |
| Content width | 3480 (x 180 → 3660) |
| Frame furniture | progress bar y 150, section label y 196, title y 262 |
| Content band | y 470 → 1700 |
| Caption band | centred at y 1900 |
| Lower limit for any element | y 2040 |
| Two-column grid | 1680 px columns, 120 px gutter; left x 180, right x 1980 |

180 px side margins (4.7 % of width) and a 140 px top margin keep titles inside the title-safe area used for broadcast and projection. The renderer records anything drawn outside the safe area and fails QA if the list is not empty; the final render reported none.

## Design system

Shared with the portrait cut, scaled for viewing distance:

- **Type:** DejaVu Sans (titles 104 px, section labels 44 px, captions 66 px bold) and DejaVu Sans Mono for code and identifiers (30–46 px, auto-sized per panel).
- **Palette:** dark technical interface — background #080E1C → #101A30 with a faint grid; teal #2DD4BF primary, blue #388BFD, violet #A78BFA, amber #FBBF24 for callouts and flags, red #F87171 for risk, green #4ADE80 for passing checks and reliable segments.
- **Layout:** one concept per screen; charts and code side by side rather than stacked; the review queue is the only full-width table, and it carries seven short columns.
- **Motion:** 0.35 s fade in, 0.30 s fade out, 50 px element rise, cubic ease-out, chains revealing node by node, bars growing with the narration, 3.5 % Ken-Burns zoom on notebook figures, 0.5 s crossfades between paired panels.

## Voice-over

edge-tts `en-US-AndrewNeural` (professional male English) at +25 %, ≈ 150 words per minute — the same MP3 files as the portrait cut, which keeps both films frame-accurate with each other. Replace with your own recordings via `narration/scene_01_user.wav` … `scene_11_user.wav` in both folders.

## Background music

Not bundled. Drop a licensed track at `assets/background_music.mp3` and re-render: it loops to length, mixes at 0.07 gain (about −23 dB) under the narration, and the mix is re-normalised afterwards.

Recommended style: subtle futuristic technology instrumental — slow synth pad with a soft pulse at 80–100 BPM, no vocals, no heavy percussion, minimal melodic movement.

## Platform fit

| Platform | Fit |
|---|---|
| YouTube (standard) | Yes — 4K UHD 16:9 at 30 FPS is the native format; upload the SRT for switchable captions |
| LinkedIn desktop feed | Yes — landscape plays in-feed and full-width on desktop |
| Conference or class slides | Yes — 16:9 matches slide masters; embed the file directly |
| Portfolio site | Yes — `faststart` starts playback before the download finishes |
| Shorts / Reels / TikTok | Use the 9:16 cut instead |

## Render environment

PyAV 18.1.0 (FFmpeg libraries in-process; local policy blocks `ffmpeg.exe`), Python 3.14.7 on Windows 11, Pillow for drawing, Pygments for code highlighting, edge-tts for the voice. Full render: 5,301 frames in about 9 minutes.
