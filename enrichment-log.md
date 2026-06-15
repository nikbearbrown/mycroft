# Chapter Enrichment Log — mycroft

**Date:** 2026-06-15
**Pass:** Tables & Figures enrichment (in place, `chapters/`)
**Design authority:** `brutalist/CLAUDE.md` (D3 v7) + `brutalist/DESIGN.md` (visual constitution)

## Totals

| Metric | Count |
|---|---|
| TABLE comments rendered → markdown tables | 37 |
| TABLE comments remaining | 0 |
| FIGURE comments bound + preserved | 33 |
| Figure image references in chapters | 64 |
| Static SVGs (`images/`) | 68 |
| PNGs (300 DPI, `images/`) | 68 |
| Interactive D3 v7 files (`d3/`) | 40 |
| Chapters with a `## Prompts` section | 18 |

## What changed

- **Pass 1 — Tables:** every `<!-- [TABLE: …] -->` comment replaced with a GitHub-flavored markdown table inferred from surrounding prose, with an italic `*Table N — caption*` line. No headings added above tables.
- **Pass 2 — Figures:** each `[IMAGE/FIGURE/DIAGRAM/INFOGRAPHIC/CHART]` comment was **preserved** (never removed); an `![alt](images/{slug}-fig-NN.png)` + `*Figure N.N — title*` was inserted directly above it. Each bound figure got a brutalist static SVG (hardcoded palette, viewBox `0 0 700 420`, role/title/desc) and a self-contained D3 v7 HTML companion (pinned cdnjs 7.9.0, `var(--color-*)` theming, dark mode, reduced motion, ResizeObserver, `(event,d)` handlers, zero-baseline bars, inline FALLBACK_DATA, ARIA).
- **Pass 3 — CAJAL reconciliation:** figure comments were bound to the existing CAJAL figure number that depicts them by content (not blind sequential); remaining unreferenced CAJAL figures were inserted at semantic spots. Every `images/*-fig-*.png` is now referenced (no orphans).
- **Pass 4 — PNG:** `node scripts/svg-to-png.mjs` regenerated PNGs from updated SVGs. SVG/PNG parity = 68/68.
- **Pass 5 — Prompts:** every enriched chapter carries a `## Prompts` section, one entry per figure (files + brutalist generation prompt).

## Invariants honored

- No prose, headings, or exercises altered outside comment regions and the appended `## Prompts` sections.
- No FIGURE comments removed. All image references resolve from the book root (`images/…`).
- Palette: zero off-palette (Okabe-Ito) colors remain in `images/*.svg`.
