# HSBC: Agentic-Adjacent AI in Investment & Commercial Banking
## A Confirmed Coding-Assistant Rollout, a Separately-Named Agentic System, and Two Simplification Programmes That Should Not Be Read as One

**Case Study — Professional/Industry Document**
**Series:** Agentic AI Adoption in Financial Services (2025–2026)
**Classification:** Public Information — Sourced from Verified Public Disclosures

---

## A Note on Scope Before We Begin

This case study covers HSBC Holdings plc's AI deployment in and around its Corporate and Institutional Banking (CIB) segment, treating two genuinely separate systems as separate:

1. **A confirmed coding-assistant rollout** — 31,000 engineers enabled as of HSBC's FY2025 Annual Results call, delivering two distinct, HSBC-confirmed productivity outcomes (60% faster unit testing; 5x faster vulnerability patching), described by HSBC as assistive tools, not autonomous agents.
2. **A separately-named, later-announced agentic system** — a financial-crime detection partnership with Google Cloud, announced roughly four months after the coding-assistant figures were disclosed, explicitly using the term "agentic AI" in a way HSBC has never applied to its coding tools.

Alongside these, HSBC is running two further initiatives this case study treats as distinct from the AI story and from each other: an organisational-simplification programme (headcount/role-duplication savings) and a legacy-application-demise programme (technical-debt reduction). None of these four threads — coding assistants, agentic financial-crime detection, organisational simplification, application demise — is stated by HSBC to cause or explain any of the others. This case study's central discipline is keeping them apart rather than assembling them into a single, more dramatic "AI transformed HSBC" narrative than HSBC's own disclosures actually support.

This entry deliberately scopes out HSBC's Mistral AI partnership (December 2025), the appointment of David Rice as HSBC's first Chief AI Officer (April 2026), and HSBC's broader "50 processes" reengineering workstream — each a genuine HSBC initiative, each mentioned where relevant for context, none developed into a full section here.

---

## Executive Summary

HSBC discloses two real, dated, precisely-sourced AI-productivity figures for its coding assistants — 60% faster unit testing and five times faster vulnerability patching — attached to a rollout that reached 31,000 enabled engineers by its FY2025 results (25 February 2026), up from a lower figure disclosed roughly six to eight months earlier. HSBC is careful, in its own language, to describe these as assistive tools that engineers use, not autonomous agents: no HSBC source describes an agent independently monitoring the codebase, retrieving context, and drafting patches without human review.

Separately, and roughly four months after those figures were disclosed, HSBC announced a partnership with Google Cloud that explicitly uses the term "agentic AI" — but for financial-crime detection, not coding. This case study treats the resulting contrast — assistive coding tools on one side, an explicitly agentic financial-crime system on the other — as a genuine pattern in HSBC's own terminology, while being careful to label it as an inference this case study draws by reading two separate disclosures together, not a distinction HSBC has stated in any single place. This entry's title calls HSBC's overall AI posture "agentic-adjacent" for exactly this reason: HSBC sits next to the agentic-AI conversation, with one genuinely agentic system in production, while its higher-profile coding-assistant story remains, by HSBC's own description, assistive rather than autonomous.

A third and fourth thread run alongside both AI stories without HSBC connecting them to either: a $1.5 billion organisational-simplification programme targeting headcount and role duplication (with $1.2bn realized by year-end 2025, and $1.8bn in associated severance costs disclosed a year earlier), and a legacy-application-demise programme that shrank HSBC's non-strategic application estate by 1,165 applications in 2025 alone. This case study's most significant sourcing correction, made during verification, concerns the $1.8bn figure specifically: an unrelated, later HSBC disclosure uses the same dollar amount for something else entirely (cost reallocation, not severance), and this entry deliberately uses only the earlier, correctly-attributed figure to avoid that conflation.

The sections that follow lay out HSBC's firm context and strategic rationale, the operational problem behind both the technology and organisational threads, what is and is not confirmed about the coding assistants and the agentic financial-crime system, an illustrated workflow and a tested reference implementation grounding it, the documented results across all four threads kept separate, the limitations and caveats this case study identified, and a forward-looking, clearly-labeled editorial section — each attributed to its actual source.

---

## 1. Firm Context and Strategic Rationale

HSBC Holdings plc is one of the world's largest banking and financial services organisations, with total assets of $3,233,034m at 31 December 2025. *[Source: HSBC Holdings plc Annual Results 2025 media release, 25 February 2026]* Headquartered at 8 Canada Square, London, HSBC holds a primary listing on the London Stock Exchange (LSE: HSBA) and the Hong Kong Stock Exchange (HKEX: 5), with secondary listings on the New York Stock Exchange (NYSE: HSBC) and the Bermuda Stock Exchange. It serves around 41 million customers across 56 countries and territories, and describes the UK and Hong Kong as its two home markets. *[Source: HSBC "Our markets" corporate page; HSBC Annual Results 2025 media release]*

For FY2025, HSBC reported revenue (net operating income before change in expected credit losses) of $68,274m and reported profit before tax of $29,907m — a decline of $2.4 billion from FY2024's $32,309m. *[Source: HSBC Annual Results 2025 media release, 25 February 2026]* That headline decline is fully attributable to a $4.9 billion adverse year-on-year swing in notable items — dilution and impairment losses on HSBC's Bank of Communications associate, reserve-recycling losses on the sale of its French retained home-loan portfolio, legal provisions, and organisational-simplification restructuring costs — and not to any deterioration in underlying trading. On a constant-currency basis, excluding notable items, profit before tax rose $2.4 billion to $36,617m, and return on tangible equity excluding notable items rose 1.6 percentage points to 17.2%. *[Source: HSBC Annual Results 2025 media release]* This case study presents both the reported and underlying figures rather than the reported figure alone, because reported PBT on its own would understate a period in which HSBC's own disclosed operating trend was improving.

