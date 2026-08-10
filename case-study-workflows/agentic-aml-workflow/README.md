# Agentic AML Compliance Workflow

A multi-agent AML compliance pipeline for institutional equities, built on large language models. Processes AML-flagged trades through a four-agent autonomous pipeline with a mandatory human compliance officer checkpoint before any settlement action executes.

Built as a reference implementation for developers working on agentic AI in regulated financial workflows. The architecture reflects how autonomous agent systems can be responsibly deployed in compliance-sensitive environments — where auditability, human accountability, and failure-mode handling are not optional features.

---

## The Problem This Solves

Institutional trade desks process thousands of trades daily. A small fraction carry AML flags — sanctions name matches, unusual volume patterns, structuring indicators, jurisdiction risks. Each flagged trade requires a compliance officer to investigate it: pull the counterparty's LEI record, check KYC currency, run a sanctions check, review transaction history, and produce a documented exception report.

That investigation is labor-intensive, data-heavy, and rule-governed. It is exactly the kind of work where autonomous agents generate leverage — handling every data retrieval and synthesis step, so the compliance officer arrives at a structured, evidence-backed report rather than a blank screen.

The hard constraint: no autonomous system can authorize settlement. That decision carries regulatory liability. A compliance officer must review, judge, and sign off. The architecture enforces this structurally, not behaviorally.

---

## How It Works

```
[AML-flagged trade enters pipeline]
            │
            ▼
    ① Triage Agent
    Characterizes the flag, assigns risk level (LOW/MED/HIGH),
    directs the investigation agent on what to check.
            │
            ▼
    ② Investigation Agent
    Reasons over pre-fetched data: LEI record, KYC status,
    sanctions check result, 24-month transaction history.
    Concludes: FALSE POSITIVE or GENUINE CONCERN.
            │
            ▼
    ③ Reasoning Agent
    Produces a numbered audit chain (3–7 steps).
    Every step cites a specific data source.
    Designed to satisfy regulatory audit scrutiny.
            │
            ▼
    ④ Report Agent
    Produces a structured exception report with four
    fixed sections: FLAG SUMMARY · INVESTIGATION FINDINGS ·
    REGULATORY ASSESSMENT · RECOMMENDED ACTION
            │
            ▼
    ⑤ Human Checkpoint  ← MANDATORY. Cannot be bypassed.
    Compliance officer reviews the report, applies qualitative
    judgment, and submits a decision: approve / escalate / block.
    A signed approval token is required for settlement execution.
            │
            ▼
    [Settlement · Escalation · SAR Assessment]
```

Each agent's output is validated before the next agent runs. Any validation failure escalates immediately — the pipeline never passes bad output downstream. The human gate is architecturally enforced: the settlement API requires a signed token that only the human review system can generate. No prompt injection, hallucination, or model error can bypass it.

---

## Key Design Decisions

**Pre-fetch over tool-use for data sources.** The investigation agent does not call external APIs. The orchestrator queries all four data sources before the agent runs and injects the results as structured context. This makes every data check mandatory, deterministic, and orchestrator-logged before any agent sees the data. In a compliance system, whether a sanctions check ran cannot depend on what the model decided to do.

**Architectural gate, not behavioral instruction.** The original instinct is to write a system prompt that says "do not execute settlement without human approval." This is wrong. A model can hallucinate past a behavioral instruction. The settlement API requires a signed approval token as a mandatory parameter — a constraint no instruction can bypass.

**Per-agent validation before pipeline proceeds.** Every agent has a defined output contract. A triage output without a risk level, an investigation output missing a check area, a reasoning chain without citations — these are caught by the validator before the next agent is invoked. Failures escalate; they do not propagate.

**Citation-based hallucination detection.** Every agent claim must be tagged with `[SOURCE: SOURCE_NAME]`. The validator counts citations and escalates below threshold. An agent that cannot cite a source is asserting a claim without evidence.

**Escalation is a workflow, not a failure state.** Trades the pipeline cannot resolve confidently are routed to a senior compliance officer with the full investigation context. Three resolution paths: approve, block, or escalate further to a compliance committee.

**SAR assessment boundary.** This system never files a Suspicious Activity Report. When a trade is blocked, it creates a `SARAssessment` record, writes it to the audit log, and notifies the BSA Officer. Whether to file is a legal judgment that belongs to a human.

---

## Repository Structure

