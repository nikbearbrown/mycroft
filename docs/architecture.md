# Architecture Design Document
## Recipe-Conductor-Script System
### Agentic Pipeline Framework for Domain Experts

**Version:** 1.0  
**Date:** June 2026  
**Status:** Draft — awaiting human review before governing implementation

---

## 1. Problem Statement

Domain experts — branding students, marketing analysts, researchers — have
real intelligence work to do: monitor competitors, track sentiment, analyze
regulatory filings, surface anomalies. The tools available to them require
either deep technical skill (write the code yourself) or surrender of judgment
(let the automation run and trust the output).

Neither is acceptable. The first excludes the domain expert. The second
produces pipelines that run confidently in the wrong direction because no
one with domain knowledge was in the loop when it mattered.

This system is a human-AI collaborative pipeline framework inserted between
domain expert intent and agentic execution that produces verified, auditable
intelligence output without requiring the domain expert to write code — while
keeping them in the loop at every decision that requires their judgment.

**What it is not:** a no-code automation platform. A no-code platform hides
the execution. This system makes the execution legible and keeps the human
accountable for what it produces.

---

## 2. Architecture Principles

### P1 — AI Does AI Things. Humans Do Human Things.
The system enforces labor separation at every step. AI executes: fetches,
parses, deduplicates, scores, transforms, formats. Humans decide: whether
the data contract was met, whether the output makes domain sense, whether
an anomaly is signal or noise, whether a finding requires action.

A step that requires human judgment is not a bottleneck. It is the point.

**Honors:** Explicit supervisory capacity labels on every human task.  
**Violates:** A conductor flow that proceeds through a gate automatically
because no failure was detected.  
**Failure state:** Pipelines that produce confident, wrong output because
domain judgment was never exercised.

### P2 — Verified Local Data Over Live Fetches
Tools read from verified local data. They do not reach external sources.
Ingest scripts touch external sources and land raw data. GIGO scripts
clean and verify before anything enters the verified layer. This separation
is structural, not advisory.

**Honors:** A tool script that reads only from `data/verified/`.  
**Violates:** A tool script that calls an external API directly.  
**Failure state:** Token waste, rate limit failures, schema drift from
upstream changes, hallucinated interpretation of malformed external data.

### P3 — Dialogue Before Automation
Every pipeline runs in dialogic mode before it earns silent mode. Silent
mode is a trust level granted after documented successful runs, not a
default for users who find gates inconvenient. The dialogue is not overhead —
it is where domain judgment is exercised and recorded.

**Honors:** A conductor flow that stops at each phase gate and waits
for explicit human clearance with a named verification test.  
**Violates:** Appending silent mode to a flow that has never completed
a dialogic run.  
**Failure state:** Pipelines running in production whose phase gates
have never been tested against real failure conditions.

### P4 — Two Customers, Two Output Contracts
Every pipeline that produces output produces two artifacts: a log for
agents (full detail, structured, parseable) and a report for humans
(insight, decision, anomaly — not pipeline output). A log that is handed
to a human has failed its customer. A report that reads like a log has
failed its customer.

**Honors:** A conductor flow that explicitly generates both artifacts
as separate steps.  
**Violates:** Treating the run log as the human deliverable.  
**Failure state:** Domain experts drowning in pipeline detail, missing
the signal the pipeline was built to surface.

### P5 — Provenance Is Non-Negotiable
Every recipe links to its source. Every script documents its inputs,
outputs, and side effects. Every run is logged. Every gate decision
records who cleared it and when. Generated output is evidence of a run,
not source of truth, until a human accepts it.

**Honors:** A report that links to its log entry, which links to the
scripts that produced it, which link to the recipes that specified them.  
**Violates:** A generated file with no traceable origin.  
**Failure state:** An output that cannot be audited, reproduced, or
defended when its conclusions are questioned.

### P6 — Recipes Are the Canonical Specification
The recipe is the authoritative description of what a pipeline does.
Not the script. Not the conductor flow. Not the n8n JSON. If a script
and its recipe disagree, the recipe wins and the script is wrong. Recipes
are written for domain experts first, agents second, developers third.

