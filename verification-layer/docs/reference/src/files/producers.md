---
title: Producers
slug: files-producers
section: Files
order: 60
summary: The agents whose disagreement Cross-Agent Validation measures, each a concept lens over one shared EDGAR payload, and the two pairings the compare route offers.
---

A producer is one agent's view of a company: a set of us-gaap concepts (XBRL accounting tags such
as `Assets` or `NetIncomeLoss`) read from the shared SEC EDGAR companyfacts payload, written into a
context string, and reasoned over by a model through the unchanged validation loop. Cross-Agent
Validation runs two producers on the same company and compares what they conclude.

Each producer is a `ConceptLens` value (see [[producers/lens.py]]): a name, an `AgentID`, a concept
list, an optional header line, a trace-name prefix and a version. Nothing else differs between
producers. The lens cannot change how the model is called, how the reply is parsed or what happens
on failure; those are what the accountability layer holds constant across agents (module docstring
of [[producers/lens.py]]).

**Dependency rule.** `producers/` may import from `core/`, `pipeline/` and `datasources/`
(`tests/test_layering.py`: "a producer is a lens over a data source, run through the pipeline").

**The four lenses.**

| Lens | File | `AgentID` | Version | Concepts, in context order | Header |
|---|---|---|---|---|---|
| `financial` (Producer A) | [[producers/financial.py]] | `FINANCIAL` | v2 | `Assets`, `Revenues`, `NetIncomeLoss`, `EarningsPerShareDiluted` | none |
| `earnings` (Producer B) | [[producers/earnings.py]] | `EARNINGS` | v2 | `EarningsPerShareDiluted`, `EarningsPerShareBasic`, `OperatingIncomeLoss`, `NetIncomeLoss` | "Earnings-quality snapshot:" |
| `bull` | [[producers/bull.py]] | `BULL` | v1 | all six concepts above | the bull brief |
| `bear` | [[producers/bear.py]] | `BEAR` | v1 | all six concepts above | the bear brief |

**The two pairings** ([[producers/__init__.py]]'s `PAIRINGS`, offered by `/api/compare` as
`pairing`):

- `lenses`: financial against earnings. The lenses differ in what they see. Under lens v2 they share
  two concepts, `NetIncomeLoss` and `EarningsPerShareDiluted`; each still sees two the other does
  not (`Assets` and `Revenues` for A; `EarningsPerShareBasic` and `OperatingIncomeLoss` for B). The
  route's default contradiction rule for this pairing is `concept_aware`.
- `bull_bear`: bull against bear. Both see the same six figures and differ only in their brief, so a
  disagreement can only come from interpretation ([[producers/bull.py]] docstring). All six concepts
  are shared, and the route's default rule is `canonical_facts`, since any figure both cite is
  comparable.

The shared set is never written down in a comparator: `shared_concepts(*lenses)` in
[[producers/lens.py]] computes it from the lens definitions each time, and [[web/server.py]] passes
it to the comparison ([[validation/cross_validation.py]], [[validation/concept_linkage.py]]).

**How the web app runs them.** For a ticker compare, [[web/server.py]] fetches the companyfacts
payload once, calls each lens's `summarize` for the two contexts and `select` for the structured
`facts` in the payload, records each producer's `concepts` and `lens_version`, and runs both agents
through `validation.cross_validation.run_cross_agent_validation`. `run_lens` and the `analyze_*`
wrappers are the single-producer path, used by `scripts/smoke_langfuse_trace.py` and the tests.

## `producers/__init__.py`

**Role:** the producer registry: every lens, the pairings the compare route offers, and a lookup by
name.

- `LENSES`: `(FINANCIAL_LENS, EARNINGS_LENS, BULL_LENS, BEAR_LENS)`, ordered by role: Producer A,
  then Producer B, then the bull/bear pairing (comment). `tests/test_producer_lens.py` pins this
  order.
- `PAIRINGS`: `"lenses"` maps to `(FINANCIAL_LENS, EARNINGS_LENS)` and `"bull_bear"` to
  `(BULL_LENS, BEAR_LENS)`, each as (agent A's lens, agent B's lens). [[web/server.py]] indexes it
  with the request's `pairing`, which the request model limits to those two values.
- `BY_NAME`: lens by its `name`.
- Re-exports `ConceptLens` and `run_lens`.

