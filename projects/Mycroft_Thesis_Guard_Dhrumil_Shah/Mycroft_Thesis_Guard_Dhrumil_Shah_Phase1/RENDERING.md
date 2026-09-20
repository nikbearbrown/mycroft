# Rendering — 9:16 vertical

All commands below run from this folder
(`youtube/mycroft-thesisguard-brief/mycroft-thesisguard-9x16/`) in Windows
PowerShell, exactly mirroring the approved 16:9 project's own scripts one
directory level deeper.

## Prerequisites

- Windows PowerShell 5.1+ or PowerShell 7+
- Node.js 20+ (verified working: Node v24.19.0 / npm 11.17.0)
- `runtime/remotion` dependencies already installed in the workspace
- A local Chrome or the bundled Remotion `chrome-headless-shell`
- The approved 16:9 reel's `../assets/evidence/` and `../mp3/` present and
  unmodified — the 9:16 build reuses them and does not duplicate them

## How to render the single composition (all 10 films are one composition)

There is one Remotion composition (`MycroftThesisGuardBrief9x16`) that
contains all 10 scenes as internal `<Sequence>` blocks — there is nothing to
render "per film" separately; the whole 180-second timeline renders in one
pass, same as the approved 16:9 master.

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\render-4k.ps1
```

This script:
1. Runs `sync-to-remotion.ps1` (copies the 9:16 TSX into
   `runtime/remotion/src/mycroft-brief/`, and copies the **reused** evidence
   images and narration MP3s from `../assets/evidence` and `../mp3` into
   `runtime/remotion/public-mycroft-brief/mycroft-brief/`).
2. Renders composition `MycroftThesisGuardBrief9x16` at 2160×3840, h264,
   CRF 18, to `output/Mycroft-thesisguard-brief-9x16-4k-Dhrumil_Shah.mp4`.
3. Runs `check-video.ps1` automatically to verify the output.

## To only synchronize source and assets (no render)

```powershell
.\scripts\sync-to-remotion.ps1
```

## To verify an already-rendered master

```powershell
.\scripts\check-video.ps1 -VideoPath .\output\Mycroft-thesisguard-brief-9x16-4k-Dhrumil_Shah.mp4
```

Checks: 2160×3840, 24 fps, 179.5–180.5 s, h264 video, aac audio, and prints
file size.

## To extract review stills after rendering

```powershell
.\scripts\qc-stills.ps1 -VideoPath .\output\Mycroft-thesisguard-brief-9x16-4k-Dhrumil_Shah.mp4
```

Writes 10 PNGs (one per scene) to `_qc/final/`.

## Development preview

After `sync-to-remotion.ps1` has run at least once:

```powershell
cd ../../../../runtime/remotion
npm run studio
```

Open the **Mycroft-ThesisGuard-Brief / MycroftThesisGuardBrief9x16**
composition (registered alongside the existing 16:9
`MycroftThesisGuardBrief` composition in `runtime/remotion/src/Root.tsx` —
neither entry was removed or modified by adding the other).

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `sync-to-remotion.ps1` throws "evidence assets are missing" | The approved 16:9 reel's `assets/evidence/` was moved or deleted | Restore `../assets/evidence/` — the 9:16 build has no assets of its own to fall back to by design (Step 9: reuse, don't duplicate) |
| `render-4k.ps1` throws "No local Chrome executable was found" | Neither the bundled `chrome-headless-shell` nor system Chrome is present | Run `npx remotion browser ensure` from `runtime/remotion`, or install Chrome |
| `check-video.ps1` throws a resolution mismatch | The Remotion `Composition` entry for `MycroftThesisGuardBrief9x16` in `Root.tsx` was edited or removed | Confirm `Root.tsx` still declares `width={2160} height={3840}` for that id |
| `check-video.ps1` throws a duration mismatch | `AUDIO_BEATS` in the 9:16 TSX was edited independently of the 16:9 file | The two files' `AUDIO_BEATS` arrays must stay identical — copy the array from `../src/MycroftThesisGuardBrief.tsx` if they drift |
| Text looks cropped at the very edge on a real phone | A scene's absolute `top`/`left` value was moved outside `SAFE` | Keep all text within the `SAFE = {left:120, right:120, top:170, bottom:170}` box defined in the TSX |

## Build commands (from the workspace root, for reference)

```powershell
# same two toolkit-level commands used for every reel in this workspace
./art run   youtube/mycroft-thesisguard-brief/mycroft-thesisguard-9x16
./art final youtube/mycroft-thesisguard-brief/mycroft-thesisguard-9x16
```

Note: this reel was rendered directly via `render-4k.ps1` (mirroring how the
approved 16:9 `mycroft-thesisguard-brief` reel itself was rendered, per its
own `README.md`), not via the `./art` beat-sheet pipeline used by the
toolkit's `ai-explainer`/`cli-explainer`/`deep-explainer` skills — this reel
does not have a `beat_sheet.json` of its own; it reuses the 16:9 reel's
supplied narration directly.