**Honors:** A recipe written so a branding student can read it and
understand what the pipeline does and where their judgment is required.  
**Violates:** A recipe that describes implementation details rather
than business logic.  
**Failure state:** Domain experts who cannot read their own pipelines,
cannot catch errors, and cannot specify new ones.

---

## 3. System Overview

```
External Sources
      │
      ▼
┌─────────────┐
│   INGEST    │  scripts/ingest/
│   SCRIPTS   │  Touch external sources.
│             │  Land raw data to data/raw/
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    GIGO     │  scripts/gigo/
│   SCRIPTS   │  Clean, validate, deduplicate.
│             │  Promote verified data to data/verified/
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────────────────────────────┐
│    TOOL     │     │           CONDUCTOR              │
│   SCRIPTS   │◄────│   Cowork / Codex in dialogic     │
│             │     │   mode. Sequences recipes.       │
│ scripts/    │     │   Enforces phase gates.          │
│ tools/      │     │   Surfaces human tasks.          │
└──────┬──────┘     │   Generates both output types.   │
       │            └──────────────┬──────────────────┘
       │                           │
       ▼                           ▼
┌─────────────┐           ┌────────────────┐
│    LOGS     │           │    REPORTS     │
│             │           │                │
│ Full detail │           │ Human insight  │
│ Agent-      │           │ Decision-ready │
│ readable    │           │ Executive      │
│ logs/       │           │ summary        │
└─────────────┘           │ reports/       │
                          └────────────────┘
```

The human is present at two structural points:

1. **At phase gates** inside the conductor flow — verifying outputs,
   clearing steps, exercising domain judgment before the pipeline proceeds.

2. **At the report** — reading the human-facing output and deciding
   what it means and what action it requires.

The conductor is not autonomous infrastructure. It is a dialogue partner
that sequences work, surfaces decisions, and refuses to proceed past gates
without human clearance.

---

## 4. Repository Structure

```
repo-root/
│
├── CLAUDE.md                    # Conductor configuration
│                                # Gate behavior, labor separation rules,
│                                # silent mode policy, conductor identity
│
├── AGENTS.md                    # Cross-agent operating rules
│                                # Grounding order, forbidden actions,
│                                # required reads before any task
│
├── DATA_CONTRACT.md             # What verified data looks like
│                                # GIGO rules, schema definitions,
│                                # provenance requirements
│
├── README.md                    # Human-facing orientation
│
├── recipes/                     # Canonical pipeline specifications
│   ├── README.md                # Recipe index + two-customer principle
│   ├── fetch-rss.md
│   ├── fetch-reddit.md
│   ├── fetch-regulatory.md
│   ├── score-sentiment.md
│   ├── deduplicate.md
│   ├── build-knowledge-graph.md
│   ├── competitor-analysis.md
│   ├── detect-anomalies.md
│   └── intelligence-pipeline.md # Conductor recipe — sequences the others
│
├── scripts/                     # Python implementations + callable tools
│   ├── README.md                # Script index + tool/script equivalence note
│   │
│   ├── ingest/                  # Touch external sources
│   │   ├── README.md            # Ingest layer rules
│   │   ├── fetch_rss.py
│   │   ├── fetch_reddit.py
│   │   └── fetch_regulatory.py
│   │
│   ├── gigo/                    # Clean and verify — GIGO layer
│   │   ├── README.md            # GIGO layer rules
│   │   ├── validate_schema.py
│   │   ├── deduplicate.py
│   │   └── normalize_fields.py
│   │
│   └── tools/                   # Read verified data, produce output
│       ├── README.md            # Tool layer rules
│       ├── score_sentiment.py
│       ├── build_knowledge_graph.py
│       ├── competitor_analysis.py
│       └── detect_anomalies.py
│
├── data/                        # Local data — the only thing tools read
│   ├── README.md
│   ├── raw/                     # Ingest output — not GIGO verified
│   │   └── README.md            # Raw data is not safe for tools
│   └── verified/                # GIGO-cleared — safe for tools
│       └── README.md            # Verified data contract
│
├── conductor/                   # Conductor flows
│   ├── README.md                # Conductor identity + dialogic mode policy
│   ├── intelligence-pipeline.md
│   ├── content-agent.md
│   ├── survey-analysis.md
│   └── verified/                # Flows cleared for silent mode
│       └── README.md            # Silent mode graduation requirements
│
├── reports/                     # Human-readable output
│   ├── README.md                # Two-customer principle
│   ├── templates/               # One template per pipeline
│   │   ├── intelligence-summary.md
│   │   ├── competitor-analysis.md
│   │   └── survey-analysis.md
│   └── generated/               # Actual report outputs
│       └── YYYY-MM-DD-<name>.md
│
├── logs/                        # Agent-readable audit trail
│   ├── RUN_LOG.md               # Every meaningful run
│   └── gate-decisions/          # Human gate clearances
│       └── YYYY-MM-DD-<flow>.md
│
└── docs/                        # Human-facing system documentation
    ├── README.md                # Documentation index
    ├── architecture.md          # This document
    ├── labor-separation.md      # AI/human division of work
    ├── silent-mode-policy.md    # How flows graduate to silent mode
    ├── data-contract.md         # Ingest/GIGO/verified layer rules
    ├── recipe-standard.md       # How to write a recipe
    ├── script-standard.md       # How to write a script
    ├── conductor-standard.md    # How to write a conductor flow
    ├── report-standard.md       # How to write a report template
    └── contributing.md          # How students add to the system
```