HSBC's workforce stood at approximately 208,000 full-time-equivalent staff (208,720 precisely) at year-end 2025, down from roughly 214,000 FTE at end-2024. *[Source: HSBC Annual Report and Accounts 2025; HSBC "About HSBC" corporate descriptor]* This case study is careful to attribute this figure to HSBC specifically and not to conflate it with headcount figures from other companies this series has covered.

**Leadership and organisational structure.** Georges Elhedery became Group Chief Executive effective 2 September 2024, succeeding Noel Quinn. Pam Kaur became Group Chief Financial Officer effective 1 January 2025 — HSBC's first female CFO — having previously served as Group Chief Risk and Compliance Officer since 2013. *[Source: HSBC leadership disclosures; HSBC Annual Results 2025 media release]* Effective 1 January 2025, HSBC restructured its segment reporting into four businesses plus Corporate Centre: Hong Kong, UK, Corporate and Institutional Banking (CIB), and International Wealth and Premier Banking (IWPB). *[Source: HSBC Annual Results 2025 media release, segmental notes]* This replaced the prior structure of Wealth and Personal Banking, Commercial Banking, Global Banking and Markets, and Corporate Centre; CIB specifically integrates the former Commercial Banking business (outside the UK and Hong Kong) with the former Global Banking and Markets business. All segmental comparatives in HSBC's FY2025 disclosures were re-presented on this new basis, and this case study uses only the current segment names throughout, rather than the retired ones.

HSBC's own account of why this restructuring happened is explicit and is the closest primary-source language to the "high structural complexity, extensive legacy technology, and fragmented operational workflows" framing this case study opened with. HSBC's 22 October 2024 announcement stated the changes "will reduce the duplication of processes and decision making that are built into the current structure and will result in greater alignment and agility in serving our customers." *[Source: HSBC "Simplified organisational structure to accelerate strategic execution," 22 October 2024, filed with the SEC]* Elhedery told analysts the following week: "The primary reason for the reorganization is to simplify the bank and remove duplication of roles… The cost savings are an ancillary benefit." *[Source: reported via Reuters/Banking Dive, 29 October 2024]* At FY2025 results, he described HSBC as "becoming a simple, more agile, focused bank, one that moves with the speed our customers need to navigate the modern world." *[Source: HSBC Annual Results 2025 Announcement — Edited Transcript, 25 Feb 2026]* In 2025, HSBC reduced net Managing Director positions by circa 15% as part of this effort. *[Source: same]*

**Corporate and Institutional Banking (CIB): the segment this case study is anchored on.** CIB is the closest current HSBC segment to "Investment & Commercial Banking," combining transaction banking and capital markets activity. It was the single largest contributor to Group profit in FY2025, posting revenue of $27,637m and constant-currency profit before tax of $11,386m — 38.1% of Group PBT, ahead of Hong Kong (32.0%), UK (22.4%), and IWPB (14.6%). *[Source: HSBC Annual Results 2025 media release, segmental data]* This scale is the direct context for why CIB is where this case study locates its coding-assistant and engineering-productivity narrative: it is HSBC's largest segment by profit contribution, and — as later sections document — it is also the segment David Rice, HSBC's newly appointed Chief AI Officer, served as Chief Operating Officer immediately prior to his AI appointment. *[Source: HSBC / CIO Dive coverage of the Chief AI Officer appointment, 23 March 2026]*

**Market position.** HSBC is the largest UK-listed bank by market value and, as of late January 2026, became the first European-listed lender to surpass a $300 billion market capitalization. *[Source: Bloomberg, 27 January 2026]* By total assets, S&P Global Market Intelligence ranked HSBC as Europe's second-largest bank at end-2025 ($3.212tn), narrowly behind BNP Paribas ($3.279tn) — a reversal from end-2024, when HSBC ranked first in Europe by the same measure. *[Source: S&P Global Market Intelligence, European bank rankings]* This case study treats the asset ranking as a snapshot rather than a settled fact, since it is date-sensitive and sourced to a third-party aggregator rather than HSBC's own disclosure; HSBC's own descriptor states only that, "with assets of US$3,233bn at 31 December 2025, HSBC is one of the world's largest banking and financial services organisations" — a claim this case study can confirm from HSBC's own reported total-assets figure without needing the comparative ranking to hold.

**Strategic rationale for AI investment, in HSBC's own words.** At the same FY2025 results call, Elhedery named generative AI as the bank's single largest new-technology investment: "If you ask me, 'Where is the biggest investment going into the new technology today,' it is definitely going into generative AI." *[Source: HSBC Annual Results 2025 Announcement — Edited Transcript, 25 Feb 2026]* This statement, together with the organisational-simplification rationale above, frames the operational problem the next section addresses: a bank that has explicitly named its own structural duplication as a problem to be solved, and has explicitly named generative AI — not any other technology category — as its largest current investment in addressing it.

---

## 2. The Operational Problem

HSBC has been explicit, in its own words, about the shape of the problem it is addressing — and it is worth being precise about which problem, because this case study documents two related but distinct ones that should not be read as a single narrative.

**The first problem is organisational: duplicated processes and decision-making layered across a large, complex bank.** HSBC's own 22 October 2024 restructuring announcement named this directly, stating the changes "will reduce the duplication of processes and decision making that are built into the current structure." *[Source: HSBC "Simplified organisational structure to accelerate strategic execution," 22 October 2024]* This is an organisational-design problem, and HSBC's stated response to it — the segment restructuring into four businesses effective 1 January 2025, and the associated $1.5 billion annualised simplification-savings target — is a headcount and organisational-design intervention, not an AI deployment. Section 5.3 of this case study returns to the $1.5bn/$1.2bn simplification figures on their own terms, kept separate from the AI-coding narrative below, consistent with this series' practice at CommBank of not fusing a labor-cost story with a technology story unless a primary source actually connects them.