```
agentic-aml-pipeline/
│
├── main.py                     FastAPI entry point and dev implementations
├── config.py                   LLM config, data source config, build_orchestrator()
├── schemas.py                  Trade, AMLFlag, AgentResult — core data contracts
├── orchestrator.py             AMLOrchestrator and dependency interfaces
├── agent_validation.py         Per-agent output validators
├── investigation_prefetch.py   Pre-fetcher and InvestigationContext
├── data_sources.py             Data source interfaces, GLEIF implementation, stubs
├── escalation.py               Escalation sub-workflow and routing
├── sar_assessment.py           SAR assessment scope boundary
├── taxonomy_loader.py          AML taxonomy loader
│
├── aml_taxonomy.json           Six AML flag types with investigation checklists
├── docker-compose.yml          Local development stack
├── Dockerfile                  Container build
├── requirements.txt            Python dependencies
├── .env.example                All environment variables documented
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py             Trade fixtures and mock dependencies
│   └── test_pipeline.py        Test suite (10 tests, no LLM calls required)
│
└── scripts/
    └── init_db.sql             PostgreSQL table creation
```

---

## Quick Start

**Prerequisites:** Docker, Docker Compose, and one of: Anthropic API key, OpenAI API key, or Google Gemini API key.

```bash
# 1. Clone
git clone https://github.com/your-org/agentic-aml-pipeline.git
cd agentic-aml-pipeline

# 2. Configure
cp .env.example .env
# Open .env — set whichever API key you have (see LLM section below)

# 3. Run
docker compose up

# 4. Send a test trade
curl -X POST http://localhost:8000/trades/flagged \
  -H "Content-Type: application/json" \
  -d @tests/sample_trade.json

# 5. Read the docs
open http://localhost:8000/docs
```

On first run, the four agents execute against real LLM calls. The full exception report is printed to console. The trade auto-approves (`DEV_AUTO_APPROVE=true`). You can read exactly what the compliance officer would have received.

---

## LLM Provider Support

The pipeline supports Anthropic, OpenAI, and Google Gemini out of the box. Set whichever key you have in `.env` — the pipeline detects the provider automatically.

```env
# Anthropic Claude (recommended for compliance text quality)
ANTHROPIC_API_KEY=sk-ant-...

# OR OpenAI
OPENAI_API_KEY=sk-...

# OR Google Gemini
GEMINI_API_KEY=AIzaSy-...
```

Default models: `claude-sonnet-4-6` · `gpt-4o` · `gemini-2.0-flash`

Override with `LLM_MODEL=your-model-name` in `.env`.

For Azure OpenAI, Groq, Ollama, or any OpenAI-compatible endpoint:
```env
LLM_PROVIDER=openai_compatible
LLM_BASE_URL=https://your-endpoint/v1
LLM_API_KEY=your-key
LLM_MODEL=your-model-name
```

---

## What Works Out of the Box

| Component | Development mode |
|---|---|
| Four-agent LLM pipeline | Real LLM calls |
| GLEIF LEI verification | Real API (free, no key required) |
| KYC records | Stub — returns fixture data |
| OFAC sanctions check | Stub — returns clean result |
| Transaction history | Stub — returns fixture data |
| Human review gate | Auto-approves, logs full report to console |
| Audit log | Console + in-memory |
| Escalation queue | Logs to console |
| Settlement API | Logs only, no execution |

Stubs are clearly marked with `use_stub=True` in `config.py`. Flip to `False` when your adapter is ready.

---

## Implementing Your Adapters

Three data source adapters need to be built for your institution. Each follows the same pattern — a class that subclasses the interface in `data_sources.py` and implements one `query()` method.

**KYC Records** — connect to your institution's KYC management platform:
```python
class YourKYCAdapter(KYCStore):
    def query(self, lei: str) -> KYCRecord:
        # Call your internal KYC system, map response to KYCRecord
        ...
```

**Sanctions Database** — OFAC SDN list (local XML cache recommended for latency):
```python
class YourSanctionsAdapter(SanctionsDatabase):
    def query_by_lei(self, lei: str, counterparty_name=None) -> SanctionsCheckResult:
        # Query OFAC SDN by LEI — never by name string
        ...
```

**Transaction History** — connect to your trade surveillance system:
```python
class YourTXHistoryAdapter(TransactionHistoryStore):
    def query(self, lei: str, lookback_months: int = 24) -> TransactionHistorySummary:
        # Pull 24-month history, detect BSA typology patterns
        ...
```

See `config.py` — the `ADAPTER PATTERN` section — for a complete skeleton with error handling.

**Human Review Queue** — the most important implementation. Build a UI that shows the exception report and lets the compliance officer submit a decision. Connect it to a durable queue (PostgreSQL or SQS):
```python
class YourReviewQueue(HumanReviewQueue):
    def request_approval(self, trade_id, report) -> ApprovalDecision:
        # Post to your review UI, block until officer submits
        ...
```