---

## 5. Component Specifications

### 5.1 Recipes

A recipe is the canonical human-readable specification of a pipeline or
pipeline step. It is written for domain experts first. It is the source
of truth when a script and a recipe disagree.

**Required sections:**

| Section | Purpose |
|---|---|
| Purpose | What business question this answers — no technical detail |
| Inputs | Table of inputs with types, sources, and required/optional |
| Phase Gates | Numbered gates with verification tests and supervisory capacity labels |
| Steps | Numbered steps with labor assignment, script called, I/O, and destination |
| Output Contract | Agent output (log) and human output (report) separately specified |
| Stop Conditions | Conditions that halt the conductor and require human intervention |
| Provenance | Link to original source (n8n JSON, prior recipe, external spec) |

**Supervisory capacity labels** appear on every human step:

| Label | Capacity | Definition |
|---|---|---|
| [PA] | Plausibility Auditing | Evaluating output for domain-grounded implausibility before verification |
| [PF] | Problem Formulation | Deciding what the pipeline should do before it runs |
| [TO] | Tool Orchestration | Deciding which script, in what order, with what trust level |
| [IJ] | Interpretive Judgment | Supplying meaning and accountability to AI output |
| [EI] | Executive Integration | Holding multiple pipeline outputs toward a unified conclusion |

**What a recipe is not:**
- A script or code
- An n8n workflow JSON
- A log or run record
- A report

### 5.2 Scripts

A script is the Python implementation of one recipe step. Every script
is also a callable tool — the conductor can invoke it directly, a student
can run it manually, and another script can import its primary function.
Same file, three uses.

**Script layers and their contracts:**

#### Ingest Layer (`scripts/ingest/`)
- **May:** make network requests, call external APIs, read external RSS feeds
- **Must:** write output only to `data/raw/`
- **Must not:** write to `data/verified/` — that is GIGO's job
- **Must not:** be called directly by tool scripts

#### GIGO Layer (`scripts/gigo/`)
- **May:** read from `data/raw/`
- **Must:** validate against the schema defined in `DATA_CONTRACT.md`
- **Must:** write clean output only to `data/verified/`
- **Must not:** make network requests
- **Must not:** be skipped — nothing enters `data/verified/` without passing GIGO

#### Tool Layer (`scripts/tools/`)
- **May:** read from `data/verified/` only
- **Must:** produce output to `logs/` or `reports/generated/`
- **Must not:** read from `data/raw/`
- **Must not:** make network requests
- **Must not:** write back to `data/verified/` without a GIGO pass

**Required script structure:**

