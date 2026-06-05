# Contradiction Detection Agent
### Mycroft Framework · Intelligence Layer
> **Layer 3 of 3 in the Mycroft Intelligence Pipeline**
> Earnings Call Agent → Tech Stack Agent → Contradiction Agent

---

## What This Agent Does

The Contradiction Detection Agent is the third agent in the Mycroft intelligence pipeline. It does not collect data — it reads what the other two agents already stored, compares their signals, and surfaces conflicts that a human analyst might miss.

In plain terms: if Microsoft's engineers are building at 3x their normal pace on GitHub, but management never mentioned this on the earnings call — that gap is a contradiction. This agent finds it, flags it as HIGH severity, and routes it to a human reviewer. It never makes investment decisions. It surfaces conflicts.

<img width="2464" height="813" alt="image" src="https://github.com/user-attachments/assets/6ddb7901-44c9-41a9-9091-164843f3ee2f" />


---

## Position in the Mycroft Pipeline

```
Earnings Call Intelligence Agent
        ↓ writes to Postgres
        
Tech Stack Directional Signal Agent  
        ↓ writes to Postgres
        
Contradiction Detection Agent
        ↓ reads from both
        ↓ fetches live news via Alpha Vantage
        ↓ runs 6 contradiction patterns
        ↓ writes conflict report to Postgres
        ↓ routes HIGH severity flags to human review
```

---

## The Six Contradiction Patterns

| Pattern | Agents Compared | What It Detects |
|---|---|---|
| 1 | Earnings ↔ News | Guidance direction vs news sentiment |
| 2 | Earnings ↔ News | Risk admitted on call but news tone doesn't reflect it |
| 3 | Earnings ↔ News | High Q&A evasion but analyst coverage positive |
| 4 | Earnings ↔ Tech Stack | Positive guidance but engineering footprint declining |
| 5 | Tech Stack standalone | Engineering burst with no management disclosure |
| 6 | Earnings ↔ News | Strengthened guidance against negative news momentum |

Patterns 1–3 and 6 require news data. Patterns 4–5 require Tech Stack Agent data. If data is unavailable for a pattern, it is marked as deferred — not skipped silently.

---

## Sample Output — Microsoft Q3 2024

```json
{
  "resolve_id": "CONTRA-MSFT-20260320-001",
  "ticker": "MSFT",
  "company_name": "Microsoft",
  "overall_confidence_level": "CONFIDENCE_REDUCED",
  "detection_summary": {
    "total_flags": 1,
    "high_severity": 1,
    "patterns_active": 6,
    "patterns_skipped": 0,
    "requires_human_review": true
  },
  "signal_inventory": {
    "guidance_signals": 1,
    "news_articles": 50,
    "tech_stack_snapshots": 1
  },
  "contradiction_flags": [
    {
      "pattern_id": 5,
      "pattern_name": "Engineering Burst vs Undisclosed Pivot",
      "severity": "HIGH",
      "conflict_description": "Significant engineering burst detected (burst_ratio=2.94x) but no corresponding management disclosure on earnings call",
      "recommended_action": "ESCALATE_TO_HUMAN",
      "requires_human_review": true
    }
  ]
}
```

**What this means:**
Microsoft's GitHub shows repo creation at 2.94x their historical baseline — engineers are in the middle of a major direction change. But on the Q3 2024 earnings call, management never disclosed this pivot to investors. That gap between what engineers are doing and what management told investors is flagged as HIGH severity.

---

## Architecture

```
Manual Trigger
      ↓
Set Company Input (ticker, company, lookback_days)
      ↓
HTTP: Alpha Vantage News API (live sentiment)
      ↓
Process + Save News Signals
      ↓
┌─────────────────────────────────────────┐
│  DB: Fetch Earnings Guidance Signals    │
│  DB: Fetch Risk Admissions              │
│  DB: Fetch QA Pressure Map             │──→ Merge → Aggregate All Signals
│  DB: Fetch News Signals                 │
│  DB: Fetch Tech Stack Signals           │
└─────────────────────────────────────────┘
      ↓
Run Pattern Detection Engine (6 patterns, pure logic)
      ↓
Build Groq Prompt
      ↓
LLM Needed? (IF contradictions found)
  YES → Groq: Analyse Contradictions (llama-3.3-70b-versatile)
  NO  → No-Flag Passthrough
      ↓
DB: Insert Contradiction Report
      ↓
Fan Out Flags → DB: Insert Contradiction Flag (one row per flag)
      ↓
Build Final Report (visible in n8n output panel)
```

---

## Data Sources

| Source | What It Provides | Agent |
|---|---|---|
| Earnings call transcripts | Guidance signals, risk admissions, Q&A pressure | Earnings Call Agent |
| GitHub GraphQL API | Repo burst, language shifts, velocity | Tech Stack Agent |
| Alpha Vantage News API | Headlines, sentiment scores, topic tags | Built into this agent |

---

## Database Tables

This agent creates and writes to two new tables:

### contradiction_reports
One row per agent run. Stores the overall verdict.