The docstring's reason for the registry: callers enumerate the producers instead of hard-coding two
names, which is how the UI's setup band stopped hard-coding the concept lists it shows.

Related: [[producers/lens.py]], [[web/server.py]]

## `producers/lens.py`

**Role:** the `ConceptLens` value type, the context format every producer uses, the shared-concept
calculation, and `run_lens`, the one runner for a single producer.

### Key functions and classes
- `ConceptLens`: a frozen dataclass with `name`, `agent_id`, `concepts`, `header` (default `None`),
  `trace_prefix` (default `"llm_call"`) and `version` (default `"v1"`). Frozen because a lens is an
  identity, not a setting: if a run could change the concept set mid-flight, the concept list in the
  run's audit trail would no longer be evidence of what the agent read (docstring, citing P3).
  `version` is stored with every compare run as `producers[slot].lens_version`, so a replay or a
  corpus entry says which concept set produced it; the comment records v1 as the disjoint pairing
  used from 2026-08-28 to 2026-09-25 and v2 as adding `NetIncomeLoss` and `EarningsPerShareDiluted`
  to both.
- `ConceptLens.select(facts)`: `datasources.edgar.select_fact` for each concept in order, with the
  default `auto` basis; `None` where the payload has nothing. So `Assets` comes out as a
  point-in-time value and income and EPS figures as the latest standalone quarter (see
  [[datasources/edgar.py]]).
- `ConceptLens.summarize(ticker, facts)`: the context string. The first line is `Ticker: TICKER`, then
  the header if the lens has one, then one line per concept: `Concept: ` followed by
  `Fact.describe()`, for example `EarningsPerShareDiluted: 2.02 USD/shares (FY2026 Q3, 3 months
  ending 2026-06-27, 10-Q, frame CY2026Q2, accn ...)`. A concept missing from the payload is written
  `Concept: not reported`, not dropped, so the context shows what the agent was asked to consider
  and not only what happened to exist.
- `shared_concepts(*lenses)`: the concepts every given lens reads, as a `frozenset`; empty for no
  lenses. The docstring notes that [[validation/concept_linkage.py]] used to assume the two concept
  sets were disjoint for ever.
- `run_lens(lens, ticker, cik, call_agent_fn, *, run_id=None, fetch_fn=None)`: fetches the
  companyfacts payload, summarises it through the lens, wraps the adapter with
  `pipeline.observability.make_traced_adapter` under the name `TRACE_PREFIX:TICKER` (so each model
  attempt is its own LangFuse generation span), and runs `pipeline.middleware.run_validation_loop` as
  the lens's `agent_id`. It creates a run id when none is given. It adds no error handling: an
  `EdgarFetchError` or a `HaltError` propagates as is, because swallowing a halt here "would defeat
  ADR-07" (docstring).

### The context format is a contract
The value must come first on each line: the UI's input-provenance check reads the leading number
after the first `: ` back out to decide whether a number an agent cited was a value it was given
(`summarize` docstring). `tests/test_producer_lens.py` parses every line back into concept and value,
and `tests/test_edgar_facts.py` checks that the value stays first after the period metadata was
added. New concepts are appended so that line N of a v1 context still names the same concept
(`tests/test_producer_lens.py`, `test_v1_context_lines_keep_their_position`).