```python
"""
Purpose: One sentence describing what this script does.
Input: Expected data format and source path.
Output: Produced data format and destination path.
Side effects: Any network calls, file writes, external service calls.
Idempotent: Yes/No — reason.
Recipe: recipes/<recipe-name>.md
"""

from typing import ...

def primary_function(input: InputType) -> OutputType:
    """
    Mirrors module docstring. One sentence per field.
    """
    ...

if __name__ == "__main__":
    # Sample input for manual verification
    # Prints output to stdout
    # No side effects beyond what the function itself performs
    ...
```

**What a script must never contain:**
- Hardcoded credentials (use environment variables, document the variable names)
- Direct reads from external sources in gigo or tool scripts
- Logic that belongs in a recipe (business rules, gate decisions)
- Output formatting for humans (that belongs in report templates)

### 5.3 Conductor

The conductor is Cowork or Codex running in dialogic mode, configured by
`CLAUDE.md` for a specific project. It is not a script. It is not
autonomous infrastructure. It is a dialogue partner.

**What the conductor does:**
- Reads the recipe for the requested pipeline
- Sequences steps in dependency order
- Invokes scripts as tools at AI steps
- Surfaces human tasks with named supervisory capacities and specific
  verification tests
- Stops at phase gates and waits for explicit human clearance
- Generates both log output and human report output
- Refuses to proceed when a stop condition is met

**What the conductor does not do:**
- Make domain judgments
- Clear its own phase gates
- Decide that a finding is significant or insignificant
- Proceed past a hard gate because no error was detected

**Conductor flow document structure:**

| Section | Content |
|---|---|
| Mode | Dialogic or Silent (silent only if in `conductor/verified/`) |
| Entry Point | How the flow is triggered |
| Flow Steps | Dependency-ordered steps with AI/human labor, handoff conditions |
| Phase Gates | Which steps are hard gates requiring explicit human clearance |
| Silent Mode Requirements | What must be true before this flow can be submitted for verification |

**Handoff conditions** are specific and testable. Not "looks good." Examples:

- "Every item in the deduplicated output has a URL, a source, and a
  timestamp. Zero null fields in these columns."
- "Sentiment scores fall between -1.0 and 1.0. No item has a null score.
  The human has confirmed that the top 3 flagged items are plausibly
  negative given domain knowledge."
- "The knowledge graph has no orphan nodes. Every entity maps to at
  least one recipe input source."

### 5.4 Data Layers

Three layers with strict boundaries:

```
External Sources
      │  (ingest scripts only)
      ▼
data/raw/
      │  (gigo scripts only)
      ▼
data/verified/
      │  (tool scripts only)
      ▼
logs/ and reports/generated/
```

**`data/raw/`**
- Written by ingest scripts only
- Not safe for tool scripts to read
- Schema may be malformed, incomplete, or changed from upstream
- Treated as untrusted until GIGO clears it

**`data/verified/`**
- Written by GIGO scripts only after validation passes
- Schema matches `DATA_CONTRACT.md`
- Safe for tool scripts to read
- The only data source tool scripts are permitted to use

**`DATA_CONTRACT.md`** defines:
- Schema for each data type the system handles
- Required fields and types
- Validation rules GIGO enforces
- What "verified" means for each data source
- What to do when validation fails (log, flag, halt — never silently pass)

### 5.5 Logs

Logs are for agents and audit purposes. They contain full detail.

**`logs/RUN_LOG.md`** records every meaningful run:
- Date and time
- Conductor flow name
- Trigger (manual, scheduled, external)
- Steps completed
- Steps halted and reason
- Gate decisions (who cleared, what was verified)
- Scripts invoked with input/output summary
- Errors encountered
- Artifacts produced with paths
- Unresolved issues

**`logs/gate-decisions/`** records human gate clearances:
- Date and time
- Flow name and step number
- Human who cleared the gate
- Verification test performed
- Result of verification
- Any caveats or provisional clearances

Logs are evidence of what happened. They are not reports. They are not
source of truth for findings. They are the audit trail that makes findings
defensible.

### 5.6 Reports

Reports are for humans. They surface insight and enable decisions. They
do not reproduce pipeline output.

**`reports/templates/`** contains one template per pipeline. Each template
defines the structure of the human-facing output for that pipeline type.

