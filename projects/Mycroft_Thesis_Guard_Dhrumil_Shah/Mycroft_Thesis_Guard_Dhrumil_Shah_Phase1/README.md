# Mycroft ThesisGuard — 9:16 Vertical Recomposition

## Project

Mycroft ThesisGuard — Dhrumil Shah's evidence-first review film. This folder
is a **completely separate, isolated 9:16 (portrait) recomposition** of the
approved 16:9 4K master at `../` (`mycroft-thesisguard-brief`). Nothing in
`../` was modified to build this.

## Description

A native 2160×3840 vertical version of the same three-minute film, built the
same way the 16:9 master was: a single Remotion/React/TypeScript composition
driven by measured narration timing, with real captured evidence from the
Mycroft notebook and Implementation Report. Every scene was **redrawn** for
portrait — image-beside-headline layouts became image-below-headline,
horizontal token chains became vertical chains with down-arrow connectors,
side-by-side comparisons became top/bottom stacks. Nothing was cropped or
stretched from the 16:9 render.

## Purpose of the 9:16 version

The 16:9 master is built for landscape playback (YouTube, a desktop review).
This version targets vertical/mobile-first placements (Shorts, Reels, TikTok,
phone-first sharing) without sacrificing legibility of the underlying
evidence — every stat, source citation, and screenshot crop was re-checked
against a 2160-wide canvas, not just resized.

## Folder structure

```text
mycroft-thesisguard-brief/                 [existing 16:9 project — untouched]
├── src/MycroftThesisGuardBrief.tsx
├── assets/evidence/                       [reused by this folder, not copied]
├── mp3/                                   [reused by this folder, not copied]
├── output/mycroft-thesisguard-brief-4k.mp4
├── ... (all other existing 16:9 files, unmodified)
│
└── mycroft-thesisguard-9x16/               [this folder — new, isolated]
    ├── src/
    │   └── MycroftThesisGuardBrief9x16.tsx  # complete 4K vertical Remotion composition
    ├── config/
    │   ├── video-config.json
    │   ├── films-manifest.json
    │   └── render-config.json
    ├── scripts/
    │   ├── sync-to-remotion.ps1
    │   ├── render-4k.ps1
    │   ├── check-video.ps1
    │   └── qc-stills.ps1
    ├── docs/
    │   ├── README.md                        # this file
    │   ├── FILMS.md
    │   ├── RENDERING.md
    │   └── VIDEO-SPECIFICATIONS.md
    ├── assets/                              # empty by design — see "Assets" below
    ├── output/
    │   └── Mycroft-thesisguard-brief-9x16-4k-Dhrumil_Shah.mp4
    └── _qc/final/                           # 10 review stills after rendering
```

## Assets

`assets/` in this folder is intentionally empty. Evidence screenshots and
narration audio are **reused, not duplicated**, directly from the approved
16:9 reel's `../assets/evidence/` and `../mp3/` (Step 9 of the build
requirements: reuse existing assets, don't duplicate large files
unnecessarily). If a vertical-specific asset is ever needed, it belongs in
this `assets/` folder — none was needed for this cut, since every existing
screenshot re-crops cleanly at portrait width.

## Dependencies

- Node.js 20+ (Remotion CLI, React 18, TypeScript 5 — same versions already
  installed in `runtime/remotion/package.json`)
- Windows PowerShell 5.1+ or 7+
- A local Chrome install or the bundled Remotion `chrome-headless-shell`
- `ffmpeg`/`ffprobe` (bundled with `@remotion/compositor-win32-x64-msvc`, or
  a system install)

No new npm packages were added — this reel renders through the existing
`runtime/remotion` workspace, exactly like the 16:9 master.

## Installation

Nothing to install beyond what the workspace already has. If
`runtime/remotion/node_modules` is missing, install it once from the
workspace root:

```powershell
cd ../../../../runtime/remotion
npm install
```

## Build / render instructions

```powershell
cd .   # this folder
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\render-4k.ps1
```

See [RENDERING.md](RENDERING.md) for the full command reference, the
development-preview command, and troubleshooting.

## Final video specifications

| Property | Value |
|---|---|
| Resolution | 2160 × 3840 |
| Aspect ratio | 9:16 (portrait) |
| Quality | 4K UHD |
| Video codec | H.264 |
| Audio codec | AAC |
| Frame rate | 24 fps |
| Duration | 180.0 s (03:00, identical to the 16:9 master) |

Full detail in [VIDEO-SPECIFICATIONS.md](VIDEO-SPECIFICATIONS.md).

## Output location

```text
mycroft-thesisguard-9x16/output/Mycroft-thesisguard-brief-9x16-4k-Dhrumil_Shah.mp4
```

## Preserved from the approved project

- Same 10-scene story and order (executive summary → problem → data →
  method → results → falsifiability stop → agent workflow → evidence
  boundary → auditable loop → your-turn/close).
- Same narration (16 Kokoro `af_bella` beats, byte-identical MP3s, reused not
  re-synthesized).
- Same cited evidence (`ASSET-PROVENANCE.md`, `FACTCHECK.md`,
  `PROOF-COMPLIANCE.md` in `../` remain the authoritative record — nothing
  here contradicts them).
- Same financial-education disclaimer in the closing card.

**Educational research and model output; not personalized financial advice
or an investment recommendation.**
