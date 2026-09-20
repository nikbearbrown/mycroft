# Reference-video analysis — safe production adaptation

The supplied `debug-hallucination_Aug21.mp4` was reviewed from beginning to
end before authoring. It is a 3840 × 2160 (16:9), H.264/AAC, 24 fps video of
about 107 seconds, organized into short editorial modules.

## Principles adapted for this Mycroft film

- A warm cream field, dark editorial serif, small uppercase kickers, and a
  restrained terracotta accent.
- One central thought per scene, with generous whitespace and thin,
  lightly-rounded evidence cards.
- Progressive, narration-timed reveals instead of dense slides or full
  diagrams appearing at once.
- Technical facts paired with a readable artifact or source label.
- A short executive summary upfront and a sparse, memorable title finish.
- Limited motion: fades, small rises, connector reveals, and holds long
  enough to read at 4K.

## What this film does not copy

No reference-video narration, exact wording, screenshots, UI, named scene,
unique illustration, audio, or sequence is reused. The final render is a
custom Remotion composition at
`src/MycroftThesisGuardBrief.tsx`, using only Mycroft project evidence and
original narration. There is no `ClaudeComposerAsk`, `MycroftBrief`, or
`ClaudeTitleOutro` scene in the current 180-second render.

The authoritative runtime map is
[CURRENT-RENDER-MANIFEST.md](CURRENT-RENDER-MANIFEST.md).

