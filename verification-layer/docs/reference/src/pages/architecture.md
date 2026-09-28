---
title: Layers and components
slug: architecture
section: Architecture
order: 10
summary: The packages, the one-way dependency rule between them, and the running components a request passes through.
---

The Python code is split into packages that form inward-pointing layers. A layer may import
from the layers beneath it and never from a layer above. The rule is enforced by
[[tests/test_layering.py]], which reads every import with `ast` and fails naming the file and
line of any import the rule forbids. It isn't just described in a README.

## The layers

<figure>
<svg viewBox="0 0 760 360" role="img" aria-labelledby="layers-title layers-desc" xmlns="http://www.w3.org/2000/svg">
<title id="layers-title">The package layers and which may import which</title>
<desc id="layers-desc">Four rows. At the top, web may import every other layer. Below it, validation and producers. Below those, pipeline, adapters and datasources. At the bottom, core, which imports nothing internal. Arrows point from the importing layer to the imported one. A dashed arrow from validation up to web marks the one allowed upward import, which must be inside a function. Scripts and tests, on the right, may import anything.</desc>
<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="arrowhead"/></marker></defs>
<rect class="box-accent" x="20" y="20" width="600" height="50" rx="4"/>
<text class="t-mono" x="36" y="42">web/</text><text class="t-small" x="36" y="60">FastAPI routes, store, auth, step trace, Honest Ledger; serves the review app</text>
<rect class="box" x="20" y="110" width="290" height="50" rx="4"/>
<text class="t-mono" x="36" y="132">validation/</text><text class="t-small" x="36" y="150">compare, check, gate, synthesize, audit</text>
<rect class="box" x="330" y="110" width="290" height="50" rx="4"/>
<text class="t-mono" x="346" y="132">producers/</text><text class="t-small" x="346" y="150">concept lenses over EDGAR data</text>
<rect class="box" x="20" y="200" width="190" height="50" rx="4"/>
<text class="t-mono" x="36" y="222">pipeline/</text><text class="t-small" x="36" y="240">retry / halt loop, tracing</text>
<rect class="box" x="225" y="200" width="190" height="50" rx="4"/>
<text class="t-mono" x="241" y="222">adapters/</text><text class="t-small" x="241" y="240">LangChain, providers</text>
<rect class="box" x="430" y="200" width="190" height="50" rx="4"/>
<text class="t-mono" x="446" y="222">datasources/</text><text class="t-small" x="446" y="240">EDGAR, filing excerpts</text>
<rect class="box-accent" x="20" y="290" width="600" height="50" rx="4"/>
<text class="t-mono" x="36" y="312">core/</text><text class="t-small" x="36" y="330">contracts, directives, parser, schemas, numbers, assessment; imports nothing internal</text>
<rect class="box" x="640" y="20" width="100" height="320" rx="4"/>
<text class="t-mono" x="656" y="42">scripts/</text><text class="t-mono" x="656" y="62">tests/</text>
<text class="t-small" x="656" y="86">may import</text><text class="t-small" x="656" y="102">anything</text>
<line class="edge" x1="165" y1="70" x2="165" y2="108" marker-end="url(#arr)"/>
<line class="edge" x1="475" y1="70" x2="475" y2="108" marker-end="url(#arr)"/>
<line class="edge" x1="320" y1="70" x2="320" y2="198" marker-end="url(#arr)"/>
<line class="edge-accent" x1="280" y1="110" x2="280" y2="72" marker-end="url(#arr)"/>
<line class="edge" x1="115" y1="160" x2="115" y2="198" marker-end="url(#arr)"/>
<line class="edge" x1="360" y1="160" x2="190" y2="198" marker-end="url(#arr)"/>
<line class="edge" x1="525" y1="160" x2="525" y2="198" marker-end="url(#arr)"/>
<line class="edge" x1="115" y1="250" x2="115" y2="288" marker-end="url(#arr)"/>
<line class="edge" x1="320" y1="250" x2="320" y2="288" marker-end="url(#arr)"/>
<line class="edge" x1="525" y1="250" x2="525" y2="288" marker-end="url(#arr)"/>
</svg>
<figcaption>Arrows point from the importing layer to the imported one. Every layer may also import <code>core/</code> directly; those arrows are left out. The dashed arrow is the one upward import allowed, and only inside a function.</figcaption>
</figure>

