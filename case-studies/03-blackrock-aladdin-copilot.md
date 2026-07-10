# BlackRock: Agentic AI in Asset Management
## AI-Powered Analytics, Private Credit Transparency, and the Limits of "Agentic" in Practice

**Case Study — Professional/Industry Document**
**Series:** Agentic AI Adoption in Financial Services (2025–2026)
**Classification:** Public Information — Sourced from Verified Public Disclosures

---

## Executive Summary

BlackRock's Aladdin platform is the operating layer beneath a large share of global institutional investing — public filings put BlackRock's own assets under management at $13.9 trillion as of Q1 2026, while the Aladdin platform itself, licensed to a much broader universe of institutional clients, is widely reported at roughly $25 trillion in tracked assets. BlackRock has not published a single audited figure for that platform-wide number; it is a company claim repeated consistently across press coverage, not a disclosure with the precision of a 10-Q line item. This case study keeps those two numbers separate throughout, because collapsing them — attributing platform-wide client assets to a specific AI feature, as if the feature itself "manages" that scale — is exactly the kind of category error this series exists to catch.

The AI feature at the center of this case study is Aladdin Copilot, and it is also the center of a genuine, unresolved tension in how BlackRock talks about its own technology. In BlackRock's own product communications — including the primary press release announcing Copilot's May 2026 expansion into private credit analytics via the firm's 2025 acquisition of Preqin — the system is described in restrained terms: "AI-powered analytics and research" and "AI Research Assistants" that let users "interrogate" data and "synthesize" visual insights. Nowhere in that release does BlackRock call this an agent or an agentic system. Yet in a separate public venue — a conference presentation given by two of BlackRock's own AI engineers — the broader Copilot system is described as a "supervised agentic architecture," built on LangChain and LangGraph with GPT-4 function calling, routing natural-language queries across a plugin registry serving 50–60 engineering teams and more than 100 front-end applications.

Both of these are BlackRock's own words, aimed at different audiences, and they do not fully agree with each other. This case study treats that disagreement as a finding, not a detail to smooth over. It documents what the public record actually supports about the private-credit workflow specifically (a user-triggered research assistant, not an autonomously initiating agent), what the broader Copilot architecture is documented to do (agentic-style orchestration under human query, per BlackRock's own engineers), and what neither source claims (autonomous portfolio monitoring, or any form of autonomous execution — Copilot does not trade, rebalance, or take action of any kind; it answers).

---

## 1. Firm Context and Strategic Rationale

BlackRock is the world's largest asset manager by AUM, reporting $13.9 trillion in assets under management as of March 31, 2026, per its Form 10-Q filed with the SEC. Separately, and on a different basis, the Aladdin platform — BlackRock's investment and risk management technology, licensed to banks, insurers, pensions, corporations, and other asset managers as clients in their own right — is reported in press coverage at approximately $25 trillion in tracked assets as of late 2025, spanning more than 1,000 institutional users globally. BlackRock does not publish this platform-wide figure as an audited disclosure; it is the company's own repeated public claim, carried consistently across financial and crypto-industry press, and this case study treats it accordingly — as a widely repeated but company-sourced figure, not a verified metric.

The distinction matters structurally. Aladdin is not BlackRock's internal tool alone — it is a business line BlackRock sells, and the AI capabilities layered into it are built for that broader client base, not solely for BlackRock's own portfolio managers. In 2025, BlackRock closed acquisitions of Preqin (a private markets data provider), HPS Investment Partners (a private credit manager), and ElmTree (a real estate manager) — the firm's largest set of integrations in more than fifteen years, according to its own proxy filing. Preqin's private markets data is the direct predicate for the private-credit analytics workflow this case study examines: BlackRock is combining data it already owned the pipes for (Aladdin, eFront) with data it acquired (Preqin) and layering AI-powered analysis on top.

