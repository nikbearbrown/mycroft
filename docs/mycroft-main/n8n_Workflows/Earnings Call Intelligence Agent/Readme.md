# Earnings Call Intelligence Agent (n8n Workflow)

## Overview

The Earnings Call Intelligence Agent is a modular n8n workflow that transforms raw earnings call transcripts into structured financial intelligence. Instead of summarizing what was said, it extracts **what changed, what was admitted, and what analysts pushed back on** — stored in a queryable PostgreSQL schema that can be compared across companies and quarters.

This agent is part of the Mycroft Framework, an open-source initiative under Humanitarians.AI focused on building modular, transparent, and reproducible AI-powered intelligence agents for research and education.

<img width="2706" height="759" alt="image" src="https://github.com/user-attachments/assets/0d0e2c9f-0a82-4862-939e-5c9b460ab8c9" />


---

## How This Is Different From Just Reading a Transcript

A transcript reader tells you *what happened*. This agent tells you *what changed, what was hidden, and what the market should watch*.

| Capability | Reading a Transcript | This Agent |
|---|---|---|
| Output format | Prose notes | Structured PostgreSQL schema |
| Guidance tracking | Manual note-taking | Auto-classified: strengthened / weakened / unchanged / new / retracted |
| Risk detection | Reader-dependent | Extracted with severity scoring (critical / high / medium / low) |
| Analyst pressure | Lost in reading | Scored 1–10 per topic with response type classification |
| Cross-call comparison | Impossible at scale | Query across hundreds of calls in seconds |
| Auditability | None | Every claim tied to an exact transcript quote |

---

## Key Capabilities

- Parses earnings call transcripts into labeled sections (CEO remarks, CFO remarks, Q&A)
- Extracts management guidance signals with direction classification
- Extracts risk admissions with severity scoring and uncertainty language detection
- Maps analyst Q&A pressure with response type and pressure score per topic
- Generates a structured call summary with overall tone classification
- Stores all signals in PostgreSQL for cross-company and cross-quarter querying
- Returns a structured JSON response to the caller

---

## Workflow Architecture

```
POST /webhook/earnings-call
    └── Validate Input
            └── DB: Insert earnings_call
                    └── Set Call Context
                            └── Groq: Parse Transcript Sections
                                    └── Process Section Response
                                            └── DB: Insert transcript_section
                                                    └── Route by Section Type
                                                            ├── Prepared Remarks
                                                            │       ├── Groq: Extract Guidance Signals
                                                            │       │       └── Process Guidance Response
                                                            │       │               └── DB: Insert guidance_signal
                                                            │       └── Groq: Extract Risk Admissions
                                                            │               └── Process Risk Response
                                                            │                       └── DB: Insert risk_admission
                                                            └── Q&A
                                                                    └── Groq: Map QA Pressure
                                                                            └── Process QA Response
                                                                                    └── DB: Insert qa_pressure
                                                                                            └── DB: Log Agent Run
                                                                                                    └── Fetch All Signals for Summary
                                                                                                            └── Groq: Generate Call Summary
                                                                                                                    └── Process Summary Response
                                                                                                                            └── DB: Insert call_summary
                                                                                                                                    └── DB: Mark Call Complete
                                                                                                                                            └── Webhook Response
```

---

## Input

Send a POST request to your n8n webhook URL:

```json
{
  "company_name": "Microsoft Corporation",
  "ticker": "MSFT",
  "call_date": "2024-04-25",
  "fiscal_quarter": "Q3 2024",
  "transcript_text": "MODERATOR: Welcome to Microsoft Q3 2024 earnings call. CEO SATYA NADELLA: We are raising our full year revenue guidance..."
}
```

---

## Output

```json
{
  "success": true,
  "earnings_call_id": "uuid",
  "company": "Microsoft Corporation",
  "ticker": "MSFT",
  "quarter": "Q3 2024",
  "status": "complete",
  "overall_tone": "bullish",
  "narrative_summary": "Microsoft's Q3 2024 report exceeded analyst expectations, driven by strong growth in cloud computing and gaming...",
  "what_changed": "Azure cloud revenue grew 31% year over year. AI-powered Copilot seats grew 60% quarter over quarter...",
  "schema_valid": true
}
```

---

## Database Schema (7 Tables)

| Table | What It Stores |
|---|---|
| `earnings_calls` | Master record per call — company, ticker, quarter, status |
| `transcript_sections` | Parsed sections — CEO remarks, CFO remarks, Q&A |
| `guidance_signals` | Forward-looking claims with direction classification |
| `risk_admissions` | Risk statements with severity and uncertainty language |
| `qa_pressure_map` | Analyst questions with pressure scores and response types |
| `call_summaries` | Final summary with tone, what changed, what didn't |
| `agent_run_log` | Audit trail — model used, tokens, success status |

---

## Guidance Direction Classifications