| Layer | May import | Holds | Page |
|---|---|---|---|
| `core/` | nothing internal | The contracts every other layer is written against, the versioned directives, the structural parser, the record schemas, the one definition of a number, and the assessment vocabulary. | [Core](files-core.html) |
| `adapters/` | `core` | One provider each, all satisfying the `AgentAdapter` contract; the provider registry. | [Adapters](files-adapters.html) |
| `pipeline/` | `core` | The retry-then-halt validation loop and LangFuse tracing. | [Pipeline](files-pipeline.html) |
| `datasources/` | `core` | The only network egress for data: EDGAR companyfacts and filing documents. | [Data sources](files-datasources.html) |
| `producers/` | `core`, `pipeline`, `datasources` | The agents whose disagreement is measured: a concept lens over EDGAR data, run through the loop. | [Producers](files-producers.html) |
| `validation/` | `core`, `pipeline`, and `web` lazily | Everything that judges a run: figure comparison, accounting checks, the decision gate, synthesis, the audit record. | [Validation](files-validation.html) |
| `web/` | everything | The FastAPI server, the SQLite store, scope tokens, the step trace, the Honest Ledger, and the built review app. | [Web server](files-web.html) |
| `scripts/`, `tests/` | everything | Entry points and the test suite. | [Scripts](files-scripts.html), [Python tests](files-tests.html) |

**The one exception.** `validation/` reaches `web.db` to persist a run, which points upward.
It is allowed only as an import inside a function, and
`test_validation_reaches_web_only_lazily` in [[tests/test_layering.py]] keeps it from becoming a
module-level dependency.

**Why layers at all.** The code was a flat set of modules until the restructure recorded in
`logs/RUN_LOG.md`; the layering test's own docstring gives the reason for enforcing it: a
structure claimed only in a README "decays on the first commit that ignores it, and nothing
fails". `core/` importing nothing internal is what makes it safe for everything else to depend
on. See [D-02 in Design decisions](decisions.html#d-02).

## Imports between layers, as they are

{{layers}}

## Running components

A compare run touches every one of these. Only the ones marked *network* leave the machine.

| Component | Where | What it does |
|---|---|---|
| Review app | [[web/frontend/src/App.tsx]], served at `/app` | React 18 single-page app: start runs, watch them live, review records, decide gate items. |
| API server | [[web/server.py]] | FastAPI on uvicorn. Runs chat and compare work on worker threads (`asyncio.to_thread`) so the event loop keeps serving; streams steps as server-sent events. |
| Record store | [[web/db.py]], file `web/data/accountability.db` | SQLite: runs, flags, the append-only `gate_decisions` table. Gitignored. |
| Filing cache | [[datasources/filings.py]], folder `web/data/filing_cache/` | Gzipped filing documents, so an excerpt lookup fetches a filing once. Gitignored. |
| Model | [[adapters/langchain_adapter.py]] | Ollama on `OLLAMA_HOST` (local), or Gemini (*network*). Calls end after `MODEL_TIMEOUT_S` with nothing received. |
| Search tool | [[adapters/langchain_adapter.py]] | Tavily (*network*), called by the agent mid-reasoning, at most four tool round trips per call. |
| EDGAR | [[datasources/edgar.py]], [[datasources/filings.py]] | SEC companyfacts and filing documents (*network*). The only data egress. |
| Tracing | [[pipeline/observability.py]] | Self-hosted LangFuse (local), a no-op without credentials. |

## Concurrency

- **Two agents at once.** A compare runs its two producers on a two-thread pool
  ([[validation/cross_validation.py]]). `CROSS_AGENT_MAX_CONCURRENCY=1` forces one after the
  other. Reasoning objects are stored A-then-B whichever finishes first.
- **Thread-safe trace.** Each step gets a unique, gap-free sequence number under a lock
  ([[web/step_trace.py]]), and subscribers receive `step_started` / `step_finished` events as
  they happen.
- **The event loop stays free.** Work runs in `asyncio.to_thread`; events cross back to the loop
  with `call_soon_threadsafe` and are written to the client as server-sent events.
- **Known weak point.** Under two concurrent tool-calling requests, the local Ollama server has
  stopped responding four times; the cause is unconfirmed
  ([ollama-hangs-under-compare](ledger.html#ollama-hangs-under-compare)). The model-call timeout
  bounds the damage.

## Where to go next

- [A run end to end](lifecycle.html) follows one chat run and one compare run through these
  layers.
- [Principles in the code](governance.html) maps the constitution's rules to the code that
  enforces them.
- [Design decisions](decisions.html) records why the structure is the way it is.
