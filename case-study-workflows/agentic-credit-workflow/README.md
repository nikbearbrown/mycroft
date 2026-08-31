# Agentic Commercial Credit Memo Pipeline

A multi-agent pipeline for commercial credit underwriting, modeled on JPMorgan Chase's
documented agentic AI deployment. Three specialized agents each solve a distinct data
problem a credit analyst faces before they can begin thinking. A fourth agent synthesizes
the outputs into a structured memo draft. The pipeline then routes the memo to the correct
approval tier based on loan size and risk — Senior Credit Officer, Credit Committee, or
Executive Credit Committee — where a human makes the lending decision.

Built as a reference implementation for credit technology developers. Every customization
point is marked `[DEV]` so you can navigate directly from the README architecture to the
specific line in code where your institution's values need to go.

---

## The Problem This Solves

A commercial credit analyst preparing a credit memo does five things:

1. Verifies who the borrower actually is — KYC status, ownership structure, relationship history
2. Checks the public record for risk signals — litigation, adverse media, regulatory actions
3. Runs the required financial ratios from the borrower's statements
4. Synthesizes all of that against the bank's credit policy and writes the memo
5. Makes the lending judgment

Steps 1–4 are data-intensive, rule-governed, and do not require human judgment — they require accuracy and completeness. Step 5 requires human judgment and cannot be delegated.

Before agentic AI, the analyst did all five. A complex commercial credit application takes three to five days of analyst time before the first line of actual judgment is written — because steps 1–4 consume most of it. JPMorgan's deployment separates these: agents handle steps 1–4, delivering a fully assembled and cited draft. The analyst handles step 5.

**The hard constraint:** no autonomous system can approve a loan. That decision carries credit risk, regulatory liability, and capital accountability. The architecture enforces this structurally — the pipeline produces a routed memo, not a credit decision.

---

## Architecture

```
[Commercial loan application received]
              │
              ▼
   ┌─────────────────────────────┐
   │  Orchestrator               │
   │  Pre-fetches all data first │  ← KYC, OSINT, and financial statements
   │  before any agent runs.     │    are assembled into CreditContext here.
   │  Agents never call external │    Agents reason over context — they never
   │  systems themselves.        │    call data sources directly.
   └────────────┬────────────────┘
                │
       ┌────────┴────────┐
       ▼                 ▼
① KYC/Data Agent    ② OSINT Agent        ← Run in parallel. Independent
  Reviews entity       Screens adverse       data domains, no dependency
  identity, ownership, media, litigation,    between them.
  KYC recency, EDD     regulatory actions.
  requirements.        Classifies severity
  Output:              by bank taxonomy.
  CLEAR/FLAG/BLOCK      Output: NONE/LOW/MEDIUM/HIGH
       │                 │
       └────────┬────────┘
                │  (both must complete before proceeding)
                ▼
       ③ Quantitative Agent
         Ingests financial statements.
         Calculates: Leverage, Interest Coverage,
         DSCR, Current Ratio, Free Cash Flow,
         Revenue growth, EBITDA margin.
         Each calculation cites the source line item.
         Compares results against credit_policy.json
         thresholds for this specific industry.
         Output: LOW/MEDIUM/HIGH/FAIL per ratio
                │
                ▼
       ④ Reasoning/Report Agent
         Synthesizes KYC + OSINT + ratio analysis
         against credit policy. Drafts the memo:
           Executive Summary · Borrower Overview ·
           Financial Analysis · Risk Assessment ·
           Collateral Analysis · Covenant Package
         Produces: agent recommendation + risk tier
                │
                ▼
       approval_routing.py
         Routes memo to the correct approval tier
         based on loan size and agent risk tier:
           → Senior Credit Officer   (≤ $25M, LOW/MEDIUM)
           → Credit Committee        ($25M–$150M)
           → Executive Credit Committee  (HIGH/WATCH or > $150M)
                │
                ▼
       ⑤ Human Review  ← MANDATORY. Cannot be bypassed.
         Analyst or committee receives the routed draft.
         Verifies calculations. Applies qualitative judgment.
         Makes the credit decision.
         No decision record is written without sign-off.
```

**Why parallel for KYC and OSINT — and why does the reference implementation run them sequentially?** They draw from completely independent data domains — internal KYC records vs. external public records. Neither output informs the other, so parallel execution is the correct production design. The reference implementation runs them sequentially so a first-time reader can follow the agent calls one at a time without needing to understand Python concurrency. The `[DEV]` comment in `orchestrator.py`'s `run()` method shows exactly where to add `ThreadPoolExecutor` or `asyncio.gather()` when you are ready to parallelize.

**Why does the Quantitative Agent run after them?** It does not depend on their content, but it should only run after the correct entity has been confirmed. A ratio analysis against the wrong borrower's financials would be worse than no analysis.

