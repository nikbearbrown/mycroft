# Captions — Mycroft Phase 3 (9:16)

- **File:** `subtitles/mycroft_phase3_4k_9x16.srt` (copy in `outputs/`), 93 cues.
- **Burned in:** yes, centred at y 2830 on a black plate at 69 % opacity, white bold 66 px.
- **Soft track:** not embedded in the MP4. Upload the SRT alongside the video where switchable captions are wanted.
- **Machine-readable:** `captions/cues.json` carries the same cues with beat IDs.

## Rules applied

| Rule | Implementation |
|---|---|
| Matches the narration exactly | Cues are chunked from the same `SCRIPT` strings that drive the voice |
| Short enough for mobile | One line, 40 characters maximum (QA fails above 42) |
| Sentence-aware | A chunk closes at `.`, `?`, `!`, `;` or `:` once it is at least 12 characters |
| Timed to speech | Each beat's cues divide that beat's measured voiceover length in proportion to their character count, starting after the 0.30 s lead-in |
| Ends before the video does | Checked automatically at the end of every render |
| Technical spelling preserved | Captions keep `AgentConfig`, `SharedContext`, `MycroftOrchestrator`, `ROC-AUC`, `Amihud`; only the speech engine receives respellings |
| Name and project spelling | "Dhrumil Shah" and "Mycroft" throughout |

## Cue distribution

| Beat | Cues | Beat | Cues |
|---|---|---|---|
| B01 intro | 9 | B07 agent4 | 7 |
| B02 foundation | 10 | B08 agent5 | 12 |
| B03 data | 7 | B09 orchestrator | 7 |
| B04 agent1 | 10 | B10 review | 9 |
| B05 agent2 | 10 | B11 validation | 10 |
| B06 agent3 | 8 | | |

(Exact per-beat lists are in `beat_sheet.json` under `subtitle_cues`.)

## Editing captions

Captions are generated, not hand-written, so edit the narration in `phase3_video.py` and re-render: the SRT, the burned-in text and the timings all follow. Hand-editing the SRT alone would desynchronise it from the burned-in captions.

## Sample (first three cues)

```
1
00:00:00,300 --> 00:00:02,0xx
Hi, I am Dhrumil Shah, and this video

2
00:00:02,0xx --> 00:00:04,1xx
is about Phase 3 of my Mycroft project,

3
00:00:04,1xx --> 00:00:06,2xx
where I expanded the system by building
```

The exact millisecond values are in the SRT itself; the pattern above shows the cue length and phrasing style.