**The second problem is technical: a legacy application estate large enough that HSBC has set a multi-year target for shrinking it.** HSBC's own FY2025 disclosures quantify this directly. On the Annual Results 2025 call, Elhedery described the estate in rounded, spoken terms: the bank runs approximately 9,000 applications, of which roughly 3,000 are flagged for demise between 2025 and 2028. *[Source: HSBC Annual Results 2025 Announcement — Edited Transcript, 25 Feb 2026]* HSBC's own investor presentation gives the precise, published figures: 1,165 non-strategic applications demised in 2025 alone, representing c.36% progress toward the 2025–2028 target. *[Source: HSBC Annual Results 2025 Presentation to Investors and Analysts, Slide 4, footnote 4: "Gross application demise"]* This case study uses HSBC's own published "c.36%" rather than deriving a percentage from the 1,165 and "about 3,000" figures independently — the CEO's spoken "about 3,000" is a rounded approximation, and recalculating from it (1,165 ÷ 3,000 ≈ 38.8%) produces a number that disagrees with HSBC's own stated progress figure without adding any real precision.

**Why this technical estate matters for the coding-assistant story specifically.** A legacy estate of this scale is precisely the kind of environment in which engineering time is disproportionately consumed by maintenance, patching, and migration work rather than new development — the same structural shape this series has documented in other institutions' claims-and-disputes back offices, applied here to software engineering itself rather than customer-facing operations. HSBC has not published a figure quantifying what share of engineering time, pre-AI-assistant, went to this kind of maintenance work specifically; this case study does not manufacture one. What HSBC has published is the outcome side of that equation — the coding-assistant productivity figures discussed in Section 3 — and this case study treats those figures as a downstream signal of the underlying maintenance burden, not direct proof of its size, the same evidentiary posture this series took toward Lemonade's LAE ratio as a proxy for claims volume rather than a volume figure itself.

**It is worth being precise about what this section does not claim.** It does not claim that HSBC's coding assistants were deployed specifically to address the legacy-application-demise target — no primary source connects the two initiatives that directly, and this case study does not construct that connection on HSBC's behalf. It does not claim the organisational-simplification programme and the technology-simplification programme are the same effort — they are reported through different disclosures (the restructuring announcement and analyst commentary for the former; the investor-presentation slide deck for the latter) and pursue different targets (headcount/role-duplication savings versus application-count reduction). And it does not claim a specific volume of code, tickets, or engineering requests comparable to the disputes-per-day or claims-per-day figures this series has documented at CommBank and Lemonade — HSBC has not disclosed one, and this case study states that absence directly rather than filling it.

---

## 3. The AI Systems: Coding Assistants and a Separately-Named Agentic System

### 3.1 What's Confirmed — The Coding Assistants

HSBC CEO Georges Elhedery, on the FY2025 Annual Results call, described HSBC's generative AI rollout and its coding-specific subset in his own words: "we're making Generative AI available to all our colleagues in time – 85% mostly now enabled." He continued: "They will have coding assistants, or vibe coding assistants for those among our engineers – 31,000 already enabled." *[Source: HSBC Annual Results 2025 Announcement — Edited Transcript, 25 Feb 2026]* Two things are worth being precise about in these two sentences. First, "85% mostly now enabled" is Elhedery's own qualifier — HSBC is describing a rollout still in progress, not a completed state, and this case study preserves that qualifier rather than flattening it to a simple "85% have access." Second, "vibe coding" is genuinely Elhedery's own spoken phrase, but it does not appear in quotation marks in HSBC's own transcript — it is a colloquial aside describing the coding assistants, not a formal, branded HSBC product name, and this case study treats it accordingly.

**The 31,000 figure and an earlier, lower figure are reconciled as the same rollout at two points in time, not a contradiction.** HSBC's own "Transforming HSBC with AI" corporate webpage states: "More than 20,000 developers are using coding assistants, enabling a 15% efficiency in time spent coding." *[Source: HSBC "Transforming HSBC with AI" corporate page]* The same page dates its own content to the first half of 2025, noting "During 1H25... we embedded AI Review Councils across the organisation." Read against the FY2025 call's 31,000 figure — given roughly six to eight months later — this case study treats 20,000+ as an earlier checkpoint in a scaling rollout and 31,000 as the more current figure, rather than as two competing HSBC claims about the same population at the same time. This reconciliation carries one caveat worth stating plainly: HSBC's webpage carries no independently verifiable "last updated" timestamp, so the growth-over-time reading, while the best available explanation, is not a certainty — this case study states that limitation rather than presenting the reconciliation as settled beyond doubt.

The confirmed productivity outcomes attached to the coding assistants are two distinct, uncombined metrics: "We're seeing 60% speeding up in our unit testing. We're seeing five times faster patching of vulnerabilities in code thanks to all these capabilities." *[Source: HSBC Annual Results 2025 Announcement — Edited Transcript, 25 Feb 2026]* This case study keeps these separate, as HSBC itself does, and does not compound a "5x and 60%" figure into a single compounded productivity claim. It is also worth noting precisely: it is "five times faster," not "up to five times faster" — a minor embellishment that appears in at least one piece of secondary coverage and is not present in HSBC's own words.

HSBC's own "Transforming HSBC with AI" page adds one further confirmed, current-tense detail specific to the segment this case study is anchored on: "In Corporate and Institutional Banking, we've deployed a generative AI assistant to our servicing teams that supports 3 million client interactions annually, reducing turnaround times and improving experience – with 88% of clients rating us easy to deal with." This is a client-servicing tool, not the coding assistant, and this case study treats it as a separate, adjacent confirmed system within CIB rather than folding it into the coding-productivity narrative.

**One disclosure gap worth naming directly:** HSBC has not published its total engineering headcount anywhere in the materials reviewed for this case study, so "31,000 already enabled" cannot be expressed as a percentage of HSBC's engineering population — only as an absolute count. This case study does not estimate a denominator or a percentage, consistent with its practice elsewhere of stating a gap rather than filling it.

### 3.2 What's Not Disclosed — No Autonomous Code-Agent Workflow