**Required report sections:**

| Section | Content |
|---|---|
| Summary | Three sentences maximum. What happened. What was found. What requires attention. |
| Key Findings | Bulleted list. One sentence per finding. Insight only — no pipeline detail. |
| Decisions Required | Table: Decision \| Options \| Deadline \| Owner |
| Anomalies and Flags | Anything the conductor flagged for human review |
| Full Data | Link to the corresponding log entry |

**What a report must never contain:**
- Raw pipeline output (sentiment scores, deduplicated counts, schema details)
- Technical implementation detail
- Uninterpreted data that requires domain knowledge to read

**What a report must always contain:**
- A finding a domain expert can act on
- A link to the log entry that produced it
- The date and pipeline that generated it

---

## 6. The Two-Customer Principle

Every pipeline that produces output produces two artifacts. This is not
optional and is not a formatting preference. It is an architecture principle.

| Artifact | Customer | Location | Optimized for |
|---|---|---|---|
| Run log | Agents, auditors, developers | `logs/` | Completeness, parseability, traceability |
| Report | Domain experts, decision-makers | `reports/generated/` | Insight, clarity, action |

A single artifact cannot serve both customers. A log handed to a domain
expert produces confusion. A report handed to an agent produces incomplete
context. The conductor generates both as explicit separate steps. The recipe
specifies both in its output contract.

---

## 7. Silent Mode Policy

Silent mode means the conductor proceeds through all steps without
stopping at phase gates for human confirmation. It is a trust level,
not a convenience setting.

### How a flow earns silent mode

1. The flow has completed a minimum of three successful dialogic runs
   with no gate failures
2. All gate decisions from those runs are logged in `logs/gate-decisions/`
3. The GIGO scripts have been verified against a schema change in the
   upstream source (at least one deliberate validation failure test)
4. A human with domain knowledge has reviewed the report output from
   at least two runs and confirmed findings are plausible
5. The flow owner has submitted the flow for `conductor/verified/` status
   with a written sign-off referencing the run log entries

### What silent mode does not change