```sql
CREATE TABLE IF NOT EXISTS contradiction_reports (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  resolve_id TEXT UNIQUE NOT NULL,
  ticker TEXT,
  company_name TEXT,
  fiscal_quarter TEXT,
  lookback_days INT,
  total_flags INT DEFAULT 0,
  high_severity_count INT DEFAULT 0,
  medium_severity_count INT DEFAULT 0,
  overall_confidence_level TEXT,
  overall_assessment TEXT,
  overall_investment_relevance INT,
  patterns_active INT,
  patterns_skipped INT,
  signal_counts JSONB,
  requires_human_review BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### contradiction_flags
One row per flag detected. Stores the specific conflict details.

```sql
CREATE TABLE IF NOT EXISTS contradiction_flags (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  flag_id TEXT UNIQUE NOT NULL,
  resolve_id TEXT,
  ticker TEXT,
  pattern_id INT,
  pattern_name TEXT,
  severity TEXT,
  conflict_description TEXT,
  claim_a_id TEXT, claim_a_source TEXT,
  claim_a_text TEXT, claim_a_direction TEXT,
  claim_b_id TEXT, claim_b_source TEXT,
  claim_b_text TEXT, claim_b_direction TEXT,
  evidence_for_a TEXT,
  evidence_for_b TEXT,
  plausibility TEXT,
  investment_relevance_score INT,
  self_resolving BOOLEAN,
  analyst_memo TEXT,
  recommended_action TEXT,
  resolution_status TEXT DEFAULT 'UNRESOLVED',
  requires_human_review BOOLEAN DEFAULT TRUE,
  flagged_at TIMESTAMPTZ
);
```

You also need a `news_signals` table:

```sql
CREATE TABLE IF NOT EXISTS news_signals (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  claim_id TEXT UNIQUE NOT NULL,
  ticker TEXT,
  published_at TIMESTAMPTZ,
  source_name TEXT,
  headline TEXT,
  sentiment_label TEXT,
  sentiment_score NUMERIC,
  topic_tags TEXT[],
  schema_valid BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Prerequisites

Before running this agent, both upstream agents must have run for the same ticker:

- **Earnings Call Intelligence Agent** — guidance_signals table must have rows
- **Tech Stack Directional Signal Agent** — tech_stack_signals table must have rows with the correct ticker

---

## Setup Instructions

### 1. Import the workflow
 upload `Contradiction_Detection_Agent_ManualTrigger.json`

### 2. Set credentials
- All Postgres nodes → select your **Postgres account**
- Groq node → select your **Groq account**
- HTTP Request node → add your **Alpha Vantage API key** as a query parameter

Get a free Alpha Vantage API key at: https://www.alphavantage.co/support/#api-key

### 3. Create the database tables
Run the three CREATE TABLE statements above in your Postgres database.

### 4. Add unique constraint for news_signals
```sql
ALTER TABLE news_signals 
ADD CONSTRAINT news_signals_claim_id_unique 
UNIQUE (claim_id);
```

### 5. Configure the company
Click the **Set Company Input** node and update:
```
ticker        = MSFT        ← change to any company
company_name  = Microsoft   ← change accordingly
lookback_days = 365         ← how far back to look
```

### 6. Run
Click **Execute Workflow** — results appear in the **Build Final Report** node output panel.

---

## Changing the Company

To run for a different company (e.g. OpenAI after running the other two agents for OpenAI):

1. Click **Set Company Input** node
2. Change `ticker` and `company_name`
3. Click **Execute Workflow**

No Postman, no API calls, no code changes needed.

---

## Confidence Level Labels

| Label | Meaning |
|---|---|
| `NO_CONTRADICTIONS_DETECTED` | All signals consistent across agents |
| `LOW_CONCERN` | Minor discrepancy, likely noise |
| `REVIEW_WARRANTED` | ≥2 medium severity flags |
| `CONFIDENCE_REDUCED` | ≥1 high severity flag |
| `CRITICALLY_COMPROMISED` | ≥2 high severity flags |

---

## Recommended Actions

| Action | When |
|---|---|
| `ESCALATE_TO_HUMAN` | High severity — human must review before any decision |
| `MONITOR` | Medium severity — watch for further signals |
| `DISMISS` | Low relevance — likely timing or framing artefact |

---

## What This Agent Will NOT Do

- Make buy, sell, or hold recommendations
- Resolve contradictions automatically
- Override human judgment
- Produce output from a single agent alone (requires both upstream agents)

---

## Updates — March 2026

### Added: Alpha Vantage news integration
- HTTP Request node fetches live news sentiment per ticker
- Processes 50 most recent articles
- Saves to `news_signals` table before pattern detection runs
- Enables Patterns 1, 2, 3, 6 to fire with real market data

### Added: Merge node before Aggregate All Signals
- Prevents race condition where Aggregate ran before all 5 DB fetches completed
- Ensures tech stack data always reaches the pattern engine

### Fixed: Boolean comparison for burst_detected
- Postgres returns booleans as strings through n8n
- Pattern 5 now correctly handles both `true` and `"true"`

### Fixed: All DB queries use correct column names
- `claim_type AS guidance_topic` instead of `guidance_topic`
- `risk_text AS risk_description` instead of `risk_description`
- `is_repeated_topic AS evasion_flag` instead of `evasion_flag`
- `asked_by_firms AS analyst_firm` instead of `analyst_firm`

---

## Falsification Test

Per the Mycroft proposal: inject synthetic claims conforming to the shared claims schema for all 6 patterns. Each injection must trigger a flag. If any pattern fails to flag, that pattern's detection logic is redesigned before integration.

Patterns 4 and 5 were validated against real Microsoft GitHub data (burst_ratio = 2.94x, 9 declining languages). Pattern 5 fires correctly. Pattern 4 requires a company with both positive guidance and declining tech stack — not yet validated on real data.

---

## Related Agents

- [Earnings Call Intelligence Agent](../Earnings%20Call%20Intelligence%20Agent/)
- [Tech Stack Directional Signal Agent](../Tech_Stack_Directional_Signal_Agent/)

---

*Built by Anshika Khandelwal as part of the Mycroft Framework Intelligence Layer.*
*Featured workflow: Contradiction detection across financial and engineering signals.*