Pass your implementations to `build_orchestrator()`:
```python
orchestrator = build_orchestrator(config, deps={
    "review_queue":     YourReviewQueue(),
    "audit_log":        YourPostgresAuditLog(),
    "settlement_api":   YourSettlementAPI(),
    "escalation_queue": YourEscalationQueue(),
})
```

---

## Configuration

Every developer decision point in the code is marked `[DEV]`. Find them all with:

```bash
grep -rn "\[DEV\]" . --include="*.py"
```

**Decisions that require compliance team or legal counsel input:**

| Decision | Where it lives |
|---|---|
| Confidence score thresholds (auto-clear / auto-escalate) | `schemas.py` + `aml_taxonomy.json` |
| KYC review cycle thresholds by risk tier | `data_sources.py` + `aml_taxonomy.json` |
| SAR assessment scope and filing boundary | `sar_assessment.py` + your BSA Officer |
| OFAC list staleness threshold | `config.py SanctionsSourceConfig` |
| Transaction history lookback period | `config.py TXHistorySourceConfig` |
| Escalation routing rules (team names, desk IDs) | `escalation.py DEFAULT_ROUTING_RULES` |

**Decisions owned by engineering:**

| Decision | Where it lives |
|---|---|
| LLM provider and model | `config.py LLMConfig` |
| Queue backend (PostgreSQL / SQS / BullMQ) | `orchestrator.py HumanReviewQueue` |
| Audit log backend | `orchestrator.py AuditLog` |
| Deployment topology | `docker-compose.yml` |

---

## AML Taxonomy

`aml_taxonomy.json` defines the six flag types in scope for US equities under OFAC/BSA/FinCEN:

| Flag type | Description |
|---|---|
| `SANCTIONS_NAME_MATCH` | Counterparty name matches an entity on a sanctions watchlist |
| `SANCTIONS_LEI_MATCH` | Counterparty LEI directly matches a sanctioned entity |
| `UNUSUAL_VOLUME` | Trade value anomalous relative to counterparty's history |
| `STRUCTURING` | Pattern of trades designed to stay below reporting thresholds |
| `LAYERING` | Rapid buy/sell pattern with near-zero net economic position |
| `JURISDICTION_RISK` | Counterparty domiciled in a FATF high-risk jurisdiction |

Each entry contains an investigation checklist, false positive indicators, genuine concern indicators, regulatory citations, and SAR guidance. The file is plain JSON — your compliance team can update it without touching code.

---

## Running Tests

```bash
# Full suite — no LLM calls required
pytest tests/ -v

# Single test
pytest tests/test_pipeline.py::test_malformed_event_raises_validation_error -v
```

The suite covers schema validation, agent output validation, the token gate, data source failure handling, and taxonomy completeness. All 10 tests run without LLM calls or external API access.

---

## Regulatory Scope

This implementation targets US BSA/AML requirements under OFAC/FinCEN for institutional equities.

**This system never files a SAR.** When a trade is blocked, it creates a `SARAssessment` record and notifies the BSA Officer. Whether to file is a legal judgment that belongs entirely to a human. See `sar_assessment.py` for the full scope declaration.

All confidence score thresholds, KYC review cycle values, and sanctions staleness parameters are reference defaults. Your institution's compliance policy and legal counsel define the actual values.

---

## Production Checklist

- [ ] Set `ENVIRONMENT=production` and `DEV_AUTO_APPROVE=false`
- [ ] Implement `HumanReviewQueue` with a real review UI and durable queue
- [ ] Implement `AuditLog` with PostgreSQL append-only storage
- [ ] Implement `SettlementAPI` connected to your settlement system
- [ ] Implement `EscalationQueue` with a durable backend
- [ ] Build KYC, OFAC, and TX history adapters — set `use_stub=False`
- [ ] Compliance team confirms all threshold values
- [ ] BSA Officer defines SAR assessment process and implements `BSONotifier`
- [ ] Update escalation routing rules with real team names and desk IDs
- [ ] Run test suite with real LLM calls against known historical cases
- [ ] Legal counsel reviews the SAR scope declaration in `sar_assessment.py`
- [ ] Change all default passwords in `docker-compose.yml`

---

## Contributing

This is a reference implementation. Contributions that improve the architecture, add adapter implementations for common compliance platforms, or extend the test suite are welcome.

When contributing, keep the `[DEV]` markers in place — they are how developers find what to customize.

---