- The run log is still written in full
- Gate decision records are still written (as auto-cleared, with the
  flow's verified status as authority)
- Stop conditions still halt the flow — silent mode suppresses
  interactive gates, not safety stops
- The human report is still generated — silent mode is not headless mode

### Revoking silent mode

Silent mode is revoked when:
- The upstream data source changes schema
- A new ingest source is added to the flow
- A GIGO script is modified
- Two consecutive runs produce reports that a domain reviewer flags
  as implausible
- The flow owner requests reversion to dialogic mode

Revocation is recorded in `logs/gate-decisions/` with reason.

---

## 8. Contributing — How Students Add to the System

The system grows through student contributions. A student's contribution
is a recipe plus a script (or set of scripts) that implements it. A recipe
without a script is a specification waiting for implementation. A script
without a recipe is an implementation without a specification. Both are
incomplete contributions.

### Contribution types

| Contribution | What it is | Minimum deliverable |
|---|---|---|
| New data source | A new ingest + GIGO script pair | Script pair + recipe entry for the fetch step |
| New analysis | A new tool script | Script + recipe for the analysis step |
| New pipeline | A new conductor flow | All component recipes + conductor flow document |
| Recipe improvement | Clarifying an existing recipe | Updated recipe with change rationale |
| Bug fix | Correcting a script | Updated script + updated recipe if behavior changed |

### Review checklist before a contribution is accepted

- Recipe written for domain expert audience — passes the "can a branding
  student read this?" test
- Script has complete module docstring with all required fields
- Script reads only from the correct layer (`raw/`, `verified/`, or external
  for ingest only)
- No hardcoded credentials
- `if __name__ == "__main__"` block present and runnable
- Recipe links to script; script links to recipe
- If a new pipeline: conductor flow document exists
- If a new pipeline: report template exists
- Run log entry exists for at least one manual test run
- No files in `data/madison-main/n8n-workflows/originals/` were modified

---

## 9. N8n Migration

The original n8n workflows are preserved as provenance artifacts at:

```
data/madison-main/n8n-workflows/originals/
```

These files are never edited. They are the evidence of what the original
workflow did. When a recipe or script disagrees with the original JSON,
the recipe is the authoritative specification going forward — but the
JSON remains as the historical record.

### Migration mapping

| n8n node type | Migrates to |
|---|---|
| HTTP Request (external fetch) | `scripts/ingest/` |
| XML / RSS parse | Part of ingest script |
| Code node (clean/validate) | `scripts/gigo/` |
| Code node (analyze/transform) | `scripts/tools/` |
| Google Sheets read (dedup) | `scripts/gigo/` |
| Google Sheets write | `scripts/tools/` |
| OpenAI node | `scripts/tools/` |
| Merge / filter / branch | Recipe logic — conductor flow structure |
| Webhook trigger | Conductor entry point |
| Respond to Webhook | Conductor output step |

### What migration produces per workflow

For each n8n workflow, migration produces:

1. `recipes/<workflow-name>.md` — the canonical specification
2. `scripts/ingest/<name>.py` — one or more ingest scripts
3. `scripts/gigo/<name>.py` — one or more GIGO scripts
4. `scripts/tools/<name>.py` — one or more tool scripts
5. `conductor/<workflow-name>.md` — the conductor flow
6. `reports/templates/<workflow-name>.md` — the report template

Migration is complete when a domain expert can run the conductor flow
in dialogic mode, clear each gate with a real verification test, and
receive a human report that answers the business question the original
n8n workflow was built to answer.

---

## 10. Open Questions

| Question | Stakes | Status | Owner |
|---|---|---|---|
| Google Sheets auth for GIGO scripts | Several workflows write/read Sheets as dedup store — need credential strategy that works for students | Open | — |
| Scheduling / trigger mechanism | How are ingest scripts triggered on a schedule without n8n? Cron? GitHub Actions? Cowork scheduled run? | Open | — |
| Multi-student shared `data/verified/` | If multiple students run the same pipeline, do they share verified data or maintain separate copies? | Open | — |
| Report delivery | Reports go to `reports/generated/` — how do domain experts receive them? Email? Slack? Manual check? | Open | — |
| Silent mode enforcement | What prevents a student from running a conductor flow in silent mode before it has earned verified status? Policy or technical control? | Open | — |

---

## 11. Glossary

| Term | Definition |
|---|---|
| Recipe | A human-readable markdown specification of a pipeline step or full pipeline. The canonical source of truth. Written for domain experts. |
| Script | A Python implementation of a recipe step. Also callable as a tool by the conductor. |
| Tool | A script invoked by the conductor. Same file — the word "tool" emphasizes its callable, agent-invocable nature. |
| Conductor | Cowork or Codex running in dialogic mode, configured by CLAUDE.md, sequencing recipes and enforcing phase gates. |
| Dialogic mode | The default conductor mode. Every phase gate requires explicit human clearance before the pipeline proceeds. |
| Silent mode | A trust level earned after documented successful dialogic runs. The conductor proceeds through gates automatically. Not a convenience setting. |
| Ingest script | A script that touches external sources and lands raw data to `data/raw/`. |
| GIGO script | A script that validates, cleans, and promotes data from `data/raw/` to `data/verified/`. GIGO = Garbage In, Garbage Out (prevention layer). |
| Tool script | A script that reads only from `data/verified/` and produces output to `logs/` or `reports/generated/`. |
| Phase gate | A hard stop in a conductor flow that requires explicit human clearance with a named, specific verification test before the flow proceeds. |
| Handoff condition | A specific, testable condition that must be true about a step's output before the next step begins. Not "looks good." |
| Supervisory capacity | The type of human judgment required at a phase gate: Plausibility Auditing, Problem Formulation, Tool Orchestration, Interpretive Judgment, or Executive Integration. |
| Two-customer principle | Every pipeline produces two output artifacts: a log for agents (full detail) and a report for humans (insight and decision). |
| Provenance | The traceable chain from a report finding back through its log, scripts, recipe, and original source data. |

---

*This document governs implementation when the Open Questions section has
owners and deadlines assigned and this sentence has been removed by a
human reviewer.*
