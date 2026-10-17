# System architecture

How the pieces fit, and — more usefully — why several of them are deliberately *not* what the
obvious design would have been.

## The shape

```
  SEC bulk data sets                    EDGAR, document by document
  (DERA, quarterly)                     (N-CSR / N-CSRS primary docs)
         │                                        │
         ▼                                        │
  download_bulk ──► build_parquet                 │
         │          (DuckDB, ~10-15M rows/qtr)    │
         ▼                                        │
    data/parquet/          ┌── form_d ◄── Form D bulk sets
         │                 │                      │
         ▼                 ▼                      ▼
  ┌──────────────────────────────────────────────────────────┐
  │  Postgres: raw_holdings, form_d_filings, restricted_lots │  immutable
  └──────────────────────────────────────────────────────────┘
         │
         ▼
  resolve_graph ──interrupt()──► a named human ──► review_decisions
   (LangGraph, Postgres checkpointer)                  │
         │                                             │
         ▼                                             ▼
   match_decisions ──► securities ──► marks ◄── company_identity
                                       │
                                       ▼
                        ┌──────────────────────────┐
                        │ signal/  findings        │
                        │          exposure        │
                        │          event_study     │
                        └──────────────────────────┘
                              │              │
              quarterly_graph │              │ mcp/server
              (fan-out, LLM)  │              │ (stdio, read-only)
                              ▼              ▼
                   _signal.json          six tools
                   quarterly_note.md     + cursors
```

## Layers

| Layer | What it is | Mutability |
|---|---|---|
| `data/*.zip`, `data/parquet/` | the SEC's bytes, and a queryable projection of them | re-downloadable |
| `raw_holdings`, `form_d_filings`, `public_observations` | filed facts, one row per disclosed position | **immutable** — resolution never edits a row here |
| `restricted_lots`, `ncsr_filings` | a *parse* of filed documents | replaced per filing on re-ingest |
| `review_decisions`, `match_decisions`, `company_identity` | judgments, with the name of who made them | append-only |
| `securities`, `marks` | the resolved analytical layer | rebuildable from the three above |
| `docs/_signal.json`, `docs/*.md` | published artifacts | regenerated |

The invariant that matters: **a matcher bug is always recoverable**, because resolution writes
to its own tables and never mutates the raw layer. The panel can be dropped and rebuilt from
`raw_holdings` + `match_decisions` without re-downloading anything.

## Where LangGraph earns its place — and where it does not

Most of this project is batch ETL, and batch ETL should not be a graph. Being explicit about
that is part of the design.

**Not a graph.** Bulk download, Parquet conversion, DuckDB filtering, loading, the marks build,
the split detector. Plain Python, CLI-invoked, idempotent, re-runnable. Wrapping these in a
state machine would add ceremony and remove nothing.

**Is a graph — entity resolution** (`src/graphs/resolve_graph.py`). A genuine agent loop:
look up candidates, consult prior decisions and the alias table, re-evaluate, and on low
confidence `interrupt()` to a human — backed by a Postgres checkpointer so the run pauses,
survives a process restart, and resumes days later when the reviewer returns. Proven across
both a deliberate process boundary and an unplanned server crash.

**Is a graph — quarterly analysis** (`src/graphs/quarterly_graph.py`). A real fan-out: one
branch per company, each measuring dispersion and propagation independently so that one
company's thin coverage cannot suppress another's figures, then a join because the note is
about the quarter rather than about a company. A join over a variable number of branches is
what a graph is for. Each branch opens its own connection; `psycopg2` connections are not safe
to share across concurrent branches.

## Where the LLM sits — exactly two places, and neither touches a number

**Entity-resolution adjudication** (`src/resolve/llm.py`, local Ollama). Consulted only in the
0.80–0.90 confidence band and on unresolved names. It was *measured against* the deterministic
matcher on the same 322 cases: precision fell from 99.6% to 94.5%, and every regression was an
invented match. The deterministic matcher is retained; the model is the documented fallback,
not the default.

