# Sprint 4 — Local vs. API Extraction: Quality Comparison

**Goal:** Swap the Sprint 3 extraction (cloud API) to a local model via Ollama,
and measure the quality difference. The deliverable is the comparison itself —
not making the local model "win."

## Setup

| | Sprint 3 (API) | Sprint 4 (local) |
|---|---|---|
| Model | Groq-hosted LLM (cloud API) | llama3.2 (3B) via Ollama, on-device |
| Cost | paid per call | free |
| Privacy | data sent to provider | nothing leaves the machine |
| Internet | required | not required |

Same prompt, same schema, same two headlines.

## Results

**Headline A: "OpenAI safety employee resigns, claiming the company's culture is broken"**

| | type | confidence |
|---|---|---|
| Groq (API) | `executive_change` ✅ | 70 |
| llama3.2 (local) | `funding_layoff` ❌ (not a valid schema type) | 0 |

**Headline B: "It's not AI anymore, it's 'super intelligence'" (vague)**

| | type | confidence |
|---|---|---|
| Groq (API) | `news_mention` ✅ | 20 |
| llama3.2 (local) | `news_mention` ✅ | 0 |

## What the comparison shows

- **Type accuracy dropped.** The local model mistyped a clear executive change
  as `funding_layoff` — a label that isn't even in the schema (it invented one).
  The API model classified it correctly.
- **Confidence calibration collapsed.** The API model produced a meaningful 70-vs-20
  gap that separates a real signal from noise. The local model returned 0 for both,
  giving the human reviewer no signal-strength cue.
- **The vague headline was typed correctly by both** — but the local model still
  gave no usable confidence.

## The honest trade-off

A small local model (llama3.2, 3B) is **free and fully private**, but its extraction
quality and confidence calibration are **noticeably worse** than the cloud API on the
same inputs. For a pipeline where a human validates every signal anyway, a weaker
extractor raises the human's workload (more to correct) but does not break the design
— the human gate still catches the errors.

**Decision for this project:** keep the API extractor (Sprint 3) as the primary path
for quality; the local path (Sprint 4) stays available for cost-sensitive or
privacy-sensitive runs, with the documented quality cost.

## Possible next step (not required for Sprint 4)

A larger local model (e.g. llama3.1:8b) would likely close much of the gap at the cost
of more RAM and slower runs — itself a model-size vs. quality vs. resource trade-off
worth a follow-up measurement.

## Boundary (unchanged)

Both extractors only EXTRACT structure. Neither decides risk or validates. Every
signal stays `validated_by: None` until a human confirms (P2).
