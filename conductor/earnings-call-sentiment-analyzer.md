# Earnings Call Sentiment Analyzer — Conductor Flow

## Mode

Dialogic. Silent mode is unavailable while the recipe is `DRAFT`.

## Entry Point

A human supplies an approved local earnings-call transcript plus company, ticker, quarter, and fiscal-year metadata.

## Flow Steps

### Step 1 — Open Run

- Labor: AI
- AI task: Create a run ID; record recipe version, source path, source hash, metadata, and sample-versus-real classification.
- Handoff condition: Provenance fields are complete.
- On failure: Stop.

### Step 2 — Validate Input

- Labor: AI with human provenance gate
- AI task: Confirm file type, size, extractable text, and constrained upload path.
- Human task: Confirm the source classification and permitted use.
- Handoff condition: Source and input gates are recorded.
- On failure: Reject the transcript without changing the source.

### Step 3 — Parse Transcript

- Labor: AI
- AI task: Run the project's parser to create ordered evidence chunks with section, speaker, and role attribution.
- Handoff condition: At least one chunk exists; unknown values remain explicit; parser metrics are logged.
- On failure: Stop and preserve parser diagnostics.

### Step 4 — Score Evidence

- Labor: AI
- AI task: Run the recorded FinBERT model over the chunks and retain positive, neutral, negative, and net-tone values for every chunk.
- Handoff condition: Every aggregate traces to stored chunk evidence and model metadata.
- On failure: Stop; do not emit partial aggregate conclusions as final.

### Step 5 — Produce Two Outputs

- Labor: AI
- AI task: Export the structured run log and draft the human report using `reports/templates/earnings-call-sentiment-analyzer.md`.
- Handoff condition: Log and report are separate, cross-linked artifacts.
- On failure: Stop before review.

### Step 6 — Human Evidence Review

- Labor: Human [PA] [IJ] [EI]
- Human task: Inspect section boundaries, speaker roles, unknown attributions, strongest evidence chunks, and whether language matches the displayed interpretation.
- Handoff condition: Named decision, date, tested items, untested items, and correction requests are recorded.
- On failure: Keep the recipe at `DRAFT`; do not use results downstream.

## Hard Gates

- Transcript provenance
- Extractable-text and path-safety validation
- Parser attribution
- Model/version traceability
- Chunk-to-aggregate provenance
- Human adequacy review
- Report/log separation

## Current Sample

- Raw input: `data/raw/earnings-call-sentiment-analyzer/northstar-cloud-systems-q3-fy2026.txt`
- Classification: user-created synthetic/sample transcript
- Permitted use: parser, orchestration, UI, and sentiment-pipeline testing
- Prohibited claim: evidence about a real issuer or investment
