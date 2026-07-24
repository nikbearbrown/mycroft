---
status: DRAFT
todos_open: 2
last_gate: null
attestation: null
recipe_version: 0.1.0
---

# Earnings Call Sentiment Analyzer

## Purpose

Turn an approved earnings-call transcript into section-, speaker-, and evidence-chunk-level FinBERT sentiment signals that a human analyst can inspect. Sentiment is a model judgment about language tone, not evidence of truthfulness, valuation, management quality, or future returns.

## Required Reads

- `SNICKERDOODLE.md`
- `DATA_CONTRACT.md`
- `projects/Earnings-Call-Sentiment-Analyzer/MYCROFT.md`
- `projects/Earnings-Call-Sentiment-Analyzer/README.md`
- `data/raw/earnings-call-sentiment-analyzer/README.md`

## Inputs

| Input | Type | Source | Required |
|---|---|---|---|
| Transcript | UTF-8 TXT or text-based PDF, maximum 10 MB | Approved local file copied into `data/raw/earnings-call-sentiment-analyzer/` | Yes |
| Company name | String, maximum 200 characters | Human-supplied metadata | Yes |
| Ticker | String, 1–20 characters | Human-supplied metadata | Yes |
| Fiscal quarter | `Q1`–`Q4` | Human-supplied metadata | Yes |
| Fiscal year | Integer | Human-supplied metadata | Yes |
| Model version | Model identifier | `MODEL_NAME`; defaults to `ProsusAI/finbert` | Yes |

## Phase Gates

1. **Source and provenance gate — [TO].** The transcript must have a named origin, import date, and explicit real-versus-sample classification. Failure: stop before parsing.
2. **Input conformance gate — [PA].** The file must be readable TXT or a text-based PDF and remain inside the configured upload directory. Failure: reject the input; do not attempt silent OCR.
3. **Parser gate — [PA].** Section and speaker attribution must be surfaced with unknown values preserved. `[TODO: DEFINE]` A human must set the acceptable unknown-speaker rate and labeled-corpus accuracy threshold, with reasoning.
4. **Model gate — [TO].** Record model name, chunk text, positive/neutral/negative probabilities, final score, and processing timestamp. Failure: do not emit an aggregate without its evidence rows.
5. **Evidence adequacy gate — [IJ].** `[TODO: APPROVE]` A named analyst must inspect representative chunks, section boundaries, speaker roles, and the strongest positive and negative passages.
6. **Two-customer output gate — [EI].** The completed sample run is exported as `logs/earnings-call-sentiment-analyzer-20260724-050407-ncs-q3fy2026.json` and `reports/generated/earnings-call-sentiment-analyzer-20260724-050407-ncs-q3fy2026.md`. The report remains pending named human review.

## Workflow

1. Validate transcript metadata and store the approved source through the Spring Boot API.
2. Queue only job identifiers and the constrained shared-volume path through RabbitMQ.
3. Extract text, detect transcript sections and speakers, and split the source into one-to-three-sentence evidence chunks.
4. Score each chunk with the recorded FinBERT model and retain all three class probabilities.
5. Persist transcript metadata, job state, source chunks, model outputs, and aggregates in PostgreSQL.
6. Surface transcript-, section-, management-, analyst-, and speaker-level views without hiding the underlying evidence.
7. Generate the agent log and human report, then stop for analyst review.

## Implementation Map

| Responsibility | Implementation |
|---|---|
| Upload, validation, job creation, read APIs | `projects/Earnings-Call-Sentiment-Analyzer/backend/` |
| Text/PDF extraction | `projects/Earnings-Call-Sentiment-Analyzer/worker/app/transcript_reader.py` |
| Section, speaker, role, and chunk parsing | `projects/Earnings-Call-Sentiment-Analyzer/worker/app/text_processing.py` |
| FinBERT inference | `projects/Earnings-Call-Sentiment-Analyzer/worker/app/model.py` |
| Queue worker and durable processing | `projects/Earnings-Call-Sentiment-Analyzer/worker/app/main.py` |
| Evidence dashboard | `projects/Earnings-Call-Sentiment-Analyzer/frontend/` |
| Full local orchestration | `projects/Earnings-Call-Sentiment-Analyzer/docker-compose.yml` |

## Output Contract

### Agent Log

Path: `logs/earnings-call-sentiment-analyzer-[RUN_ID].json`

Required fields: recipe version, run ID, transcript provenance, source hash, company metadata, model identifier, parser version or commit, chunk count, section counts, speaker-role counts, unknown-attribution count, label counts, score calculation, start/end timestamps, failures, raw source path, verified output path, and report path.

### Human Report

Path: `reports/generated/earnings-call-sentiment-analyzer-[RUN_ID].md`

Reader: research analyst or finance reviewer.

Decision enabled: accept the analysis as adequate for research use, request parser/model corrections, or block downstream use.

Required sections: source and model, analysis scope, overall and cohort tone, prepared-versus-Q&A comparison, management-versus-analyst comparison, guidance and risk-language signals, cited evidence chunks, attribution gaps, limitations, human decision, and unresolved questions.

## Stop Conditions

- Stop if transcript provenance is missing or the file is represented as real issuer evidence without support.
- Stop if a PDF contains no extractable text.
- Stop if an upload path resolves outside the configured upload directory.
- Stop if chunk-level source evidence is not retained with model scores.
- Stop if model/version metadata is missing.
- Stop if a sentiment score is presented as investment advice, truthfulness, valuation, or a forecast.
- Stop before publishing, trading, alerting, or sharing externally without a named human decision.

## Small-Run Command

Parser and path-safety tests:

```bash
cd projects/Earnings-Call-Sentiment-Analyzer/worker
PYTHONPATH=. python3 -m unittest discover -s tests -v
```

Full sample run remains gated:

```bash
cd projects/Earnings-Call-Sentiment-Analyzer
docker compose up -d --build
```

Do not promote this recipe from `DRAFT` until the two remaining TODOs have their required human evidence.

## Provenance

Imported from the user-supplied project at `/Users/adwaitchangan/Study/Mycroft/Earnings_Call_Sentiment_Analyzer/` on 2026-07-24. The original source folder remains untouched.
