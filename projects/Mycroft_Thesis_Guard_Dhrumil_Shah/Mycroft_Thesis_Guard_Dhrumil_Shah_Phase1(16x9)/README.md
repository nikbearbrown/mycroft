# Mycroft ThesisGuard — 3-Minute Evidence Review Film

This folder contains the complete, reproducible source for Dhrumil Shah's
three-minute **Mycroft ThesisGuard** technical explainer. The film is an
evidence-first research review, not investment advice and not a trading-demo
video.

## Deliverable

- **Master:** 3840 × 2160, 16:9, 24 fps, exactly 03:00
- **Renderer:** Remotion / React / TypeScript within the supplied
  `brutalist.art-main` workspace
- **Narration:** supplied MP3 beat recordings, synchronized frame-by-frame
- **Evidence:** captured screenshots from the supplied notebook, report, and
  proposal. No fabricated terminal result, chart, or model metric is used.

The current cut intentionally omits the narrated `B10b` audio beat to retain
an exact three-minute runtime. Its real Cell 50 visualization-scope evidence
is still shown in Beat 9. See [SOURCE-SCRIPT.md](SOURCE-SCRIPT.md).

## What the film proves (and what it does not)

The film can visibly support the recorded 184,138-row/120-company run,
chronological evaluation, five-model comparison, logistic-regression holdout
result (ROC AUC 0.5158; Brier 0.2466), moderate drift, 120 reports, 600 trace
events, zero automated decisions, and the human-review boundary.

The supplied materials contain **figure-file creation records**, but not the
actual generated plot files. The film therefore shows the authentic Cell 50
record and explicitly says it does not invent charts. This is a deliberate
truthfulness constraint; see [FACTCHECK.md](FACTCHECK.md).

## Folder map

```text
mycroft-thesisguard-brief/
├── src/MycroftThesisGuardBrief.tsx  # complete 4K Remotion composition
├── assets/evidence/                 # captured, provenance-labelled evidence
├── mp3/                             # supplied narration beats
├── scripts/                         # sync, render, verification, still-QA
├── CURRENT-RENDER-MANIFEST.md       # canonical 180 s render map
├── final_beat_sheet.json            # archived supplied narration/plan source
├── beat_sheet.json                  # archived supplied planning source
├── SOURCE-SCRIPT.md                 # exact narration used in this cut
├── PRODUCTION-PLAN.md               # 10-scene visual/evidence map
├── PROOF-COMPLIANCE.md              # skeptical review matrix
├── FINAL-QA.md                      # rendered-master verification
├── FACTCHECK.md                     # claims and limitations
├── REFERENCE-ANALYSIS.md            # reference-video production principles
├── ASSET-PROVENANCE.md              # source location for every evidence asset
├── SCREEN-RECORDING-PLAN.md         # truthful optional capture plan
├── INTEGRATION.md                   # Remotion registry contract
└── README.md
```

`CURRENT-RENDER-MANIFEST.md`, the TypeScript composition, and
`SOURCE-SCRIPT.md` are the authoritative runtime documents. The two beat-sheet
JSON files and `mp3/timings.json` are preserved source materials; they describe
an earlier 233.6-second planning treatment and must not be mistaken for the
rendered 180-second composition.

## Prerequisites

This is designed to live inside the supplied Brutalist.art workspace:

- Windows PowerShell 5.1+ or PowerShell 7+
- Node.js 20+ (the supplied workspace runtime also works)
- the `runtime/remotion` dependencies installed
- a compatible Chrome/Chrome Headless Shell installation used by Remotion

No remote API, model account, or private data is required to render this
version. The committed media assets are sufficient.

## Build the video

From this directory:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\render-4k.ps1
```

The script synchronizes the composition and the required assets into the
workspace renderer, renders the MP4, and calls the verification script. The
output is:

```text
output/mycroft-thesisguard-brief-4k.mp4
```

To only synchronize source and assets:

```powershell
.\scripts\sync-to-remotion.ps1
```

To verify an already-rendered master:

```powershell
.\scripts\check-video.ps1 -VideoPath .\output\mycroft-thesisguard-brief-4k.mp4
```

To extract ten readable review frames after rendering:

```powershell
.\scripts\qc-stills.ps1 -VideoPath .\output\mycroft-thesisguard-brief-4k.mp4
```

## Development preview

After synchronization, open a terminal at `runtime/remotion` and run:

```powershell
npm run studio
```

Choose the **Mycroft-ThesisGuard-Brief / MycroftThesisGuardBrief** composition.
The composition is registered in `runtime/remotion/src/Root.tsx`.

## GitHub checklist

Commit the complete Brutalist.art workspace (including the registered
composition in `runtime/remotion/src/Root.tsx`) and this folder. Do commit
the `src`, documentation, audio, and evidence assets. Do not commit
`output/`, `_qc/`, `node_modules/`, or generated Remotion caches.

Before publishing a public video or repository, review
[PROOF-COMPLIANCE.md](PROOF-COMPLIANCE.md). The film is designed to be
truthful and reviewable; it does not claim features, charts, live interfaces,
or a hosted URL that were not supplied.

## Visual reference use

The supplied reference video informed only general production principles:
warm editorial palette, clear hierarchy, one idea per scene, progressive
reveals, thin bordered cards, and restrained motion. Its narration, exact
wording, specific UI, and unique creative assets were not copied. See
[REFERENCE-ANALYSIS.md](REFERENCE-ANALYSIS.md).