The operational problem this solves is specific to private markets. Public-market portfolios have standardized, frequently updated pricing and disclosure. Private credit — direct lending, BDCs, closed-end funds, semi-liquid vehicles — does not. Fund structures vary, disclosure cadence varies, and the same underlying loan can appear differently across GP reporting formats. Assessing risk, liquidity, or exposure at the asset level, rather than the fund level, has historically required manual reconciliation across inconsistent documents. That is the fragmentation problem BlackRock is selling a solution to, and it is a real, well-documented industry problem independent of any AI claim.

---

## 2. The Operational Problem

### 2.1 Private Credit Data Fragmentation

Private credit funds report to their limited partners on their own schedules, in their own formats, at the fund level rather than the underlying-asset level. An LP or risk analyst trying to understand true exposure — which borrowers, which industries, which leverage levels sit beneath a given BDC or closed-end fund — has historically had to manually pull fund administration documents, normalize inconsistent terminology and reporting periods across GPs, and reconstruct asset-level detail that no single source provides in standardized form. BlackRock's own press materials describe private credit as "fragmented by design, with many wrapper formats and siloed data sources," a characterization attributed to Leon Sinclair, BlackRock's Global Head of Preqin Product, in the firm's May 2026 announcement.

The manual version of this work is the same category of problem Goldman Sachs and JPMorgan Chase both faced in their respective domains: large volumes of unstructured or inconsistently structured data that must be normalized before any judgment can be applied to it. What differs here is that the end product is not a decision with a settlement or credit-approval consequence — it is an analytical view. Nothing in BlackRock's Aladdin private credit tooling, as publicly documented, executes a trade, rebalances a portfolio, or commits capital. That is a structural difference from both prior case studies in this series, and it matters for how "agentic" this deployment can honestly be described as being: a system with no execution authority is a different category of system from one that is architecturally blocked from executing without approval, even though both end in a human decision.

### 2.2 Querying at Scale Across a Unified Platform

The second, related problem is one of access, not just data quality. Aladdin already unifies public and private asset data on a single platform for its institutional clients. But translating a portfolio manager's question — "what's my exposure to this borrower across every BDC and closed-end fund I hold" — into the right combination of the hundreds of domain-specific APIs Aladdin exposes has historically required either a specialist who knows the platform deeply, or a manual, multi-step query process across separate tools. This is the problem Aladdin Copilot as a whole (not just the private-credit feature) is documented to address: natural-language access to a large surface area of specialized, siloed internal capability.

---

## 3. The AI Deployment: What's Confirmed, and Where the Record Disagrees

> **Note on section title.** This section departs from this series' usual "The Agentic AI Solution" header. That's deliberate, not an inconsistency: the public record doesn't support describing a single, agreed-upon "solution" here the way it does for Goldman Sachs and JPMorgan Chase. The title reflects what this section actually does — establish what's confirmed and name where BlackRock's own communications disagree with each other.

BlackRock's deployment in this space is best understood as two claims from two different parts of the same company, describing overlapping but not identical things.

**Claim 1 — the private-credit feature, per BlackRock's own product announcement (primary source).**
On May 6, 2026, BlackRock announced an expansion of Aladdin's private credit capabilities via Preqin, described in the press release as "Integrated AI-powered analytics and research" that "enable users to interrogate market, fund and asset data within a single environment, synthesize with custom visual insights." The release introduces standardized asset-level benchmarks — money multiples, valuation trends, leverage ratios, defaults and recoveries, equity cushion multiples, and borrower financials — that let users assess risk and performance across BDCs and closed-end fund structures that previously required fund-by-fund manual reconciliation. Nowhere in this release, or in any of the wire-service and trade-press reproductions of it (Yahoo Finance, BusinessWire, Preqin, Funds Society, Markets Media, Hubbis all ran the same language), does BlackRock describe this feature as an agent or as agentic. The verbs are all user-initiated: "interrogate," "synthesize," "assess." This is BlackRock's own choice of language for its own product, in its own announcement, and it describes an on-demand research assistant, not an autonomously initiating system.