**What happens on a blocking signal?** A KYC BLOCK, HIGH severity OSINT finding, or FAIL financial risk assessment halts the pipeline immediately. The Reasoning/Report Agent is not invoked. The assembled context is passed directly to a Senior Credit Officer. The pipeline does not attempt to synthesize past a blocking signal.

---

## Why Each File Exists

| File | Why it exists for this specific problem |
|---|---|
| `schemas.py` | Defines `LoanApplication`, `CreditContext`, `CreditMemo` — the data contracts specific to commercial credit underwriting |
| `data_sources.py` | Three separate interfaces for the three distinct data problems: KYC, OSINT, financial statements. Each is an independent stub you replace with a real adapter |
| `credit_policy.json` | Credit policy thresholds by industry and loan type. The Quantitative Agent reads thresholds from here — not from hardcoded prompt strings. Your risk team edits this file, not the code |
| `policy_loader.py` | Typed accessor for `credit_policy.json`. Agents call `get_policy_summary_for_agent(industry)` to get thresholds injected into their prompts at runtime |
| `approval_routing.py` | Routes completed memos to the correct human approval tier based on loan amount and risk. This is unique to commercial banking — AML compliance does not have approval tiers |
| `orchestrator.py` | Coordinates the agent sequence, parallel execution, blocking logic, and memo assembly. All agent prompts live here as named constants |
| `main.py` | FastAPI entry point. Dev stubs wired up on startup, real adapters swapped in via `[DEV]` markers |

---

## Finding the Customization Points

Every decision your institution needs to make is marked `[DEV]` in the relevant file.
Run this to find them all:

```bash
grep -rn "\[DEV\]" . --include="*.py" --include="*.json"
```

**Key `[DEV]` decisions by owner:**

| Decision | File | Owner |
|---|---|---|
| Ratio thresholds by industry | `credit_policy.json` | Credit Risk Team |
| Approval tier dollar limits | `credit_policy.json` | Credit Policy / Risk Committee |
| KYC review cycle lengths per risk tier | `credit_policy.json` | Compliance Team |
| OSINT severity blocking threshold | `credit_policy.json` | Compliance Team |
| Covenant headroom percentages | `credit_policy.json` | Credit Structuring Team |
| KYC adapter (replace StubKYCRepository) | `data_sources.py` + `main.py` | Engineering |
| OSINT adapter (replace StubOSINTProvider) | `data_sources.py` + `main.py` | Engineering |
| Financial data adapter (replace StubFinancialDataStore) | `data_sources.py` + `main.py` | Engineering |
| Approval queue submission (replace DevApprovalQueue) | `main.py` + `approval_routing.py` | Engineering |
| Audit log persistence (replace DevAuditLog) | `main.py` | Engineering |
| LLM provider (Anthropic → OpenAI / Gemini) | `orchestrator.py` `_call_llm()` | Engineering |
| Citation minimum per agent | `orchestrator.py` `MIN_CITATIONS_PER_AGENT` | Engineering / Credit Risk |
| Parallel agent execution (KYC + OSINT) | `orchestrator.py` `run()` | Engineering |
| Entity identifier (EIN → LEI for institutional clients) | `schemas.py` + `data_sources.py` | Engineering |

---

## Quick Start

**Prerequisites:** An Anthropic API key.

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Set ANTHROPIC_API_KEY=sk-ant-... in .env

# 3. Run
uvicorn main:app --reload

# 4. Submit a test application
curl -X POST http://localhost:8000/applications/submit \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_legal_name": "Apex Industrial Supply LLC",
    "applicant_ein": "12-3456789",
    "applicant_industry": "INDUSTRIAL_MANUFACTURING",
    "loan_type": "REVOLVING_CREDIT_FACILITY",
    "requested_amount": "45000000",
    "proposed_collateral_description": "Accounts receivable and inventory, first lien",
    "relationship_manager_id": "RM-NYC-042"
  }'