### Design notes
- One runner over a data value replaced two near-identical modules, `financial_grader.py` and
  `earnings_grader.py`, whose summarise and analyse functions were the same code with different
  constants, down to a copied latest-value helper. A third producer is now a `ConceptLens` literal,
  and ADR-07's retry-then-halt behaviour cannot drift between producers run through `run_lens`
  (module docstring; `logs/RUN_LOG.md`, 2026-09-04, "SOLID restructure: layered packages, no loose
  root modules, three duplications removed"; `docs/SYSTEM_DESIGN.md` §4).
  `tests/test_producer_lens.py` exercises a third lens built as a literal and asserts the retry
  path is the same for every lens in `LENSES`.
- Period and unit metadata were added to each line in B0 (`logs/RUN_LOG.md`, 2026-09-24, "B0:
  period- and unit-aware facts; a retired revenue tag; tool errors recorded as "ok"").

### Limits and open issues
- The module docstring says there is only one call site for the validation loop. That is true of
  producers run through `run_lens`; the web compare route does not use `run_lens`. It calls
  `summarize` and runs both agents through [[validation/cross_validation.py]], which calls
  `run_validation_loop` itself, with the web layer's own step-trace wrapper rather than
  `make_traced_adapter`. The retry-then-halt logic still lives in one function,
  [[pipeline/middleware.py]], but there are two paths into it.
- The docstring still describes Producer A as balance-sheet and top-line and Producer B as per-share
  and operating income, and says they differ in four things; since lens v2 they also share two
  concepts, and `version` is a fifth field.
- Every lens reads the `auto` basis; no lens asks for annual figures (B0 entry, open issues).

Related: [[datasources/edgar.py]], [[pipeline/middleware.py]], [[pipeline/observability.py]],
[[tests/test_producer_lens.py]]

## `producers/financial.py`

**Role:** Producer A, the headline-financials lens: `FINANCIAL_LENS`, plus the `summarize_facts` and
`analyze_ticker` wrappers.

`FINANCIAL_LENS` reads `Assets`, `Revenues`, `NetIncomeLoss` and `EarningsPerShareDiluted`, as
`AgentID.FINANCIAL`, with no header, trace prefix `llm_call`, version v2. `Revenues` is read through
the tag fallbacks in [[datasources/edgar.py]], so the current ASC 606 revenue tag is used when the
filer has moved to it.

- `summarize_facts(ticker, facts)`: `FINANCIAL_LENS.summarize(ticker, facts)`.
- `analyze_ticker(ticker, cik, call_agent_fn, *, run_id=None, fetch_fn=None)`: `run_lens` with this
  lens. It exists only to keep the LangFuse span name `analyze_ticker` (`@observe`), on which existing
  traces are keyed (docstring).

### Design notes
- The file is a declaration, not an implementation: the HTTP client moved to
  [[datasources/edgar.py]] and the orchestration to [[producers/lens.py]], which left only what is
  specific to Producer A, the concepts it reads (module docstring).
- Until 2026-09-25 (lens v1) the concept set was deliberately disjoint from Producer B's, so the two
  never saw a common figure and could never genuinely disagree. Lens v2 (roadmap phase B2) keeps
  each producer's own emphasis and adds the two headline figures both now share; new concepts go
  last so v1 lines keep their positions (comment above the lens; `logs/RUN_LOG.md`, 2026-09-25,
  "B2 + B3: overlapping lens metrics, and accounting checks that feed the gate"). The decision to
  overlap metrics now and add bull/bear later was the human's (`logs/RUN_LOG.md`, 2026-09-24,
  "Human decisions: audit-layer roadmap approved; web UI scope for brutalist/").
- Not a ratio engine: no structured recommendation or target price; ratio calculations,
  competitor-filing lookups and backtesting are out of scope (module docstring).

### Limits and open issues
- The ledger entry `disjoint-concepts` (RESOLVED) records the first live v2 result: AAPL's two agents
  cited the same net income and EPS and matched, but in the same batch two of three agent-A runs that
  parsed said diluted EPS was not in their context although it was. Agents do not reliably use the
  new line.
- Documentation disagreements: `docs/SYSTEM_DESIGN.md` §3.2 and §4 still list the v1 concept sets
  (three concepts each) and describe them as deliberately disjoint; `README.md` describes Producer A
  as balance-sheet and top-line only.

Related: [[producers/lens.py]], [[producers/earnings.py]], [[tests/test_financial_grader.py]]

## `producers/earnings.py`

**Role:** Producer B, the earnings-quality lens: `EARNINGS_LENS`, plus the
`summarize_earnings_facts` and `analyze_earnings` wrappers.

`EARNINGS_LENS` reads `EarningsPerShareDiluted`, `EarningsPerShareBasic`, `OperatingIncomeLoss` and
`NetIncomeLoss`, as `AgentID.EARNINGS`, with the header line "Earnings-quality snapshot:", trace
prefix `llm_call_earnings`, version v2. It reads the same companyfacts payload as Producer A.

- `summarize_earnings_facts(ticker, facts)`: `EARNINGS_LENS.summarize(ticker, facts)`.
- `analyze_earnings(...)`: `run_lens` with this lens, under the LangFuse span name
  `analyze_earnings`, kept stable for the same reason as `analyze_ticker` (docstring).

### Design notes
- It replaced a fixture Producer B with a second real grader, closing the stretch goal in the
  cross-agent validation proposal's §6.4 (module docstring; `logs/RUN_LOG.md`, 2026-08-28, "Replace
  fixture Producer B with a real second grader (closes proposal §6.4 stretch goal)").
- Lens v1's disjoint concept set gave the two producers genuinely different evidence, the
  information asymmetry the design argued makes disagreement meaningful, but it also meant they could
  never disagree about the same figure. v2 keeps most of the asymmetry and adds `NetIncomeLoss`, so
  the two share `NetIncomeLoss` and `EarningsPerShareDiluted` (module docstring; the B2 entry named
  under [[producers/financial.py]]).
- Both producers reach EDGAR through [[datasources/edgar.py]] rather than one importing from the
  other (module docstring).

### Limits and open issues
- `tests/test_earnings_grader.py`'s `test_different_concepts_than_financial_grader` still carries the
  comment "different evidence, same company" and checks only that `Assets` and `Revenues` are
  absent, which remains true under v2; the shared figures are checked in
  `tests/test_producer_lens.py`.
- Documentation disagreement: `README.md` describes Producer B as "a *different* slice" of the
  payload, which no longer holds for the two shared concepts.

Related: [[producers/lens.py]], [[producers/financial.py]], [[tests/test_earnings_grader.py]]

## `producers/bull.py`

**Role:** the bull lens, one side of the bull/bear pairing, and `SHARED_FIGURES`, the concept list
both sides read.

`SHARED_FIGURES` is every concept either filing lens reads, in first-seen order, built from
`FINANCIAL_LENS.concepts + EARNINGS_LENS.concepts` with duplicates removed: `Assets`, `Revenues`,
`NetIncomeLoss`, `EarningsPerShareDiluted`, `EarningsPerShareBasic`, `OperatingIncomeLoss`. It
follows the two lenses automatically if either changes.

`BULL_LENS` reads those six as `AgentID.BULL`, trace prefix `llm_call_bull`, version v1, with the
header: "Brief: you are the bull analyst. Make the strongest case FOR this company that these figures
support, using only these figures. If they do not support a bullish view, say so plainly."

### Design notes
- Bull and bear are the opposite of the financial/earnings pairing: the same facts, different briefs,
  so a disagreement can only come from interpretation, which is what roadmap phase B5 classifies
  (module docstring).
- The brief never permits going beyond the figures: the directive's grounding rule still binds every
  number, and "the figures don't support a bullish view" is an acceptable answer (module docstring).
- Added in roadmap phase B4 (`logs/RUN_LOG.md`, 2026-09-26, "B4 + U7: structured assessments and
  bull/bear, built and reverted as the default").

### Limits and open issues
- `bull-bear-unmeasured` (OPEN): four live agent runs under the active directive. Bear passed the
  format check 2 of 2 and bull 0 of 2; one bear answer added an unsupported claim and another argued
  from search results rather than the filing figures. Too few runs to say whether the briefs affect
  compliance or grounding.
- The brief says "using only these figures", but the adapter still offers the search tool when a
  key is configured, and its prompt tells the model a search result is a valid source
  ([[adapters/langchain_adapter.py]]). The NVDA bear run above is an instance.

Related: [[producers/bear.py]], [[producers/lens.py]], [[producers/__init__.py]]

## `producers/bear.py`

**Role:** the bear lens, the other side of the bull/bear pairing.

`BEAR_LENS` reads `SHARED_FIGURES` from [[producers/bull.py]] as `AgentID.BEAR`, trace prefix
`llm_call_bear`, version v1, with the header: "Brief: you are the bear analyst. Make the strongest
case AGAINST this company that these figures support, using only these figures. If they do not
support a bearish view, say so plainly." Same figures, opposite brief, same grounding rules (module
docstring).

`tests/test_producer_lens.py` checks that bull and bear read the same concepts, that the set is the
union of the two filing lenses, that the briefs say "FOR" and "AGAINST", and that both say "using
only these figures".

### Limits and open issues
- The same as for [[producers/bull.py]]: `bull-bear-unmeasured` (OPEN), and the search tool remaining
  available despite the brief.

Related: [[producers/bull.py]], [[producers/lens.py]]