**Claim 2 — the broader Aladdin Copilot architecture, per BlackRock's own engineers (primary-adjacent source).**
Separately, in a public technical presentation documented in the ZenML LLMOps database, two BlackRock AI engineers — Brennan Rosales (AI Engineering Lead) and Pedro Vicente Valdez (Principal AI Engineer) — describe Aladdin Copilot broadly as a "supervised agentic architecture" built on LangChain and LangGraph, using GPT-4 function calling to orchestrate specialized tool calls. In this description, a filtering and access-control node narrows the searchable universe of available plugins and tools down to roughly 20–30 relevant options per query, out of a much larger registry serving 50–60 specialized engineering teams across more than 100 front-end applications on the platform. The stated design goals are democratizing access to Aladdin's own APIs through natural language, and doing so under guardrails: output filters intended to catch hallucinations, and an explicit boundary preventing Copilot from issuing investment advice outside Aladdin's own data. This is a legitimate agentic-systems description — tool orchestration, supervised autonomy over which internal capability to invoke — but it describes Copilot's general query-routing function across the whole platform, not the private-credit feature specifically, and no source ties this architecture description to the Preqin-powered private credit workflow by name.

**What neither source claims.** Neither the product announcement nor the engineering presentation describes Copilot autonomously monitoring positions, initiating analysis without a user prompt, or taking any action with financial consequence. Both describe a system that responds to a query and returns an answer. That agreement — between BlackRock's own restrained product language and BlackRock's own engineers' more technical description — is the load-bearing evidence here, and it doesn't require an outside source to make the point: the company's public statements about itself already establish the boundary.

**The honest read:** the private-credit analytics workflow this case study illustrates is real, is built on real data infrastructure (Aladdin plus Preqin plus eFront), and plausibly sits on top of the agentic orchestration layer BlackRock's engineers describe for Copilot generally. But it is documented, by BlackRock itself, as a query-and-response research tool — not an autonomous agent making or executing decisions. Readers of this series should take from that a specific lesson: a vendor calling its own broader platform "agentic" in one venue does not mean every feature built on that platform is agentic in the sense this series has otherwise documented at Goldman Sachs and JPMorgan Chase, where agents took multi-step autonomous action within a structurally enforced human-approval boundary. Here, the boundary is simpler, because there is nothing downstream to approve — the system doesn't act at all.

---

## 4. Illustrated Workflow: Private Credit Exposure Query During a Market Volatility Event

> **IMPORTANT: This workflow is an illustrative scenario constructed for demonstration purposes.**
> It is built from BlackRock's publicly disclosed architecture — the query-routing pattern, the plugin/tool registry, the guardrail structure, and the private-credit benchmark categories are sourced from public documentation. The specific portfolio, fund names, and figures used in this scenario are hypothetical and are not claimed to represent any BlackRock client's actual holdings or BlackRock's proprietary operational procedures.

---

### The Scenario

A market volatility event has hit the leveraged loan and private credit markets. A portfolio manager at an institutional client of Aladdin needs to understand their fund's exposure to a specific mid-market industrial borrower across several BDC and closed-end fund positions before end of day. Under the manual process, this would require pulling fund-level reports from each GP relationship, manually identifying which funds hold exposure to the borrower, and reconciling leverage and valuation figures reported in inconsistent formats. Under the Copilot-plus-Preqin workflow, the PM instead poses the question directly to the platform.

This is the case we will trace.

---

### Phase 1: Query Submission and Routing (Human-Initiated, Then Autonomous Routing)

**Step 1 — Natural-Language Query**
The portfolio manager types a plain-language question into Aladdin: exposure to the borrower across all BDC and closed-end fund holdings, with current leverage and valuation trend. Nothing happens until this query is submitted — there is no autonomous monitoring trigger in the documented architecture.

