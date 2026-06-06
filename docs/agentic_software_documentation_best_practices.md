# Best Practices for Agentic Software Documentation

*Research synthesis, June 2026*

---

## The Core Problem: Why Conventional Documentation Fails

Traditional software documentation assumes deterministic execution. You describe what the code does, and it does that. Agentic systems break this contract in three ways: they pursue *goals* rather than follow procedures, they make decisions at runtime that aren't fully predictable from their configuration, and their behavior emerges from the interaction of prompts, models, tools, memory, and environment in ways no single document captures completely.

Research bears this out. One analysis found agents exhibiting up to 63% coefficient of variation in execution paths for identical inputs. The MIT 2025 AI Agent Index — which surveyed 30 deployed production agents across 1,350 data fields — found that most developers "share little information about safety, evaluations, and societal impacts," with transparency gaps especially pronounced in exactly the areas users most need to understand.

The documentation problem is not peripheral. It is how teams lose control of production agents, how regulators will scrutinize AI-Act compliance, and how the field will (or won't) develop shared accountability norms.

---

## The Emerging Standard Layer

### AGENTS.md: Documentation as Agent Context

The most significant documentation practice to emerge in the last year is **AGENTS.md**, released by OpenAI in August 2025 and now stewarded by the Agentic AI Foundation (AAIF) under the Linux Foundation. Think of it as a README for agents rather than humans: a markdown file that lives alongside a codebase and tells AI coding agents the conventions, build steps, testing requirements, and operational constraints they need to work reliably across different repositories.

Within months of release, it was adopted by over 60,000 open-source projects and integrated into GitHub Copilot, Cursor, Devin, VS Code, Gemini CLI, and others. The key design insight is that documentation *is* agent context — it's not separate from how agents behave, it shapes how they behave.

The AAIF (founded December 2025, with Anthropic, OpenAI, Block, AWS, Google, Microsoft, Cloudflare, Bloomberg as platinum members) now coordinates AGENTS.md, MCP, and Block's Goose framework as the backbone of an open agentic documentation and interoperability ecosystem.

### Agent Cards: Structured Capability Description

A parallel thread is **Agent Cards** — structured documentation artifacts that capture what an agent can do, how it's configured, what memory and tool integrations it has, what governance constraints apply, and what evaluation metrics it targets. An academic proposal from MICAI 2025 formalized Agent Cards as the agent-layer equivalent of Model Cards and Datasheets for Datasets, proposing them as a foundation for agent ledgers, audit bundles, and maturity frameworks.

Separately, Google's Agent-to-Agent (A2A) protocol — launched April 2025, now at v1.0 with 150+ organizational backers including Microsoft, AWS, Salesforce, SAP, and ServiceNow — specifies that agent cards be published at `/.well-known/agent-card.json`, making agent capability discovery machine-accessible following RFC 8615 standards. A2A v1.0 (released early 2026) added signed Agent Cards with cryptographic verification of agent identity.

### Policy Cards: Runtime Governance Documentation

Complementing capability documentation is a proposal for **Policy Cards** — machine-readable artifacts that encode operational, regulatory, and ethical constraints for agents at the deployment layer. Where Agent Cards describe *what an agent can do*, Policy Cards describe *what it must and must not do*. A 2025 paper proposed Policy Cards as an extension of existing transparency artifacts, with built-in crosswalk mappings to NIST AI RMF, ISO/IEC 42001, and the EU AI Act, and support for automated validation and continuous-audit pipelines.

### Arazzo: Workflow-Level Documentation

For multi-step API workflows, the **Arazzo Specification** (OpenAPI Initiative, v1.0.1 current) fills the gap between individual endpoint documentation and end-to-end workflow documentation. OpenAPI describes what each endpoint does; Arazzo describes how to sequence them into business-meaningful workflows with explicit inputs, outputs, success criteria, and step dependencies — in machine-readable YAML or JSON.

This matters for agents because an agent reading only OpenAPI docs must infer workflow intent. Arazzo makes workflows explicit and deterministic, improving both developer experience and agent reliability. Practitioners cite Arazzo as the answer to "how do agents know not just what tools exist, but in what order to use them." Tooling support in 2026 includes Redocly, Speakeasy, APIDog, and others.

---

## Documentation Types and What Each Requires

### System Prompt Documentation

System prompts are the behavioral core of most LLM-based agents, and they require their own documentation discipline separate from code. Best practices that have converged in production:

- **Version control with semantic meaning**: treat prompt changes the way you treat API version bumps. A change that alters refusal behavior or tool selection logic is a breaking change.
- **Change history with behavioral rationale**: not just *what* changed, but *why* and *what behavioral outcome was sought*. Rollback without rationale is blind rollback.
- **Behavioral test coverage**: prompt changes should trigger regression tests before deployment. Platforms like LangSmith, Braintrust, and PortKey now provide Git-based prompt versioning with evaluation hooks for exactly this.
- **Intent documentation**: what is this prompt trying to accomplish? What are the known edge cases? What behaviors were explicitly ruled out and why?

The non-determinism problem is acute here. Because prompts don't produce the same outputs for the same inputs, prompt documentation must describe *intended behavioral envelopes*, not expected outputs.

### Tool and Integration Documentation

Tool documentation for agents goes beyond standard API documentation. Beyond the function schema, agents need:

- **Authorization scope documentation**: what permissions does this tool require? What can it do that the agent should *not* be able to do even if technically possible?
- **Failure mode catalog**: what does this tool return when things go wrong? How should the agent interpret ambiguous returns?
- **Interaction constraints**: some tools have rate limits, ordering requirements, or idempotency properties that an agent reasoning about "what to do next" must understand.
- **Side effect documentation**: which tool calls are reversible? Which have real-world consequences that can't be undone?

MCP (Model Context Protocol, Anthropic, now AAIF-governed) has become the dominant standard for connecting agents to tools, with 10,000+ published MCP servers. MCP's schema-first design means tool documentation is built into the protocol layer — but the behavioral and constraint documentation on top of the schema still requires deliberate authorship.

### Workflow and Pipeline Documentation

For agentic pipelines with defined structure, the field has split into two camps:

**Deterministic subflows with agentic decision points**: the dominant production pattern is using DAG schedulers (Airflow, Temporal) for fixed pipeline segments and only allowing agents to branch where genuine judgment is required. This makes documentation tractable — you document the fixed structure in standard ways, and document the agent decision points with explicit criteria for what the agent is deciding and what acceptable outcomes look like.

**State-machine-style graphs**: tools like LangGraph make agent workflows into explicit state graphs that are themselves a documentation artifact. The graph is the specification. This is probably the most tractable approach for complex multi-agent systems: if the graph is readable, the workflow is documented.

Regardless of approach, workflow documentation needs: termination criteria (how does the agent know it's done?), fallback paths (what happens when a tool fails?), loop detection (what prevents infinite retry loops?), and human escalation triggers (what conditions require human involvement?).

### Decision Audit Trails

This is where documentation as a static artifact gives way to documentation as a runtime artifact. The observability tooling layer — LangSmith, MLflow, Langfuse, Arize, AgentOps — now treats structured execution traces as first-class documentation. A good trace answers: what did the agent decide at each step, what information it had, what tools it called and with what arguments, and what it did with the results.

OpenTelemetry (OTel) is emerging as the standard foundation for agent observability traces, providing portability across platforms. The practical implication: instrument from day one. Traces that aren't captured aren't recoverable, and for audit and compliance purposes, the absence of traces is itself a finding.

The deeper question — whether LLM-generated chain-of-thought constitutes genuine transparency or plausible-sounding post-hoc rationalization — remains unsettled. Treat traces as evidence of what the agent *did*, not necessarily proof of *why* it did it.

### Operational Runbooks

Agentic systems in production need runbooks that specifically address:

- **Intervention protocols**: how does a human override or pause an agent in flight? What state is preserved?
- **Behavioral drift detection**: how do you know if an agent's behavior has shifted from its documented baseline? What metrics trigger review?
- **Rollback procedures**: if a prompt change or model update degrades behavior, what's the path back?
- **Incident classification**: which agent failures are operational (tool timeout, API error) versus behavioral (agent took an action outside expected scope)?

---

## Observability as Documentation Infrastructure

The observability platforms have converged on a consistent model: every LLM call, tool invocation, retrieval step, and planning decision is a node in a structured trace tree. This trace is the primary documentation artifact for understanding what an agent actually did in production.

Key platforms and their positioning in 2026:
- **MLflow**: open-source, OpenTelemetry-native, full lifecycle platform; preferred for teams requiring data ownership
- **LangSmith**: deeply integrated with LangChain/LangGraph; adds evaluation and deployment management alongside tracing
- **Langfuse**: open-source with ClickHouse-native self-hosting option
- **Braintrust**: fast prototyping, strong for teams with non-technical stakeholders

The point worth emphasizing: these traces aren't just debugging tools. For regulated deployments, they are the audit trail. For multi-agent systems, they are the only artifact that captures what actually happened across agent boundaries.

---

## Regulatory and Compliance Dimension

The EU AI Act is the most significant external pressure on agentic documentation practices. Key milestones:
- **August 2025**: General-purpose AI model obligations took effect, including technical documentation and transparency requirements
- **August 2026** (weeks away): Full enforcement for high-risk systems, with penalties up to €35M or 7% global revenue

For agentic systems classified as high-risk (credit decisioning, HR screening, critical infrastructure, medical, law enforcement applications), the Act requires: continuous risk management documentation, human oversight mechanisms with intervention points, logging sufficient for post-hoc audit, and Annex IV technical documentation packages.

The Act's requirement that humans be able to "meaningfully oversee" an AI agent has no settled operational definition, but practitioners are interpreting it as: the documentation must be sufficient for a human reviewer to understand what the agent decided, why, and what alternatives it considered.

Finland became the first EU member state with full AI Act enforcement powers in December 2025. The August 2026 deadline is real.

NIST AI RMF and ISO/IEC 42001 provide complementary frameworks. Policy Cards (described above) specifically propose crosswalk mappings to these standards, enabling documentation artifacts to double as compliance evidence.

---

## The Transparency Gap in Practice

The MIT 2025 AI Agent Index finding is worth dwelling on: across 30 prominent deployed agents, the researchers found significant and consistent gaps in transparency about safety mechanisms, evaluation practices, and societal impact. This is the ground truth of current practice — most production agentic systems are not well-documented on the dimensions that matter most for accountability.

The reasons are predictable: safety and evaluation documentation is expensive to produce, confers competitive disadvantage when published, and there are currently no enforcement mechanisms requiring it (though the EU AI Act is changing this for high-risk applications).

For teams building agentic systems, this gap is both a risk (inadequate documentation creates operational and compliance exposure) and a signal about the state of practice (don't confuse the absence of published documentation for the absence of a documentation problem).

---

## Open Problems and Genuine Unsettled Questions

**Emergent multi-agent behavior**: how do you document behavior that arises from agent interactions that wasn't designed into any individual agent? No good answer exists. Current practice is to document the intended orchestration and treat observed emergent behavior as a testing and monitoring problem rather than a documentation problem.

**Non-determinism in documentation**: if the same agent produces different outputs for the same input, what does documentation mean? The field is converging on documenting *behavioral envelopes* (the space of acceptable behaviors) rather than expected outputs, but the tooling for this is immature.

**Living documentation**: as agents are updated through prompt changes, model swaps, or fine-tuning, their behavior changes. Documentation written at deployment time drifts from reality. Some teams treat evaluation suites as the authoritative behavioral specification — the tests describe what the agent should do — but this conflates testing with documentation.

**Chain-of-thought as documentation**: agent scratchpads and reasoning traces look like transparent documentation of agent decisions. Whether they accurately reflect the underlying computation or are plausible-sounding rationalizations is an open research question with significant compliance implications.

**Documentation for non-technical stakeholders**: there is essentially no established practice for communicating agentic system behavior to executives, regulators, or affected users. The gap between trace-level technical documentation and meaningful user-facing disclosure is wide and largely unaddressed.

---

## Practical Recommendations

**Tier your documentation by audience**: developers need traces and prompt versioning; operators need runbooks and behavioral baselines; auditors need decision logs and compliance crosswalks; users need capability disclosures. Don't try to serve all four with a single artifact.

**Treat AGENTS.md as mandatory for any repository**: it costs almost nothing and makes agent behavior more predictable and auditable across the entire tooling ecosystem.

**Version system prompts like APIs**: a behavioral change in a prompt is a software change. Treat it as one, with versioning, change rationale, and evaluation gating.

**Instrument from day one**: retroactively reconstructing what an agent did from minimal logs is often impossible. OpenTelemetry-compatible traces captured at deployment become your audit trail, your debugging substrate, and your compliance evidence.

**Use Arazzo for any workflow with multiple tool calls**: if an agent needs to sequence more than two API calls, Arazzo gives you a machine-readable workflow document that both humans and other agents can consume.

**Separate what the agent *can* do from what it *should* do from what it *did***: Agent Cards (capability), Policy Cards (constraints), and observability traces (execution record) are three distinct documentation artifacts that serve different purposes and should be maintained independently.

---

## Sources

- MIT 2025 AI Agent Index, Staufer et al. (FAccT '26, arxiv 2602.17753)
- OpenAI "Practices for Governing Agentic AI Systems," Shavit et al. (2023)
- Linux Foundation / AAIF formation announcement (December 2025)
- AGENTS.md specification, agents.md
- Agent Cards: A Documentation Standard for Operational AI Agents, MICAI 2025
- Policy Cards: Machine-Readable Runtime Governance for Autonomous AI Agents (arxiv 2510.24383, October 2025)
- Arazzo Specification, OpenAPI Initiative (openapis.org/arazzo-specification)
- InfoWorld: "Best practices for building agentic systems" (April 2026)
- InfoQ: "From Prompts to Production: a Playbook for Agentic Development" (February 2026)
- MLflow: "Top 5 LLM and Agent Observability Tools in 2026" (April 2026)
- LangChain: "AI Agent Observability: Tracing, Testing, and Improving Agents" (April 2026)
- EU AI Act compliance analysis, Teleport / axis-intelligence (April 2026)
- IntuitionLabs: "Agentic AI Foundation: Guide to Open Standards" (April 2026)
