# Video specifications, design and export settings — Phase 3 (9:16)

## Export settings (as delivered)

| Property | Value |
|---|---|
| File | `outputs/mycroft_phase3_4k_9x16.mp4` |
| Resolution | 2160 × 3840 (true 4K portrait) |
| Aspect ratio | 9:16 |
| Frame rate | 30 FPS constant, 5,301 frames |
| Duration | 176.7 s (2:57), inside the 2–3 minute target |
| Video codec | H.264 (libx264), High profile, level 5.2, CRF 16, yuv420p |
| Audio codec | AAC-LC, 48 kHz, stereo, 256 kbps |
| Loudness | Narration peak-normalised to −1 dBFS |
| Streaming | `faststart` (moov atom first) |
| Captions | Burned in, plus `subtitles/mycroft_phase3_4k_9x16.srt` (93 cues) |

Equivalent settings if you re-encode elsewhere: `-c:v libx264 -preset medium -crf 16 -pix_fmt yuv420p -profile:v high -level:v 5.2 -r 30 -c:a aac -b:a 256k -movflags +faststart`. For H.265 instead, `-c:v libx265 -crf 20 -tag:v hvc1`.

## Mobile-safe layout (9:16)

| Region | Pixels |
|---|---|
| Left / right margins | 150 / 230 (the wider right margin clears the action rail) |
| Content column | x 150 → 1930 (1780 wide) |
| Frame furniture | progress bar y 405, section label y 450, title y 530 |
| Content band | y 820 → 2660 |
| Caption band | centred at y 2830 |
| Keep clear below | y 3100 (platform UI) |

Design rules followed: one major concept per screen, large type, short labels, vertically stacked workflows, no wide tables (the queue table is trimmed to six columns), code panels of 4–7 lines auto-sized to fit the column, and charts placed with captions rather than shrunk to fit beside text.

## Typography and palette

- **Type:** DejaVu Sans (titles 94 px, section labels 40 px, captions 66 px bold) and DejaVu Sans Mono for code and identifiers (34–46 px, chosen per panel so the longest line fits).
- **Palette:** dark technical interface — background gradient #080E1C → #101A30 with a faint grid; teal #2DD4BF primary; blue #388BFD; violet #A78BFA; amber #FBBF24 for callouts, flags and anomalies; red #F87171 for risk and market-wide events; green #4ADE80 for passing checks and reliable segments.
- **Contrast:** body text #ECF1FA on the dark ground; captions sit on a black plate at 69 % opacity.

## Motion

Fade in 0.35 s, fade out 0.30 s per beat; elements rise 50 px on a cubic ease-out; chains reveal node by node with arrows drawing in; bars and tables grow in time with the narration; notebook figures get a 3.5 % Ken-Burns zoom; paired panels crossfade over 0.5 s. Nothing spins, bounces or flies.

## Voice-over

edge-tts `en-US-AndrewNeural` (professional male English), rate +25 %, which measures ≈ 150 words per minute across the finished film — inside the 140–155 target. Replace it with your own recordings by adding `narration/scene_01_user.wav` … `scene_11_user.wav`; beat lengths follow your audio automatically.

## Background music

None is bundled, because no licensed track ships with this project. The renderer mixes one in automatically if you drop a file at `assets/background_music.mp3`: it loops to length and is mixed at 0.07 gain (about −23 dB), well under the narration, with the mix re-normalised afterwards.

Recommended style: subtle futuristic/technology instrumental — a slow synth pad with a soft pulse at 80–100 BPM, no vocals, no heavy percussion, minimal melodic movement so it never competes with speech. Sources to consider: Epidemic Sound "Ambient Technology", Artlist "Minimal Tech", or a Creative Commons ambient track with attribution. Keep it under −20 dB relative to narration and fade the last 3 seconds.

## Platform fit

| Platform | Fit |
|---|---|
| YouTube Shorts | Yes — 2:57 is inside the 3-minute limit |
| Instagram Reels / TikTok | Yes — 9:16 fills the frame; upload the SRT where supported |
| LinkedIn | Yes — portrait plays in-feed; attach the SRT for switchable captions |
| Portfolio site | Yes — `faststart` means playback starts before the download finishes |

## Render environment

PyAV 18.1.0 (FFmpeg libraries inside Python — no `ffmpeg.exe`, which local policy blocks), Python 3.14.7 on Windows 11, Pillow for drawing, Pygments for code highlighting, edge-tts for the voice. Full render: 5,301 frames in about 7 minutes.