**Step 2 — Tool Selection and Scoping**
Copilot's orchestration layer parses the query and, per BlackRock's own described architecture, a filtering and access-control node narrows the full plugin/API registry down to the relevant 20–30 tools for this specific request — in this case, Preqin's private credit data APIs, Aladdin's portfolio holdings API, and the relevant benchmark calculation modules. This scoping step is autonomous, but it is scoping a response to a request that was made, not initiating a new inquiry.

---

### Phase 2: Data Retrieval, Synthesis, and Verification (Autonomous, Request-Scoped)

**Step 3 — Cross-Referencing Fund-to-Asset Data**
The system queries Preqin's private credit data for asset-level detail beneath each fund wrapper, matching the borrower across whichever BDC and closed-end fund structures hold exposure to it. This is the specific capability the 2026 Preqin expansion introduced — a fund-to-asset view rather than fund-level-only reporting. Because this query is scoped by borrower name rather than by a specific fund, the private-credit retrieval and the portfolio-holdings retrieval are not fully independent here: portfolio position records are held by fund, not by borrower, so the system must first resolve which funds carry the borrower exposure, then join that result against portfolio holdings by fund. A query scoped by fund ID rather than borrower name could run both retrievals in true parallel; a borrower-scoped query, like this one, cannot.

**Step 4 — Benchmark Calculation**
For each fund identified, the system calculates the standardized private-credit benchmarks BlackRock's private credit suite introduced: money multiple, valuation trend, leverage ratio, and equity cushion multiple, alongside the borrower's reported financials. These are compared against category benchmarks across the broader BDC and closed-end fund universe.

**Step 5 — Synthesis, Then Guardrail Verification**
The system first assembles a draft summary: exposure by fund, leverage and valuation trend lines, and a comparison against the broader benchmark set. Only once that draft exists does a separate guardrail step — per BlackRock's engineering description of Copilot's architecture *generally, not confirmed as specific to this private-credit feature* — check every figure in it against the underlying computed data, screening for unsupported or hallucinated numbers before anything is returned to the PM.

**The system does not flag a recommendation, does not rebalance, and does not take any portfolio action. It returns an analytical view. There is no settlement, execution, or approval-token architecture here, because there is nothing being executed — this workflow ends at information, not at a decision with financial consequence.**

---

### Phase 3: Human Review and Decision (Human Decision Point)

**Step 6 — Portfolio Manager Review**
The PM reviews the synthesized exposure summary: which funds carry exposure, at what leverage, and how valuation has trended through the volatility event. They bring context the system does not have — GP relationship history, sector-specific concerns about the borrower's industry, or knowledge of covenant negotiations not captured in Preqin's structured data.

**Step 7 — Decision**
The PM decides whether the exposure requires action: flagging the position for closer monitoring, raising it with the GP, adjusting future allocation, or taking no action. Whatever decision follows happens entirely outside the tooling described here — Copilot's documented role ends at the synthesized analytical view.

---

### Workflow Summary: What the System Did vs. What the Human Did

| Step | Actor | Action |
|---|---|---|
| Submit natural-language query | Human (Portfolio Manager) | Required — nothing proceeds without this |
| Parse query, scope relevant tools | Copilot orchestration layer | Autonomous (request-scoped) |
| Retrieve fund-to-asset private credit data; join to holdings by fund | System (Preqin/Aladdin APIs) | Autonomous (request-scoped) |
| Calculate standardized benchmarks | System | Autonomous (request-scoped) |
| Synthesize visual summary (draft) | System | Autonomous (request-scoped) |
| Screen draft for hallucination | System (guardrail layer) | Autonomous (request-scoped) |
| Interpret exposure with qualitative context | Human | Required |
| Decide on any portfolio action | Human | Required |

Every autonomous step in this table is downstream of a human query and upstream of a human decision. Unlike the Goldman and JPMorgan workflows in this series, there is no architectural gate on an execution action, because the documented system has no execution capability to gate. The human-in-the-loop here is not a safeguard against autonomous action — it is the entire locus of action. The system's contribution is compression of the retrieval-and-calculation step, not participation in the decision.

