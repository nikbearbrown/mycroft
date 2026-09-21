# Video specifications

## Delivered file

| Property | Value |
|---|---|
| File | `outputs/mycroft_project_4k_9x16.mp4` |
| Resolution | 2160 × 3840 (4K portrait) |
| Aspect ratio | 9:16 |
| Frame rate | 30 FPS (constant), 5,286 frames |
| Duration | 176.20 s (2:56) |
| Video codec | H.264 (libx264), High profile, level 5.2, CRF 16, yuv420p |
| Audio codec | AAC, 48 kHz, stereo, 256 kbps |
| Size | 31.1 MB |
| Streaming | `faststart` (moov atom at the front) |
| Subtitles | Burned in; sidecar `subtitles/mycroft_project_4k_9x16.srt` (85 cues) |

Note on resolution: 2160 × 3840 is 4K **portrait**. The landscape form, 3840 × 2160, is not used here.

## Safe area (portrait social UI)

| Region | Pixels |
|---|---|
| Left / right margins | 150 / 230 (the wider right margin clears the action rail) |
| Content column | x 150 → 1930 (1780 wide) |
| Top of frame furniture | y 400 (progress bar 405, section label 450, title 530) |
| Content band | y 820 → 2660 |
| Subtitle band | centred at y 2830 |
| Reserved for platform UI | below y 3100 |

The renderer records any element drawn outside this area and fails the QA check if the list is non-empty. The final render reported none.

## Design system

- **Typography:** DejaVu Sans (headings, body), DejaVu Sans Mono (code and identifiers). Titles 94 px, section labels 40 px, subtitles 66 px bold, code 34–46 px, chosen per panel so the longest line fits.
- **Palette:** near-black navy gradient background (#080E1C → #101A30) with a faint grid; teal #2DD4BF for the primary accent, blue #388BFD, violet #A78BFA, amber #FBBF24 for the 0.50 reference line and callouts, red #F87171 for below-chance and purge markers, green #4ADE80 for the verdict.
- **Motion:** 0.35 s fade in and 0.30 s fade out per beat; elements rise 50 px with cubic ease-out; bars and lines grow with the narration; notebook figures get a 3.5 % Ken-Burns zoom. No decorative motion.
- **Subtitles:** one line, 40 characters maximum, black rounded plate at 69 % opacity, white bold text.

## Platform notes

| Platform | Fit |
|---|---|
| YouTube Shorts | Yes. 2:56 is inside the 3-minute limit; 9:16 fills the frame |
| Instagram Reels | Yes. Upload the SRT separately or use platform captions; burned-in captions already display |
| LinkedIn | Yes. Portrait video plays in-feed; the SRT can be attached for toggleable captions |
| TikTok | Yes, format-wise |
| Portfolio / website | Yes. `faststart` means it begins playing before the whole file downloads |

The MP4 has no separate subtitle track, only burned-in captions. Upload `mycroft_project_4k_9x16.srt` alongside the video where you want captions viewers can switch off.

## Render environment

| Item | Value |
|---|---|
| Renderer | PyAV 18.1.0 (FFmpeg libraries in-process; no `ffmpeg.exe`, which local policy blocks) |
| Python | 3.14.7 on Windows 11 |
| Frame drawing | Pillow, with NumPy for the background gradient |
| Code highlighting | Pygments (Python lexer) |
| Voiceover | edge-tts, `en-US-AndrewNeural`, rate +27 % |
| Render time | 9.9 minutes for 5,286 frames (~0.095 s per 4K frame) |
| Colab equivalent | `video_generation.ipynb`, same design, encodes through the `ffmpeg` binary |

## Known format limitations

- No soft subtitle track inside the MP4 (PyAV path); the SRT covers that.
- No background music; add `assets/background_music.mp3` and re-render to mix one in at −23 dB.
- The preview mode in `video_generation.py` renders 1080 × 1920 at 10 FPS for quick checks; it is disabled for delivery.