# 5. Browse the auto-generated API docs
open http://localhost:8000/docs
```

All four agents will fire against real LLM calls. The full memo draft and routing
decision are printed to console. In dev mode, the application is auto-routed without
blocking for a real analyst decision.

---

## Try Different Scenarios

> **Important:** the stubs make each outcome highly likely — they don't guarantee it.
> Agent outputs are LLM judgments on strong fixture evidence. An unexpected result
> is a live example of the agent-consistency risk Section 6.1 of the case study
> describes, not a broken scenario. Use the exact EIN/industry pairings below —
> `applicant_legal_name` and `applicant_industry` are not cross-validated against the
> EIN in stub mode, so a mismatched pair won't error but will produce an
> internally inconsistent memo.

| EIN | Company | Industry | Expected outcome |
|---|---|---|---|
| `12-3456789` | Apex Industrial Supply LLC | `INDUSTRIAL_MANUFACTURING` | Clean pass — all agents clear, memo drafted, routes to Credit Committee |
| `45-6789012` | Meridian Fabrication Group LLC | `INDUSTRIAL_MANUFACTURING` | KYC BLOCK — pipeline halts after KYC agent |
| `78-9012345` | Cascade Retail Holdings Inc | `RETAIL` | HIGH OSINT — pipeline halts after OSINT agent |
| `23-4567890` | Titan Steel Works Corp | `ENERGY` | FAIL ratio — pipeline halts after Quantitative agent |

**KYC block scenario:**
```bash
curl -X POST http://localhost:8000/applications/submit \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_legal_name": "Meridian Fabrication Group LLC",
    "applicant_ein": "45-6789012",
    "applicant_industry": "INDUSTRIAL_MANUFACTURING",
    "loan_type": "TERM_LOAN_A",
    "requested_amount": "32000000",
    "proposed_collateral_description": "Manufacturing equipment, first lien",
    "relationship_manager_id": "RM-CHI-017"
  }'
```

**HIGH OSINT block scenario:**
```bash
curl -X POST http://localhost:8000/applications/submit \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_legal_name": "Cascade Retail Holdings Inc",
    "applicant_ein": "78-9012345",
    "applicant_industry": "RETAIL",
    "loan_type": "REVOLVING_CREDIT_FACILITY",
    "requested_amount": "28000000",
    "proposed_collateral_description": "Inventory and accounts receivable, first lien",
    "relationship_manager_id": "RM-SEA-009"
  }'
```

**FAIL ratio scenario:**
```bash
curl -X POST http://localhost:8000/applications/submit \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_legal_name": "Titan Steel Works Corp",
    "applicant_ein": "23-4567890",
    "applicant_industry": "ENERGY",
    "loan_type": "TERM_LOAN_A",
    "requested_amount": "35000000",
    "proposed_collateral_description": "Industrial plant and equipment, first lien",
    "relationship_manager_id": "RM-HOU-031"
  }'
```

---

## What Works Out of the Box

| Component | Dev mode |
|---|---|
| Four-agent LLM pipeline | Real LLM calls (Anthropic Claude) |
| KYC records | 4 scenarios keyed by EIN — clean pass, KYC block, clean (for OSINT/ratio scenarios) |
| OSINT / adverse media | 4 scenarios keyed by EIN — LOW civil litigation, HIGH enforcement action, clean |
| Financial statements | 4 scenarios keyed by EIN — healthy pass, all-four-ratios-fail (ENERGY), healthy |
| Approval routing | Real logic from `credit_policy.json` — routes to correct tier |
| Approval queue submission | Dev stub — logs routing decision + memo to console |
| Audit log | Dev stub — in-memory + console |

---

## Adding a New Industry

1. Add the industry code to `IndustryCode` in `schemas.py`
2. Add the ratio thresholds to `credit_policy.json` under `ratio_thresholds`
   — key must exactly match the new `IndustryCode` string
3. Confirm the thresholds with your credit risk team before production use

---

## Production Checklist

- [ ] Replace `StubKYCRepository` with your KYC management platform adapter
- [ ] Replace `StubOSINTProvider` with Refinitiv World-Check / LexisNexis adapter
- [ ] Replace `StubFinancialDataStore` with your financial data extraction pipeline
- [ ] Replace `DevApprovalQueue` with your loan origination system integration
- [ ] Replace `DevAuditLog` with PostgreSQL append-only storage
- [ ] Credit risk team confirms all thresholds in `credit_policy.json`
- [ ] Legal reviews the credit decision boundary (no agent-originated decisions)

---

## What This Is and Is Not

**This is:** a reference implementation demonstrating how the agentic assembly pattern
applies to commercial credit underwriting. The agent design, policy-driven thresholds,
sequential-by-default KYC/OSINT execution (parallel in production — see orchestrator.py),
blocking logic, and approval routing tier structure are all illustrative of the
architecture JPMorgan's deployment embodies. Four scenarios are runnable end to end
without reading any Python — each exercises a different pipeline path (clean pass,
KYC block, OSINT block, ratio fail). There is no automated test suite in this
repository; both facts are stated together so neither implies more completeness
than actually exists.

**Known extension points not yet implemented:** quick ratio (requires `inventory` field
in `FinancialStatements`) and gross margin (requires `cost_of_goods_sold` or `gross_profit`
field). Both are marked `[DEV]` in `schemas.py` and `credit_policy.json` with instructions
for how to add them following the existing pattern.

**This is not:** JPMorgan's actual system. Data sources are stubs. Policy thresholds
are reference defaults. A production deployment requires real adapters and compliance
team sign-off on every value in `credit_policy.json`.
