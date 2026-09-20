# Video specifications — 9:16 vertical

| Property | Value |
|---|---|
| Aspect ratio | 9:16 |
| Resolution | 2160 × 3840 |
| Orientation | Portrait / vertical |
| Quality | 4K UHD |
| Video codec | H.264 (CRF 18) |
| Audio codec | AAC |
| Frame rate | 24 fps (matches the approved 16:9 master) |
| Duration | 180.0 s (exactly 03:00 — identical to the approved 16:9 master) |
| Scene count | 10, in the same order as the 16:9 master |
| Narration | Same 16 Kokoro `af_bella` beats, reused unchanged from `../mp3` |
| Export filename | `Mycroft-thesisguard-brief-9x16-4k-Dhrumil_Shah.mp4` |
| Export location | `./output/Mycroft-thesisguard-brief-9x16-4k-Dhrumil_Shah.mp4` |

## Safe-area requirements

All headline, stat, source, and footer text is placed inside a safe box of
`{left: 120, right: 120, top: 170, bottom: 170}` pixels on the 2160×3840
canvas (defined as `SAFE` in `../src/MycroftThesisGuardBrief9x16.tsx`). Nothing
required for comprehension is placed outside this box, and no text is
allowed to touch or cross the canvas edge.

## Typography requirements

- Headline serif: 104–118px (down from 132–150px in the 16:9 cut — narrower
  canvas, same visual weight relative to safe width).
- Body/stat serif: 40–74px depending on role.
- Mono kickers/source tags: 20–27px, unchanged letter-spacing ratios.
- All type sizes were chosen to stay legible at a 1080-logical-pixel mobile
  viewport (this render is 2x that reference width).

## What changed vs. the 16:9 master, and why

- Every scene that placed an evidence image **beside** the headline now
  places it **below** the headline, full safe-width.
- Every horizontal token row (pipeline chains, agent workflow, loop stages)
  is now a **vertical stack with down-arrow connectors** — the same
  left-to-right reading order becomes top-to-bottom, which is the natural
  scroll/read direction on a vertical screen.
- Two-column comparison cards (available/not-supplied, illustrative-example
  pair) are stacked top/bottom instead of side by side.
- No image is stretched or distorted: `object-fit: cover` with a fixed
  `objectPosition` is used exactly as in the 16:9 master, only the crop
  window changed shape.
- Narration audio, timing (`AUDIO_BEATS`), scene order, on-screen copy, and
  every cited figure/source label are byte-identical to the approved
  16:9 cut. See `../CURRENT-RENDER-MANIFEST.md` for the authoritative frame
  map both cuts share.

**Educational research and model output; not personalized financial advice
or an investment recommendation.**