---

## 4b. Reference Implementation

A working reference implementation of the workflow illustrated in Section 4 is available at `blackrock-aladdin-private-credit-workflow/README.md`. Like the JPMorgan case study's `agentic-credit-workflow/README.md`, it is explicitly labeled as an illustrative teaching pattern grounded in publicly documented architecture concepts — not a specification of BlackRock's actual, proprietary system. Its own README states this directly, and repeats it in the docstrings and runtime warnings of the modules most likely to be mistaken for risk-reviewed guidance.

Building the implementation surfaced two corrections that have been applied to Section 4 above, rather than left as silent discrepancies between the illustration and the working code:

- **The two data retrievals in Step 3 are not fully parallel for a borrower-scoped query.** Portfolio holdings are recorded by fund, not by borrower, so resolving "which funds hold this borrower" has to happen before joining that result against portfolio positions. A query scoped by fund ID could run both retrievals independently; the borrower-scoped query this case study illustrates cannot. Section 4 previously described these as independent parallel steps — that was inaccurate for its own scenario, and has been corrected.
- **Guardrail verification happens after synthesis, not before or concurrently.** A draft has to exist before its figures can be checked against the underlying computed data. Section 4's Step 5 previously implied the guardrail screened before synthesis; the order has been corrected to synthesis-then-verification.

Three further disclosures from the reference implementation are worth carrying into this case study directly, because they bear on what a reader should take away from the "guardrail" language used throughout Sections 3 and 4:

- **The benchmark thresholds used in the implementation (leverage above 6.0x, DSCR below 1.25x, equity cushion below 20%) are illustrative industry rule-of-thumb figures, not BlackRock's risk policy and not reviewed by any risk function.** The underlying ratio formulas are standard private-credit math; the cutoffs that decide when a figure gets flagged are not sourced to BlackRock at all, and the case study should not be read as implying they are.
- **The guardrail guarantees no unverified figure reaches the user silently — it does not guarantee that a single regeneration attempt always produces a correct figure.** When the guardrail can't verify a number, the implementation attempts one silent regeneration; if that also fails, it escalates visibly rather than retrying silently again. This is a meaningful distinction: "guardrail" in this context means detection-and-escalation is reliable, not that first-attempt correction is.
- **The implementation's own deviation log documents four additional differences from the developer architecture reference** (`Aladdin_Private_Credit_Developer_Reference.docx`) beyond the two folded into Section 4 — a schema field added to support valuation-trend calculation, an interface signature simplified from the reference doc's sketch, a function-vs-class implementation choice, and unimplemented chart/visual output left as a named extension point. None of these affect what Section 4 claims about BlackRock's actual system; they are implementation-level choices disclosed in the repository itself for anyone building from it.
- **The reference implementation's five computed ratios (including debt service coverage) do not map one-to-one onto the six benchmark categories named in BlackRock's own press release** (Sections 3–4: money multiples, valuation trends, leverage ratios, defaults and recoveries, equity cushion multiples, borrower financials). The implementation illustrates the calculation *pattern* — retrieve data, compute standardized ratios, flag against thresholds — using a representative ratio set, not a reproduction of BlackRock's specific six categories.

None of the above changes what this case study asserts about BlackRock. It changes what the illustrative workflow accurately demonstrates, and it discloses, in the same spirit as this series' sourcing standard, exactly where a teaching artifact's convenience choices diverge from the document it was built to implement.

---

## 5. Documented Results and Impact