No HSBC primary source describes an autonomous workflow in which an AI agent independently monitors the codebase, retrieves context, and drafts patches for human approval. HSBC's own language throughout describes the coding assistants as tools engineers use — assistive, human-driven productivity aids — rather than as agents operating with independent initiative over the codebase. This case study does not construct such a workflow, consistent with this series' practice at CommBank and Lemonade of stating a mechanism gap directly rather than filling it with a plausible-sounding architecture.

HSBC has, separately, articulated a general, bank-wide governance principle for AI deployments: "we are doing this with safety and security at the forefront. We're doing this in a way that we can review, monitor and audit everything we're doing in the space as a critical standard, and we're doing this in a way to keep controls, resilience and human accountability always there because we are a regulated industry and our customers' trust is the most important asset." *[Source: HSBC Annual Results 2025 Announcement — Edited Transcript, 25 Feb 2026, Georges Elhedery]* This is a genuine, on-the-record governance commitment — but it is stated at the level of AI deployments generally, not as a code-specific approval gate for the coding assistants in particular, and this case study does not present it as the latter.

### 3.3 The Separately-Named Agentic System: Financial Crime, Not Coding

HSBC's public record supports treating "agentic AI" as a term the bank has used for a different, later, and separately-announced use case: financial-crime detection, built with Google Cloud. On 17 June 2026, at the Google Cloud Summit London, HSBC and Google Cloud announced a multi-year partnership giving HSBC access to Gemini models and the Gemini Enterprise Agent Platform. The financial-crime framing was explicit: HSBC and Google Cloud describe an intent to "deploy generative AI and agentic AI to build a financial crime architecture that detects risk at an earlier stage... intervene twice as fast when risk is detected – including across the near one billion transactions the bank monitors for signs of financial crime every month." *[Source: HSBC / Google Cloud media release, 17 June 2026]*

**This distinction is an inference from HSBC's own terminology, not a direct HSBC statement that the coding tools are non-agentic.** No HSBC source explicitly says "our coding assistants are not agentic AI." What the record does show is that HSBC uses the term "agentic AI" specifically in connection with the Google Cloud financial-crime partnership, and does not use it in connection with the coding assistants anywhere in the FY2025 earnings-call material or HSBC's own AI webpage. This case study treats that as a meaningful pattern in HSBC's own language, not as an explicit HSBC claim, and labels it accordingly.

It is also worth being precise about timing: the FY2025 earnings call (25 Feb 2026), where the coding-assistant figures were disclosed, predates the Google Cloud/Gemini partnership announcement (17 June 2026) by roughly four months. HSBC has not, in any single disclosure this case study identified, discussed the coding assistants and the financial-crime agentic system together, or drawn an explicit contrast between them. The contrast this case study draws is therefore an analytical one, built by reading two separate HSBC disclosures against each other — not a distinction HSBC itself has stated in one place.

**A predecessor system exists and should not be conflated with the 2026 Gemini partnership.** HSBC's financial-crime collaboration with Google predates the Gemini partnership by five years: a 2021 pilot known internally as Dynamic Risk Assessment (DRA), built on Google Cloud's AML AI. HSBC's own account states: "We're finding two to four times more financial crime than we did previously... Now, we have 60% fewer false positive cases." *[Source: HSBC, "Harnessing the power of AI to fight financial crime"]* This case study names DRA as prior art — a genuine, earlier, and distinct HSBC-Google financial-crime system — rather than treating the 2026 Gemini partnership as HSBC's first venture into this space.

**One further discrepancy is carried forward rather than resolved.** HSBC's own release describes monitoring "near one billion transactions" monthly for signs of financial crime; Google Cloud's own coverage of the same partnership cites "more than 1.2 billion transactions each month." *[Source: artificialintelligence-news.com coverage of the Google Cloud/HSBC announcement]* These are two different entities describing the same partnership with two different numbers. This case study states both, attributed to their respective sources, rather than picking one as authoritative.

---

## 4. Illustrated Workflow: An Engineer Patching a Flagged Vulnerability

> **IMPORTANT: This workflow is an illustrative scenario constructed for demonstration purposes.**
> The confirmed functions this illustration is built from — engineers using a coding assistant to write and revise code faster, including faster identification and patching of vulnerabilities (Section 3.1) — are sourced to HSBC's FY2025 Annual Results call. Everything else below — the named engineer, the specific scenario, and the sequencing between steps — is this case study's own construction, built to be consistent with, and no richer than, what Section 3 establishes as confirmed.
>
> **This workflow does not include an autonomous code-agent step.** As Section 3.2 states directly, no HSBC source describes an agent independently monitoring the codebase, retrieving context, and drafting patches for approval. This illustration keeps the human engineer as the actor at every step, with the coding assistant as a tool the engineer invokes and reviews — not as an independent actor in its own right. This is the same discipline this series applied at Lemonade in declining to invent a dollar threshold for AI Jim's settlement authority: where HSBC has not disclosed a mechanism, this illustration does not construct one.
>
> The step sequence below has been reconciled against a working reference implementation (Section 4b). The reference implementation goes a step further than the illustration below: rather than merely omitting an invented approval criterion from the narrative, its Human Review Gate contains no default at all — not even a labeled placeholder — and requires a real, externally supplied decision function before it will apply or reject anything.

### The Scenario

An HSBC software engineer, referred to here as "Priya," working within Corporate and Institutional Banking's technology function, receives an automated alert that a known vulnerability pattern has been flagged in a piece of legacy code she maintains.

### Phase 1: Identification and Assisted Patching

**Step 1 — Vulnerability Flagged.** An existing code-scanning or security-monitoring process (not itself part of the coding assistant, and not detailed in any HSBC disclosure reviewed for this case study) surfaces a vulnerability in code Priya is responsible for. *(CONSTRUCTED: HSBC has not disclosed what triggers this flag or what tool performs the scan; this case study assumes only that some flagging mechanism precedes the assistant's involvement, since HSBC's own "5x faster patching" language describes patching speed, not vulnerability discovery.)*