Every guidance statement extracted is classified as one of:

| Direction | Meaning |
|---|---|
| `strengthened` | Management raised guidance vs prior period |
| `weakened` | Management lowered guidance vs prior period |
| `unchanged` | Guidance held flat |
| `new` | First time this metric was guided |
| `retracted` | Previously given guidance withdrawn |

---

## Sample Queries

**All calls processed with tone:**
```sql
SELECT company_name, ticker, fiscal_quarter, overall_tone
FROM earnings_calls
JOIN call_summaries ON earnings_calls.id = call_summaries.earnings_call_id;
```

**Weakened guidance signals:**
```sql
SELECT ticker, fiscal_quarter, claim_text, direction
FROM guidance_signals
WHERE direction = 'weakened';
```

**High pressure Q&A topics:**
```sql
SELECT ec.ticker, qa.question_topic, qa.pressure_score, qa.response_type
FROM qa_pressure_map qa
JOIN earnings_calls ec ON ec.id = qa.earnings_call_id
WHERE qa.pressure_score >= 7;
```

**New risks admitted this quarter:**
```sql
SELECT ec.ticker, ra.risk_category, ra.severity, ra.risk_text
FROM risk_admissions ra
JOIN earnings_calls ec ON ec.id = ra.earnings_call_id
WHERE ra.is_new_risk = true;
```

---

## LLM Used

| Component | Model |
|---|---|
| Section parsing | llama-3.3-70b-versatile (Groq) |
| Guidance extraction | llama-3.3-70b-versatile (Groq) |
| Risk extraction | llama-3.3-70b-versatile (Groq) |
| QA pressure mapping | llama-3.3-70b-versatile (Groq) |
| Call summary | llama-3.3-70b-versatile (Groq) |

Groq free tier used throughout. Swap the `model` field in any HTTP node to use Claude, GPT-4o, or any OpenAI-compatible endpoint.

---

## Credentials Required

| Credential | Type | Used For |
|---|---|---|
| Groq API Key | Header Auth (`Authorization: Bearer`) | All 5 LLM nodes |
| PostgreSQL | Database connection | All DB nodes |

---

## Companies Tested

| Company | Ticker | Quarter |
|---|---|---|
| Apple Inc | AAPL | Q4 2024 |
| Microsoft Corporation | MSFT | Q3 2024 |

Any company with a transcript can be processed — paste any earnings call text as `transcript_text`.

---

## Data Accuracy

This agent uses a large language model (Groq / Llama-3.3-70b) to extract and classify financial signals. Understanding its accuracy profile is important before using outputs for any decision-making.

| Signal Type | Accuracy | Notes |
|---|---|---|
| Section parsing | High | CEO / CFO / Q&A boundaries reliably detected |
| Overall tone | High | Bullish / bearish / neutral classification is consistent |
| Narrative summary | High | Faithful to transcript content, well-structured |
| Risk admissions | Medium-High | Captures explicit risk language well; subtle hedging may be missed |
| QA pressure scoring | Medium | Pressure scores are directionally correct but subjective |
| Guidance signals | Medium | Depends heavily on transcript length and specificity |
| Metric values | Medium-Low | Numbers extracted correctly when clearly stated; may miss implied guidance |

**What affects accuracy:**
- Longer, more detailed transcripts produce better extractions than short summaries
- Real earnings call transcripts (10,000+ words) will outperform short synthetic inputs
- The model may miss guidance buried deep in Q&A exchanges
- Metric values (exact revenue figures, margin percentages) are most reliably extracted when explicitly stated by the speaker

**This agent is best used for:**
- Directional signal detection (what changed) rather than precise number extraction
- Comparative analysis across many calls where individual errors average out
- First-pass intelligence that a human analyst then reviews

---

## How This Can Be Used

**Investor Research**
Compare guidance direction across 10+ companies in the same sector. Identify which management teams consistently strengthen vs weaken guidance quarter over quarter.

**Competitive Intelligence**
Track what risks competitors are admitting to — supply chain issues, regulatory pressure, margin compression — before they appear in news coverage.

**Analyst Preparation**
Before an earnings call, query what topics analysts pushed hardest on last quarter and what the pressure scores were. Know which topics are likely to come up again.

**Portfolio Monitoring**
Run transcripts for every company in a portfolio after earnings season. Get a structured summary of tone shifts and guidance changes without reading 20 transcripts manually.

**Academic Research**
Build a dataset of structured earnings call signals across companies and years. Study how guidance language correlates with subsequent stock performance.

**Journalism & Financial Media**
Quickly identify the most significant changes from a call — what management admitted, what analysts challenged — without reading the full transcript.

---

## Project Context

This workflow is part of the **Mycroft Framework**, an open-source initiative under Humanitarians.AI, focused on building modular, transparent, and reproducible AI-powered intelligence agents for research and education.
