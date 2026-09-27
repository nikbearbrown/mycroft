---
title: Glossary
slug: glossary
section: Reference
order: 40
summary: The terms this system uses, in plain words, with where each one lives.
---

| Term | Meaning |
|---|---|
| **Accession number** (`accn`) | SEC's id for one filing. Every figure an agent is given carries one, so it can be found in the filing ([[datasources/edgar.py]]). |
| **ADR-06 / ADR-07** | Two early architecture decisions: ADR-06, partial mitigations for fabricated reasoning (claims, citation checks, the consistency probe); ADR-07, one retry then halt. |
| **Agent** | A model called through the `AgentAdapter` contract ([Agents](f-agents.html)). |
| **Assessment** | An agent's view as data: grade, direction, assumptions, key metrics, key points ([Grades](f-grades.html)). |
| **Attempt** | One call of an agent within the validation loop; at most two per agent per run. |
| **Auditor / investor scope** | The two read scopes. Auditors see everything; investors never see the internal tier, and not the disputed material while a gate is pending ([Gate and scope](f-gate.html)). |
| **Canonical fact** | A figure tagged with its metric, period and family ([[validation/facts.py]]). |
| **Check** | An accounting rule over an agent's figures or the filing; `hard` or `heuristic` ([Checks](f-checks.html)). |
| **CIK** | SEC's company id, looked up from the ticker. |
| **companyfacts** | SEC's JSON of every XBRL fact a company has filed. One fetch serves both agents. |
| **Compare run** | Two agents on one subject, compared figure by figure ([Comparison](f-compare.html)). |
| **Consensus grade** | Proposed only when both agents gave the same grade and direction and no hard check failed. |
| **Consistency probe** | Asking the same question a second time and scoring the drift ([[validation/consistency.py]]). |
| **Contradiction rule** | Which rule sets a compare's `contradiction_flag`: `concept_aware`, `canonical_facts` or `symmetric_difference`. |
| **Corrective directive** | The fixed instruction used for attempt 2 after a structural failure ([[pipeline/middleware.py]]). |
| **Decision item** | A figure, check or grade the gate needs a human to decide. |
| **Directive** | The versioned system prompt that states the output contract ([[core/directive.py]]). |
| **Directive echo** | A conclusion that copies the directive back; rejected as a structural failure. |
| **Drift** | Here: a document or comment that no longer matches the code ([Drift found while documenting](drift.html)). |
| **Extraction** | The separate model call that reads a finished answer for its assessment ("option 1"). |
| **Gate** | The hard stop where a named reviewer decides each open item ([[validation/gate.py]]). |
| **Gate policy** | The versioned rule for what opens the gate; `v3` today. |
| **Grade** | A credit-style rating, `AAA` to `CCC`: always a model's judgment unless a human set it. |
| **Halt** | The end of the loop when both attempts fail; the run is stored as halted. |
| **Honest Ledger** | The system's own list of known issues, in code ([Honest Ledger](ledger.html)). |
| **Inline XBRL** | Machine-readable tags inside a filing's HTML, used to find a figure in the document itself ([[datasources/filings.py]]). |
| **Internal tier** | The fields investors never see: reasoning, raw output, tokens, directive text, inputs, assessments (SEC-01). |
| **Lens** | What one agent is shown: a list of us-gaap concepts over the shared companyfacts payload ([[producers/lens.py]]). |
| **Pairing** | Which two lenses a compare uses: `lenses` or `bull_bear`. |
| **Reasoning object** | The record of one attempt ([[core/schemas.py]]). |
| **SEC-01 / SEC-02** | Security requirements: the investor-scope internal tier, and scope carried in a bearer token, never a query parameter. |
| **Source sanity** | Checks on the filing itself, which never gate. |
| **Step trace** | The ordered, timed record of every call in a run ([[web/step_trace.py]]). |
| **Structural failure** | A reply that breaks the two-block contract ([[core/parsing.py]]). |
| **Synthesis** | Why two agents' views differ, what each has behind it, and whether a consensus exists ([[validation/divergence.py]]). |
| **Tavily** | The web search API the agents use as a tool. |
| **us-gaap concept** | An XBRL accounting tag, such as `Revenues` or `EarningsPerShareDiluted`. |