Unlike the Goldman Sachs and JPMorgan Chase case studies in this series, no quantified productivity or efficiency figure for Aladdin Copilot or the private-credit analytics tooling was identified in primary or credible secondary reporting at the time of this writing. BlackRock's own press release describes the capability qualitatively — compressing what previously required manual, fund-by-fund reconciliation into "a single query" — but supplies no measured time savings, cost figures, or adoption metrics. This absence is itself worth stating plainly rather than filling with a repeated industry-aggregator estimate: this case study declines to cite a number that does not exist in the record, rather than reach for the kind of thinly sourced figure that required correction in both the Goldman Sachs and JPMorgan Chase case studies.

What can be documented: the private credit suite launched in May 2026 as "the first in a series of product enhancements" per BlackRock's own release, indicating continued investment rather than a one-off feature. Separately, BlackRock's technology and subscription services revenue — which includes Aladdin licensing — was reported by the company as growing at a double-digit rate with accelerating annual contract value into 2026, though this figure reflects the whole technology services segment, not the AI features specifically, and should not be read as evidence of Copilot's individual contribution.

---

## 6. Limitations, Failures, and Honest Caveats

### 6.1 The Core Limitation Is Definitional, Not Technical

The most significant caveat in this case study is not about model reliability or data quality — it is about what can honestly be claimed at all. BlackRock's own communications describe this specific feature in assistant terms, not agent terms. Presenting it as a fully autonomous agentic deployment, the way this series has documented at Goldman Sachs and JPMorgan Chase, would overstate what BlackRock itself claims. Readers should take away that "agentic AI" is applied inconsistently even within a single company's own public statements, and that the term's marketing value currently outpaces its documentation value in cases like this one.

### 6.2 Data Quality Remains the Binding Constraint

To the extent this system does compress analytical work, it is entirely dependent on Preqin and eFront data being current and accurately mapped from fund-level GP reporting to asset-level detail. Private markets data is inherently less standardized than public markets data, and BlackRock's own framing of the private credit problem — "fragmented by design" — describes a condition the AI layer sits on top of, not one it independently solves. A synthesis layer built on incomplete or stale underlying data produces a confident-looking but incomplete answer, and nothing in the public record describes how frequently underlying private credit data is refreshed relative to public market data.

### 6.3 No Execution Authority Means No Execution Risk — But Also No Execution Accountability Trail

Because Copilot in this workflow does not execute trades or rebalance portfolios, it does not carry the "speed-of-harm" risk documented at Goldman Sachs, where an agent with broad API permissions could in principle cause rapid, hard-to-detect harm. That is a genuine safety advantage of a pure decision-support architecture. But it also means there is no publicly documented equivalent to the token-gated settlement architecture or the tiered human-approval routing this series documented at Goldman Sachs and JPMorgan Chase. The absence of that architecture isn't a flaw here — it reflects that nothing requiring it exists in this feature — but it does mean this case study cannot describe a human-approval gate with the same structural specificity as the prior two, because the public record does not show one being necessary.

### 6.4 What the Public Record Cannot Confirm

- Whether the specific private-credit analytics workflow described in Section 4 uses the same LangChain/LangGraph, GPT-4-orchestrated architecture BlackRock's engineers described for Copilot generally, or a separate implementation — no source connects the two explicitly.
- Any quantified productivity, time-savings, or adoption figures specific to this feature.
- The refresh frequency or data-quality assurance process for Preqin's underlying private credit data as ingested by this tool.
- Whether BlackRock plans to expand this tooling toward any form of autonomous recommendation or action; the "first in a series of enhancements" language in the May 2026 release does not specify direction.
- **Whether any audit-trail or per-claim source-citation mechanism exists for Copilot's outputs.** This is a meaningful gap relative to the rest of this series: both Goldman Sachs and JPMorgan Chase document agents that cite every calculation to a specific source line item and write every step to an append-only compliance ledger. No source reviewed for this case study describes an equivalent mechanism for Copilot — not because one has been ruled out, but because nothing in BlackRock's public communications addresses output logging, retention, or auditability at all. In a compliance-facing workflow, that silence would be disqualifying. In an analytics tool with no execution authority, it may simply reflect a lower regulatory bar — but the public record does not say which, and this case study does not guess.