**Quarterly commentary** (`src/signal/commentary.py`, Groq preferred). Handed a JSON block of
already-computed figures and nothing else — no database, no tools, no retrieval — so any number
in its prose that is not in that block is a fabrication, and that is mechanically checkable.
Four guards stand between a draft and the note:

| Guard | Catches |
|---|---|
| grounding | a number not in the figures (digits *and* spelled-out words) |
| superlatives | a ranking whose figure is not the extreme of any field |
| placeholders | `null` / `NaN` written into prose as if it were a value |
| length | an empty or trivial note, which passes every other check trivially |

A failed draft goes back to the model carrying the specific complaint, up to three attempts.
The superlative guard exists because a grounding check alone proved insufficient: a draft citing
only real numbers still invented a ranking that contradicted itself within a paragraph.

## The read interfaces

**MCP server** (`src/mcp/`, FastMCP over stdio). Six read-only tools. The hard constraint is
not the protocol but size: the largest query returns 2,151 rows, ~143,000 tokens serialised
whole. Every response is summary-first — a summary of the *whole* result set, one bounded page,
and an opaque cursor bound to its query arguments. Two bounds, not one: a row limit and a
character ceiling, because row widths are not uniform.

Read-only is a design decision, not an omission. A resolution decision needs a named human, and
a tool a model can call is the opposite of that.

**Signal contract** (`src/signal/contract.py`). JSON frozen at `schema_version` 1.0,
`additionalProperties: false` throughout, validated *on the way out* so no invalid signal
reaches disk. Refuses ten field names in two independent layers — the schema, and a name scan
for anywhere the schema does not reach.

## Scheduling

Two halves. `scripts/schedule.py` emits the platform-native command and needs nothing
installed; `n8n/quarterly_digest.json` is the optional n8n workflow with credentials referenced
from the n8n store. Both fire at 07:00 on the 20th of February, May, August and November — about
seven weeks after each calendar quarter end, because running on the quarter end itself would
produce a digest about the *previous* quarter and look like working software. A test asserts
both carry the same cron expression so they cannot drift.

## Tech stack

| Concern | Choice | Why not the obvious alternative |
|---|---|---|
| Bulk processing | DuckDB over Parquet | pandas in memory — rejected on measured volume (~442 MB compressed/quarter) |
| Store | Postgres (`psycopg2`) | one-row-per-run JSONB cannot answer "every manager's mark on this company over eight quarters" |
| SEC access | raw `requests` + bulk files | `edgartools` is built for 10-K/8-K shapes, not N-PORT TSVs |
| Matching | deterministic first, LLM on ambiguity only | LLM-on-everything is non-reproducible and worse at easy cases |
| Resolution model | local Ollama 8B | Groq would burn the free daily token limit on thousands of rows |
| Commentary model | Groq, large | local 8B produces weaker prose *and* weaker ranking — which is why the superlative guard exists |
| Human gate | LangGraph `interrupt()` + Postgres checkpointer | a blocking CLI prompt loses state across days |
| Splits | detect, quarantine, route to a human | auto-adjusting on a ratio heuristic mis-adjusts genuine repricings |

## Testing

334 tests, none requiring a GPU. Roughly 40 need a Postgres, a local model, or reachable EDGAR
and skip loudly without one, so the pass/skip split depends on the machine.

The tests worth knowing about are the ones that **withhold** something:

- `test_the_server_starts_with_no_cwd_and_no_pythonpath` — runs from a temporary directory with
  no working directory and no `PYTHONPATH`, because three consecutive setup failures were all
  properties of *how a client launches the server* and none was visible from inside it. A test
  that supplies what the real caller omits cannot find that class of bug.
- the N-CSR parser fixtures are **real filed HTML** from five filers, not markup written here.
  A parser whose only test is its author's own HTML proves the author is self-consistent.
