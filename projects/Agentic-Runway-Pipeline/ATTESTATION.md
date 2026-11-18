# Attestation — Agentic Runway-Risk Intelligence Pipeline

**Status at attestation:** advancing toward RUNNABLE-LIVE (on a small real-data set)
**Attested by:** Amruta Naik (acting reviewer, SOLO)
**Builds on:** the delivered runway-risk-scorer (RUNNABLE-SAMPLE)

This record states honestly what was tested, what was deliberately not tested, and
what the AI did vs. what a human decided. Assume only what is under "Tested."

---

## Tested (verified to work)

- **Schema validation (Sprint 1).** Break tests confirm the typed schema rejects
  malformed signals: bad signal_type, future dates, non-URLs, out-of-range scores.
- **Real ingestion (Sprint 1).** Live RSS feeds were pulled; real signals flowed
  through the validator and stayed UNVALIDATED (P2).
- **The research agent (Sprint 2).** The LangGraph agent runs plan -> search ->
  decide -> loop with a hard stop; it escalates search strategy and stops without
  inventing data. Demonstrated on real companies.
- **LLM extraction (Sprints 3-4).** LangChain structured output produced typed
  signals; the API model (Groq) classified a resignation as executive_change (conf 70)
  and a vague headline as news_mention (conf 20). The local model (llama3.2, Ollama)
  was measured and scored lower \u2014 documented, not hidden.
- **Dedup (Sprint 5).** Embedding dedup runs; on the sample it found no duplicates
  (correct \u2014 the signals were distinct events).
- **Storage + confidence + trend (Sprint 6).** Runs persist to DuckDB; per-brief
  confidence computed (openai 17/100 \u2014 honestly low, nothing validated); trend
  view renders across runs.
- **Serving (Sprint 7).** FastAPI endpoints and a Streamlit dashboard serve the
  stored data, read-only.
- **The human gate holds everywhere.** Every path ends at HALT-AWAITING-HUMAN; no
  component issues a verdict.

## Did NOT test (out of scope / unverified)

- **Live, at-scale real-world accuracy.** The pipeline ran on a small real-data set,
  not a production volume. Real-world predictive accuracy is unverified.
- **Independent review.** All review was solo. No second person confirmed the
  outputs, the agent's decisions, or the test adequacy.
- **Airflow orchestration (Sprint 7, deferred).** Scheduling was not built or tested;
  it is a later, separate step.
- **Whether the metrics truly predict runway.** The tool is a first-pass signal
  gatherer, not a validated financial model.

## What the AI proposed vs. what a human accepted

- The **agent** proposed which sources to search and when to stop \u2014 a human still
  validates every signal it gathered (none are auto-counted).
- The **LLM** proposed a type and confidence for each signal \u2014 a human must confirm
  before it scores (validated_by stays None until then).
- **No signal in this pipeline has been human-validated yet**, so the scorer has
  honestly scored nothing. That is the design working, not a gap.

## Known limits & guardrails

- The agent can miss or misread sources; every signal is confidence-scored and
  human-gated, and agent decisions are logged.
- Private companies have thin public data \u2014 signals are news/funding-grade, not
  SEC-grade. The confidence score and human gate exist for this.
- A small local model is weaker than the API model (measured in Sprint 4).

---

## Reviewer's decision

On the evidence above \u2014 passing break tests, demonstrated runs of every component,
and the human gate holding throughout \u2014 the pipeline is a working, honest,
end-to-end agentic system on a small real-data set. Advancing toward RUNNABLE-LIVE
would require at-scale real data and independent attestation, which are out of scope
for this phase.

*The AI gathered and structured. It did not decide. A human still judges.*
