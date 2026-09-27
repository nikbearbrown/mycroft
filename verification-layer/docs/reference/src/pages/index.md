---
title: Overview
slug: index
section: Start
order: 0
summary: What the verification layer is, what it does and doesn't claim, and how this reference is organised.
---

The verification layer is an accountability layer for LLM agents. It runs an agent under a
strict output contract, retries or halts when the contract is broken, records every attempt,
and for financial questions runs two agents on the same SEC EDGAR data, compares their figures
one by one, and stops at a human decision gate when they disagree. A named reviewer clears
the gate, and what an investor-scope reader sees depends on whether they have.

It exists to test one claim from the constitution this repository runs under
(`SNICKERDOODLE.md`): AI made execution cheap, but it did not make judgment cheap. Everything
here is built so that the machine does the fetching, parsing, comparing and counting, and a
person does the judging, with a record of both.

{{stats}}

## What it does

- **Runs an agent under a contract.** Every reply must be a `<thought_log>` block followed by a
  `<conclusion>` block. A reply that breaks the contract is retried once with a corrective
  directive, then halted. See [The validation loop](f-validation-loop.html).
- **Gives the agent a search tool and real data.** Agents run on a local Ollama model (or
  Gemini) through LangChain, with Tavily search. For a ticker, each agent is given a slice of
  the company's EDGAR facts through a *lens*. See [Agents and model calls](f-agents.html) and
  [EDGAR data, lenses and filings](f-edgar.html).
- **Compares two agents figure by figure.** Each figure an agent cites is tied to a metric and a
  period and checked against the other agent and the filing. See
  [Cross-agent comparison](f-compare.html).
- **Checks the arithmetic.** Accounting identities and each figure against the value the agent
  was given. See [Accounting checks](f-checks.html).
- **Reads each agent's grade and explains why they differ.** A separate model call extracts a
  structured assessment; a deterministic synthesis says whether the agents differ on data,
  assumptions or weighting. See [Grades and synthesis](f-grades.html).
- **Stops for a human.** Mismatched figures, failed hard checks and differing grades become
  decision items. Until a named reviewer decides each one, investor-scope reads withhold the
  disputed values. See [The decision gate and scope](f-gate.html).
- **Shows its work.** Every step is traced and streamed live to the review app; every run can be
  exported as an audit record or a Markdown review; the system keeps its own list of known
  problems. See [Live runs](f-live.html), [Audit export](f-audit.html) and
  [Honest Ledger](ledger.html).

## What it does not claim

These limits are recorded in the design documents and still hold. The rest of this reference is
written to respect them.

- It detects **numeric disagreement** between two agents' conclusions, not reasoning errors, and
  not disagreement on dates, qualitative statements or causal claims.
- It does **not decide which agent is right.** It surfaces the disagreement and records a
  human's decision.
- A grade is **a model's judgment**, never a verified fact, and is labelled as one everywhere.
- The decision gate records **a typed name**, not an authenticated person
  ([gate-identity-self-declared](ledger.html#gate-identity-self-declared)).
- Withholding is only as strong as read authentication: some routes are still unauthenticated
  ([audit-criticals](ledger.html#audit-criticals)).
- It runs on **localhost only** and has not been deployed.

## How this reference is organised

<div class="cards">
<a class="card" href="quickstart.html"><strong>Start</strong><span>Install, configure and run the server, the review app and the tests.</span></a>
<a class="card" href="architecture.html"><strong>Architecture</strong><span>The layers and their dependency rule, a run end to end, the principles, and every recorded design decision.</span></a>
<a class="card" href="f-agents.html"><strong>Features</strong><span>One page per capability: how it works, where it lives, what it costs, what is still open.</span></a>
<a class="card" href="api.html"><strong>Reference</strong><span>HTTP routes, configuration, record shapes, the glossary, the Honest Ledger and the index of every file.</span></a>
<a class="card" href="files-root.html"><strong>Files</strong><span>One entry for every file in the project, with a generated inventory of what it defines and who uses it.</span></a>
<a class="card" href="history.html"><strong>History</strong><span>Older write-ups and what the archive holds.</span></a>
</div>

Search (press `/`) covers pages, sections, files, functions, classes, exports and routes.

## How to trust this reference

- **Generated parts can't drift.** The inventory under each file entry, the route table, the
  environment-variable table, the layer matrix, the counts above and the Honest Ledger page are
  read from the source on every build.
- **Written parts are checked for coverage, not truth.** `tests/test_docs_coverage.py` fails if
  a file has no entry or a link is broken. Whether an explanation is right is still a human
  judgment; each one names its source (the code, a `logs/RUN_LOG.md` entry or a design document),
  and a reason nobody recorded is labelled `(judgment, not recorded)`.
- **Built is not the same as observed.** Where a behaviour has only been exercised by tests with
  scripted agents, the page says so; where it has been seen on a live model, it says when.

The site is rebuilt with `python scripts/build_docs.py`. See [[docs/reference/**|the entry for
the site itself]] and [[scripts/build_docs.py]].