**Step 2 — Priya Invokes the Coding Assistant.** Priya opens her coding assistant and asks it to help understand the flagged code and draft a fix. The assistant analyzes the relevant code and proposes a patch. *(CONSTRUCTED: the specific interaction pattern — what Priya types, what context the assistant retrieves, how a "vibe coding" session is actually structured — is not disclosed by HSBC in any technical detail; this case study infers only that some assistant-driven drafting step exists, consistent with Elhedery's description of "coding assistants... for those among our engineers.")*

**Step 3 — Priya Reviews the Proposed Patch.** Priya reviews the assistant's proposed fix against her own understanding of the codebase and the vulnerability. This step is the human-accountability point this illustration preserves deliberately: HSBC's own governance language states a commitment to "keep controls, resilience and human accountability always there," and this illustration reflects that by keeping Priya, not the assistant, as the party who accepts or rejects the proposed change. *(CONSTRUCTED: HSBC has not disclosed a specific review protocol, sign-off requirement, or approval gate specific to coding-assistant-drafted changes; this illustration reflects the bank-wide governance principle in general terms only, per Section 3.2's finding that no code-specific approval gate is documented.)*

**Step 4 — Patch Applied and Tested.** Priya applies the reviewed patch and runs unit tests, which — consistent with HSBC's own confirmed 60% unit-testing speed-up figure — complete faster than they would without the assistant's involvement in the surrounding development workflow. *(CONSTRUCTED: HSBC has not disclosed whether the unit-testing speed-up applies to this specific patching scenario or to unit testing generally across engineering work; this illustration applies the confirmed aggregate figure to this scenario as a reasonable but unconfirmed extension.)*

### Phase 2: Deployment

**Step 5 — Patch Deployed via Normal Change-Management Process.** The patched code moves through HSBC's existing software release and change-management process — a process this case study does not describe in any detail, since HSBC has not disclosed one specific to AI-assisted code changes. This illustration ends here deliberately, rather than continuing into a deployment-approval workflow HSBC has not described.

**What this illustration does not include:** an autonomous agent independently identifying the vulnerability without a prior flag; an agent drafting and submitting a patch without Priya's review; a disclosed, code-specific approval gate distinct from HSBC's general AI-governance principle; or any claim about how much of the "5x faster" figure is attributable to any single step above rather than to the coding assistant's overall effect on Priya's workflow.

### Workflow Summary: What the Tool Did vs. What the Human Did

| Step | Actor | Action |
|---|---|---|
| Vulnerability flagged | Existing scanning process (undisclosed mechanism) | Precedes assistant involvement; not part of the coding-assistant system per HSBC's own disclosures |
| Analyze code, draft proposed patch | Coding assistant | Assistive — HSBC confirms engineers use assistants for this; specific interaction mechanics are CONSTRUCTED |
| Review proposed patch | Human (Priya) | Required — this is the human-accountability point HSBC's general governance language supports, though no code-specific approval gate is disclosed |
| Apply patch, run tests | Human (Priya), with assistant-linked tooling | Testing speed-up (60%) is HSBC-confirmed as an aggregate figure; its application to this specific step is CONSTRUCTED |
| Deploy via change management | Human process (undisclosed detail) | Not described by HSBC in AI-specific terms; this illustration ends here rather than inventing detail |

---

## 4b. Reference Implementation

A working reference implementation now accompanies this case study, following the same pattern as the CommBank, Klarna, and Lemonade entries in this series: a companion technical artifact grounding the confirmed functions described in Sections 3.1 and 4, built and tested — not merely planned or described. It runs entirely on fabricated mock data and a deterministic, canned stand-in for a real coding assistant, with no external services, credentials, or HSBC systems involved anywhere in the repository.

**Architecture.** Consistent with the standard this series has applied elsewhere, the implementation is a single, linear pipeline — **Intake → Assistant → Human Review Gate → Apply & Test**, run by an orchestrator that executes the four stages in strict, fail-fast sequence — not a multi-agent system. This matches what HSBC's public record actually supports: a single coding-assistant capability with a small number of confirmed functions, not a documented multi-component architecture.

**What's confirmed** (sourced to HSBC's FY2025 Annual Results Announcement, per Section 3.1): engineers use coding assistants to draft and revise code; vulnerability patching is reported five times faster and unit testing 60% faster, as two distinct, uncombined figures; HSBC states a general, bank-wide human-accountability governance principle for AI deployments.

**What's deliberately absent — the Human Review Gate.** This is the repository's central design decision, and it follows the same pattern this series used for Lemonade's Authorization Gate. Every other undisclosed mechanism in this pipeline received an illustrative construction, clearly labeled. The Human Review Gate did not: per Section 3.2's finding that no HSBC source describes a code-specific approval gate — only a general governance principle — the Gate ships with **zero default review criteria**, under no label, anywhere in the codebase. It raises an error at construction if no external decision function is supplied, and it settles or rejects a patch purely based on whatever that function returns. Inventing a labeled placeholder here (for instance, "auto-approve low-severity fixes") would have implied a shape of answer — that HSBC's review process is severity-based — that nothing in the public record supports. This is the clearest engineering expression of this case study's own finding in Section 6.1: rich outcome disclosure, thin mechanism disclosure.

**What's constructed, labeled `[DEV]`:** the minimal required fields for a vulnerability report to enter the pipeline (an id, a file path, a description) — HSBC discloses no vulnerability-report schema; and the deterministic canned patch draft standing in for a real coding-assistant call — HSBC discloses no model, vendor, or prompt structure underlying its own tools.

**Test coverage.** The suite comprises 15 tests across 5 files, run in full before the repository was considered finished. **Result: 15 tests, 15 passing, 0 failing.** Several tests use mock/spy assertions to prove sequencing directly — confirming that an incomplete vulnerability report escalates before the coding assistant is ever invoked, and that a rejected review halts before the patch-and-test step is ever called, rather than assuming the fail-fast property holds from the design description alone. The Human Review Gate's own tests verify a contract, not a business rule: they confirm the Gate honors whatever its supplied decision function returns, and do not, because they cannot, test what should approve a patch in the first place — HSBC discloses no such criteria.

**Known limitations**, per the repository's own README: no real vulnerability scanner, LLM, or code-execution environment is used anywhere; the "5x faster" and "60% faster" figures are HSBC's own reported aggregates, cited in this case study, and are not reproduced, measured, or simulated by the repository; the suite uses Python's standard-library `unittest`, consistent with this series' prior reference implementations; and the repository models one vulnerability report's path through the pipeline, not throughput or concurrent processing at any real HSBC scale.

**Explicit non-claims.** This repository is not a disclosure of HSBC's actual coding-assistant or code-review infrastructure. It does not claim to replicate HSBC's tooling, model choice, review process, or timing figures, and should not be cited as evidence of HSBC's technical architecture. It is built from what HSBC has publicly confirmed plus explicitly labeled construction everywhere the public record stops, with the Human Review Gate's total absence of default criteria standing as the clearest expression of where that record actually ends.

---

## 5. Documented Results

This section presents four separate, HSBC-sourced result sets, kept deliberately apart rather than combined into a single "AI transformed HSBC" narrative — consistent with this series' finding at CommBank that distinct initiatives, reported at different times for different purposes, should not be read as one story simply because they share a company and a time period.

### 5.1 Coding-Assistant Productivity

HSBC's confirmed, dated figures are: 60% faster unit testing, and five times faster patching of vulnerabilities in code, both attributed by Elhedery directly to the coding-assistant rollout: "We're seeing 60% speeding up in our unit testing. We're seeing five times faster patching of vulnerabilities in code thanks to all these capabilities." *[Source: HSBC Annual Results 2025 Announcement — Edited Transcript, 25 Feb 2026]* No further breakdown — by team, by application, by seniority of engineer, or by baseline measurement methodology — is disclosed. This case study does not estimate what "faster" is measured against, since HSBC has not stated a specific baseline.

### 5.2 Legacy Application Estate Reduction

HSBC demised 1,165 non-strategic applications in 2025, representing c.36% progress toward its 2025–2028 target of demising approximately 3,000 applications — HSBC's own published figures, not a derived calculation. *[Source: HSBC Annual Results 2025 Presentation to Investors and Analysts, Slide 4, footnote 4: "Gross application demise"]* This case study does not attribute this reduction to the coding assistants specifically; Section 2 already states that no primary source connects the application-demise target to the coding-assistant deployment, and this section does not construct that connection here either.

### 5.3 Organisational Simplification Savings

HSBC realized $1.2 billion in annualized organisational-simplification savings by year-end 2025, ahead of an original $1 billion target for the same date. CFO Pam Kaur: "We have taken actions to realise $1.2 billion of annualised simplification savings with an immaterial revenue impact. This is ahead of our original timeline of $1 billion by the year end 2025." *[Source: HSBC Annual Results 2025 Announcement — Edited Transcript, 25 Feb 2026, Pam Kaur]* This programme's full annualized target is $1.5 billion, now expected to be actioned by the first half of 2026 — six months ahead of the original end-2026 schedule. *[Source: same]* This figure is tied by HSBC to headcount and role-duplication reduction, not to the application-demise programme in 5.2 above; the two remain separate initiatives in HSBC's own reporting, and this case study preserves that separation rather than summing them into a single "simplification total."

### 5.4 Severance and Restructuring Cost

HSBC's own FY2024 results disclosed the cost side of the simplification effort: "We expect to incur around $1.8 billion of severance and other up-front costs by the end of 2026. The bulk of these costs will be incurred this year." *[Source: HSBC Annual Results 2024 Announcement — Edited Transcript, 19 Feb 2025, Georges Elhedery]* As stated in this case study's brief-rebuild phase, this is the only $1.8bn figure this case study uses; a separate, unrelated $1.8bn figure appears in HSBC's FY2025 materials describing cost reallocation tied to the Hang Seng Bank privatisation, and that figure is deliberately excluded from this entry to avoid conflating two unrelated numbers that happen to share a dollar amount. A partial, dated data point on realized severance cost exists: HSBC's 9M25 Form 6-K states "During 9M25, we incurred $0.8bn in costs in relation to our organisational simplification, primarily related to severance." *[Source: HSBC Form 6-K, 9M25]*

### 5.5 Reading These Four Results Together

None of the four figures above is a measure of the same thing, and none should be read as corroborating another. The coding-assistant metrics (5.1) describe engineering-workflow speed. The application-demise figures (5.2) describe technical-debt reduction. The simplification-savings figure (5.3) describes headcount and role-duplication cost reduction. The severance figure (5.4) describes the upfront cash cost of achieving 5.3. A reader could reasonably ask whether AI-driven engineering productivity contributed to headcount reduction, application demise, or both — but HSBC has not stated that connection in any disclosure this case study identified, and this case study does not construct it. This is the same posture this series took toward CBA's fraud-loss and call-center-wait-time figures: real, HSBC's own numbers, sitting alongside rather than proving anything about the AI systems this case study documents.

---

## 6. Limitations, Failures, and Honest Caveats

### 6.1 Thin Mechanism Disclosure Behind Rich Outcome Figures

Consistent with a pattern this series has now documented at Lemonade, HSBC discloses outcome metrics for its coding assistants with real precision — 60% faster unit testing, five times faster vulnerability patching, 31,000 engineers enabled — while disclosing almost nothing about mechanism. No HSBC source states what tool or tools underlie the coding assistants, what model or models power them, what the "vibe coding" workflow actually consists of step-by-step, or what baseline the productivity figures are measured against. This case study's illustrated workflow in Section 4 is explicit about being a construction for exactly this reason: HSBC's own disclosure stops well short of a documented architecture, and this case study does not fill that gap with invented technical detail.

### 6.2 An Unresolved (But Reconciled) Developer-Count Discrepancy

Section 3.1 reconciles a "more than 20,000 developers" figure (from HSBC's "Transforming HSBC with AI" page, self-dated to 1H25) against a later "31,000 already enabled" figure (FY2025 Annual Results call, 25 Feb 2026) as the same population measured at two points in a scaling rollout. This case study treats that reconciliation as the best available reading, not as a certainty: the webpage carries no independently verifiable "last updated" timestamp, and it remains possible, though this case study finds it less likely, that the two figures reflect different scopes (e.g., "developers" versus "engineers," or different tool populations) rather than the same rollout at different times. A reader relying on either figure alone should know the other exists and should treat both as HSBC's own numbers rather than picking one as more authoritative without this context.

### 6.3 The "Agentic AI" Distinction Is an Inference, Not an HSBC Statement

This case study's central organizing distinction — that HSBC's coding assistants are assistive tools while "agentic AI" is a term HSBC reserves for its Google Cloud financial-crime partnership — is built by reading two separate HSBC disclosures against each other, made roughly four months apart, that HSBC itself has never presented side by side. No HSBC source explicitly states "the coding assistants are not agentic AI." This case study labels this distinction as an inference throughout rather than presenting it as a direct HSBC claim, and a future HSBC disclosure could, in principle, describe the coding assistants in agentic terms without contradicting anything currently on the public record — this case study's distinction would then need revision, not defense.

### 6.4 The $1.8 Billion Figure: A Documented Case of Same-Number, Different-Meaning Risk

This case study's most significant sourcing correction, made during its brief-rebuild phase, concerns the $1.8 billion figure. HSBC's FY2024 results (19 Feb 2025) disclosed $1.8bn in expected severance and up-front restructuring costs through 2026 — the figure this case study uses throughout Section 5.4. HSBC's FY2025 results (25 Feb 2026) separately use "$1.8 billion" for an unrelated cost-reallocation figure tied to the Hang Seng Bank privatisation. This case study made a deliberate editorial decision to use only the FY2024 severance figure and to exclude the FY2025 reallocation figure from this entry entirely, rather than present both side by side — on the reasoning that introducing a second $1.8bn figure only to immediately distinguish it from the first still risks a reader retaining "$1.8bn" attached to the wrong meaning or the wrong year. Secondary coverage reviewed for this case study (kingy.ai, metaintro.com) has independently conflated the $1.8bn severance/restructuring figure with "AI investment" — a fabricated-connection failure mode this case study does not repeat, and one that underscores why the underlying figure needed careful handling in the first place.

### 6.5 No Disclosed Connection Between the AI-Coding Story and the Cost/Headcount Story

As stated in Section 5.5, HSBC has not disclosed any causal or quantified connection between its coding-assistant productivity gains and either its organisational-simplification savings or its legacy-application-demise progress. A reader could reasonably hypothesize that engineering-productivity gains from AI tooling free up capacity that in turn supports headcount reduction or faster application decommissioning — but this is a plausible inference this case study explicitly declines to make on HSBC's behalf, since no primary source states it. This is a narrower version of the conflation risk this series names at CommBank: rather than two systems being fused into one false narrative by secondary coverage, this is a case where a reader might supply a connecting narrative HSBC itself has never offered, and this case study states that gap directly rather than leaving it for a reader to fill in unassisted.

### 6.6 Speculative Secondary-Press Figures Not Repeated Here

At least one piece of secondary financial press (Zacks, reporting on Bloomberg's initial account) describes HSBC as "evaluating up to 20,000 job cuts, 10% of its workforce, tied to AI-driven transformation plans," explicitly framed as an early-stage, undecided review rather than a confirmed HSBC plan. This case study does not present that figure as an HSBC-confirmed outcome, consistent with the standard this series applies to unconfirmed or speculative figures circulating around a company's AI story.

### 6.7 Self-Reported, Unaudited Figures

Every quantitative figure in Section 5 — the 60%/5x coding metrics, the 1,165/c.36% application figures, the $1.2bn simplification savings, and the $1.8bn severance figure — originates in HSBC's own earnings calls, investor presentations, or SEC filings. None has been independently audited or verified by a third party for the purposes of this case study, and no published methodology accompanies any of them beyond the definitions HSBC itself provides. This case study presents these as HSBC's own numbers, not as independently confirmed facts about engineering-team accuracy, code quality, or the real-world security impact of faster patching — none of which HSBC has disclosed.

---

## 7. Forward-Looking: HSBC in the Agentic Era

> **Editorial analysis.** This section draws on publicly stated positions and should be read as informed projection, not documented fact.

HSBC's own public statements through mid-2026 point toward continued, rather than diminished, investment in AI across both halves of the story this case study has kept separate. Elhedery's framing at FY2025 results — generative AI as the bank's single largest current technology investment — sits alongside a June 2026 financial-crime partnership that explicitly uses the term "agentic AI" for the first time in this case study's reviewed record, and a December 2025 partnership with Mistral AI for self-hosted frontier models, scoped out of this entry per Section 1 but signaling continued expansion in HSBC's AI infrastructure. The appointment of David Rice as HSBC's first Chief AI Officer, effective 1 April 2026, drawn directly from his prior role as COO of the CIB segment this case study is anchored on, suggests HSBC is formalizing AI governance and strategy at a senior organizational level rather than treating it as a distributed, ad hoc initiative.

Whether HSBC's coding assistants will eventually be described in agentic terms — whether an autonomous code-agent workflow of the kind explicitly absent from Section 3.2 will emerge as a disclosed capability — is not indicated anywhere in the public record as of this case study's writing. It is a plausible direction, given the rapid pace of AI-coding-tool development across the industry generally, but it remains this case study's own speculation, not a confirmed HSBC roadmap item, and should be flagged as such rather than presented as likely.

The more durable observation, and the one this case study's Section 6 findings support most directly, is that HSBC's disclosure pattern across these two stories — precise, dated outcome metrics for the coding assistants, and a genuinely separate, later-announced, explicitly agentic system for financial crime — is itself a distinction worth a reader tracking forward. Whether HSBC eventually narrows the mechanism-disclosure gap identified in Section 6.1, either for the coding assistants or for the financial-crime agentic system, is not indicated in the public record reviewed for this case study. It is a plausible direction for a bank under continued investor scrutiny of its AI-driven simplification narrative, but it remains speculation, not a confirmed roadmap item, and this case study does not attempt to resolve it either.

---

## Sources

| Source | Type | Notes |
|---|---|---|
| HSBC Holdings plc — Annual Results 2025, media release | Primary | 25 February 2026. Total assets, revenue, profit before tax, notable items, RoTE, segment data |
| HSBC Holdings plc — Annual Results 2025, Announcement — Edited Transcript | Primary | 25 February 2026, Georges Elhedery. Simplification-programme quotes, generative AI investment statement |
| HSBC Annual Report and Accounts 2025 | Primary | Headcount (208,720 FTE), corporate identity detail |
| HSBC "Our markets" / "About HSBC" corporate pages | Primary | Customer count, country/territory count, home-market descriptor |
| HSBC — "Simplified organisational structure to accelerate strategic execution" | Primary (SEC filing) | 22 October 2024. Restructuring rationale, quoted directly |
| Reuters / Banking Dive coverage of 29 October 2024 analyst remarks | Secondary, reporting named-executive on-record remarks | Elhedery's "simplify the bank and remove duplication of roles" quote |
| Bloomberg | Secondary/major financial press | 27 January 2026. $300bn market-cap milestone |
| S&P Global Market Intelligence | Secondary (aggregator) | European bank asset-ranking snapshot, end-2025 vs end-2024 |
| HSBC / CIO Dive coverage of Chief AI Officer appointment | Primary (HSBC) / Secondary (CIO Dive) | 23 March 2026. David Rice's prior CIB COO role |

**Section 2 additional sources:**

| Source | Type | Notes |
|---|---|---|
| HSBC — "Simplified organisational structure to accelerate strategic execution" | Primary (SEC filing) | 22 October 2024. "Duplication of processes and decision making" quote |
| HSBC Annual Results 2025 Announcement — Edited Transcript | Primary | 25 Feb 2026. Elhedery's spoken ~9,000/~3,000 application figures |
| HSBC Annual Results 2025 Presentation to Investors and Analysts | Primary | Slide 4. 1,165 apps demised / c.36% progress figures |

**Section 3 additional sources:**

| Source | Type | Notes |
|---|---|---|
| HSBC "Transforming HSBC with AI" corporate page | Primary | 20,000+ developers figure (dated to 1H25 context); CIB client-servicing AI assistant (3M interactions/year, 88% ease rating) |
| HSBC / Google Cloud media release | Primary | 17 June 2026. "Agentic AI" financial-crime framing, Gemini Enterprise Agent Platform, "near one billion transactions" |
| HSBC, "Harnessing the power of AI to fight financial crime" | Primary | Dynamic Risk Assessment (DRA), 2021 pilot with Google — predecessor to the 2026 Gemini partnership |
| artificialintelligence-news.com coverage of HSBC/Google Cloud announcement | Secondary | "More than 1.2 billion transactions" figure — Google Cloud's own count, differing from HSBC's "near one billion" |

**Section 4 additional sources:**

| Source | Type | Notes |
|---|---|---|
| HSBC Annual Results 2025 Announcement — Edited Transcript | Primary | 25 Feb 2026. Source of all confirmed functions this illustration draws from; no source beyond this for mechanism detail |
| This case study's own construction | Not a HSBC source | Scenario, named engineer, and step sequencing are illustrative only, per the boxed note above |

**Section 5 additional sources:**

| Source | Type | Notes |
|---|---|---|
| HSBC Annual Results 2024 Announcement — Edited Transcript | Primary | 19 Feb 2025. Source of the $1.8bn severance/restructuring figure used in this entry |
| HSBC Form 6-K, 9M25 | Primary (SEC filing) | $0.8bn realized severance cost through 9M25 |

**Section 6 additional sources:**

| Source | Type | Notes |
|---|---|---|
| kingy.ai | Secondary — reviewed and found to conflate figures | Fuses $1.8bn severance/restructuring with "AI investment," not supported by any HSBC source |
| metaintro.com | Secondary — reviewed and found to conflate figures | Same $1.8bn/AI-investment conflation; also source of the speculative 20,000-job-cut figure |
| Zacks (reporting on Bloomberg) | Secondary, explicitly framed as early-stage/speculative | "Evaluating up to 20,000 job cuts... tied to AI-driven transformation plans" — not presented as HSBC-confirmed |

**Section 7 additional sources:**

| Source | Type | Notes |
|---|---|---|
| HSBC / Google Cloud media release | Primary | 17 June 2026. First reviewed use of "agentic AI" terminology by HSBC |
| The Register, "HSBC partners with Mistral AI" | Secondary | 1 December 2025. Mistral partnership announcement, scoped out of this entry per Section 1 |
| HSBC / CIO Dive coverage of Chief AI Officer appointment | Primary (HSBC) / Secondary (CIO Dive) | 23 March 2026. David Rice's appointment, effective 1 April 2026 |
| HSBC Coding-Assistant Vulnerability-Patch Pipeline — Reference Scaffold (companion repository README) | This case study's own artifact, not an HSBC source | Built and tested (15/15 passing); documents its own confirmed/constructed/deliberately-absent boundaries per Sections 4/4b above |

---

*This case study is part of the series: Agentic AI Adoption in Financial Services (2025–2026). Illustrative workflow scenarios are clearly labeled and constructed from publicly disclosed functional details. No proprietary HSBC operational data is claimed or represented.*

*This entry's structural finding: HSBC's coding-assistant productivity story and its separately-announced, explicitly "agentic" financial-crime system are genuinely distinct disclosures, made months apart, that this case study connects only as an analytical contrast — not one HSBC has drawn itself.*
