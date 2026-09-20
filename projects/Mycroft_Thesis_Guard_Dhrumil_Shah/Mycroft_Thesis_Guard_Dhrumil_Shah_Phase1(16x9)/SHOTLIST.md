# Shot list — Mycroft ThesisGuard: Evidence Over Emotion

17 beats · ~3:11 · 3840×2160 @ 24 fps · Kokoro `af_bella` (free, local)

Every beat is a native Remotion render — no screen recordings, no stills, no
third-party imagery. Bookends use the toolkit's existing house scenes; body
beats use `MycroftBrief` (four variants).

| Beat | Scene | Variant | Headline / purpose | Accent (the one terracotta moment) |
|---|---|---|---|---|
| B00 | `ClaudeComposerAsk` | — | Cold open + executive summary; "Hi, I'm Dhrumil Shah" | send button + spark |
| B01 | `MycroftBrief` | chain | **Thesis Drift.** — the reason moves, unlogged | `no record` |
| B02 | `MycroftBrief` | contrast | **Not A Predictor.** — review layer, not buy/sell | the "THIS" panel |
| B03 | `MycroftBrief` | stats | **Check It First.** — 184,138 rows / 120 tickers | `0` prices forward-filled |
| B04 | `MycroftBrief` | grid | **Only What Was Knowable.** — causal features | `no lookahead` |
| B05 | `MycroftBrief` | stats | **Split By Time.** — 127,858 / 26,880 / 27,600 | `27,600` held back |
| B06 | `MycroftBrief` | grid | **Let The Baseline Win.** — five candidates | `prior baseline` |
| B07 | `MycroftBrief` | stats | **Barely Above Chance.** — ROC AUC 0.5158 | `0.5158` |
| B08 | `MycroftBrief` | contrast | **Surface The Drift.** — moderate drift, reported | the "HONEST MOVE" panel |
| B08b | `MycroftBrief` | contrast | **It Refuses To Guess.** — bias withheld on purpose | the "WHAT THIS ONE DOES" panel |
| B09 | `MycroftBrief` | chain | **Five Agents, One Gate.** | `human gate` |
| B10 | `MycroftBrief` | stats | **Zero Automated Decisions.** — 120 / 600 / 0 | `0` |
| B10b | `MycroftBrief` | grid | **Make It Inspectable.** — the visual layer | `challengeable` |
| B11 | `MycroftBrief` | contrast | **No Source, No Verdict.** — the boundary | the returned-status panel |
| B12 | `MycroftBrief` | chain | **The Whole Loop.** — the full pipeline | `human decides` |
| B12b | `MycroftBrief` | chain | **Try This Yourself.** — viewer takeaway | `no source? stop.` |
| B13 | `ClaudeTitleOutro` | — | Title restate + `@HumanitariansAI` | terracotta period |

## Structural notes

- **Executive summary is B00**, spoken in the cold open exactly as requested:
  who I am, what it is, and what the viewer will get in three minutes.
- **The honest result (B07) is the spine.** The reel is built so the weak ROC
  AUC lands as the finding, not as an embarrassment — the beats on either side
  (baseline-may-win, drift-surfaced) set it up and pay it off.
- **Two refusal beats** (B08b, B11) carry the falsifiability requirement: the
  system's limits are shown, not narrated around.
- **B12b is the scaffolded viewer task** — the discipline transfers without
  the codebase.

## Output

- `mycroft-thesisguard-brief.mp4` — clean master, 4K
- `mycroft-thesisguard-brief-slate.mp4` — review cut with beat burn-ins