This case study does not assert claims beyond what the cited sources report.

---

## 7. Forward-Looking: BlackRock in the Agentic Era

> **Editorial analysis.** This section draws on publicly stated positions and broader industry trends. It should be read as informed projection, not as documented fact.

BlackRock's own trajectory suggests movement toward more, not less, agentic tooling, even if the private-credit feature examined here doesn't yet claim that label. In April 2026, the firm launched RockAI, described in trade press as a no-code platform intended to let employees build their own AI agents, built explicitly on top of the existing Aladdin Copilot foundation. If accurate, this suggests BlackRock's internal ambitions for agentic capability exceed what any single externally documented feature currently demonstrates — the infrastructure (the plugin registry, the orchestration layer, the guardrail architecture) is apparently being built out ahead of specific, named, externally verifiable agentic deployments.

The more interesting industry question this case study raises is not whether BlackRock will eventually deploy something unambiguously agentic in the sense Goldman Sachs and JPMorgan Chase have — it plausibly will, given the infrastructure investment already documented. It's whether the industry's current, loose usage of "agentic AI" as a marketing term will get disciplined by the same kind of scrutiny this series has tried to apply, or whether "agentic" will continue to be used interchangeably with "AI-powered" until the terms lose useful meaning. BlackRock's own inconsistency — restrained language in a product announcement, expansive language in an engineering talk — is a small, concrete illustration of that larger drift, from a company with every incentive to be precise about its own technology.

---

## Sources

| Source | Type | Date | Notes |
|---|---|---|---|
| BlackRock — Aladdin Expands Private Credit Solutions on Preqin | Primary — company press release | May 6, 2026 | https://www.blackrock.com/aladdin/discover/press-release/blackrock-aladdin-expands-private-credit-solutions-on-preqin — feature description, benchmark categories, Sinclair quote |
| BlackRock, Inc. — Form 10-Q | Primary — SEC filing | Filed 2026, period ended March 31, 2026 | BlackRock's own AUM ($13.9 trillion) |
| BlackRock, Inc. — Form DEFA14A (proxy statement) | Primary — SEC filing | 2026 | Confirms 2025 closings of HPS, Preqin, and ElmTree acquisitions |
| ZenML LLMOps Database — "BlackRock: Agentic AI Architecture for Investment Management Platform" | Primary-adjacent — documented conference presentation by BlackRock AI engineers (Brennan Rosales, Pedro Vicente Valdez) | Undated (referenced 2025–2026) | https://www.zenml.io/llmops-database/agentic-ai-architecture-for-investment-management-platform — Copilot's general architecture: LangChain/LangGraph, GPT-4 function calling, plugin registry, guardrails |
| AI2Work — "BlackRock Launches RockAI: No-Code Platform to Democratize AI Agents" | Secondary — trade press | April 23, 2026 | https://ai2.work/blog/blackrock-launches-rockai-no-code-platform-to-democratize-ai-agents — RockAI launch, built on existing Copilot foundation |
| Aladdin (BlackRock) — Wikipedia, aggregating multiple cited news sources | Secondary — reference aggregation of press-reported figures | Accessed 2026 | Historical Aladdin platform AUM figures (2013: $11T; 2020: $21.6T) for trend context only |

Note on the $25 trillion platform-AUM figure cited in Section 1: this figure is repeated consistently across 2025–2026 press coverage (including crypto-industry press covering unrelated Aladdin integrations) but is not traceable to a specific BlackRock financial disclosure. It is treated in this case study as a widely repeated company claim, not a verified metric, and is kept explicitly separate from BlackRock's own reported AUM.

---

*This case study is part of the series: Agentic AI Adoption in Financial Services (2025–2026). Illustrative workflow scenarios are clearly labeled and constructed from publicly disclosed architectural details. No proprietary BlackRock operational data is claimed or represented.*
