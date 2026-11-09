# The signal contract and the quarterly commentary

*Week 10, with [`mcp_server.md`](mcp_server.md) — the two halves of making the
panel consumable from outside this repository.*

Two artifacts, deliberately distinct. `plan.md`: *"The signal is a contract
(`schema_version`) the coordination layer parses and that must change slowly;
the note is human presentation that can be restyled freely."*

```
python -m src.graphs.quarterly_graph              # run both
python -m src.graphs.quarterly_graph --dry-run    # no model call
python -m src.graphs.quarterly_graph --backend groq
python -m scripts.schedule --show                 # the scheduler command
```

| Artifact | For | Changes |
|---|---|---|
| `docs/_signal.json` | the coordination layer and other agents | slowly, with a version bump |
| `docs/quarterly_note.md` | a person | freely |

## The graph, and why this one is a graph

`plan.md` is strict that most of this project should not be a state machine —
*"Most of this project is batch ETL, and batch ETL should not be a graph."*
This is one of the two places it says a graph earns its place:

```
collect ─► fan_out ─► measure_company × N ─┐
                                            ▼
          render_note ◄── commentary ◄── assemble
```

The fan-out is real: each company's dispersion and propagation are measured
independently, so one company's thin coverage cannot suppress another's
figures. The synthesis then needs all of them at once, because the note is
about the quarter rather than about a company. That join over a variable
number of branches is what a graph is for.

Each branch opens its own database connection. Branches may run concurrently
and a `psycopg2` connection is not safe to share across them.

## The contract, frozen at 1.0

Nine top-level keys. `additionalProperties: false` on every object, so a field
added in passing fails validation rather than reaching a consumer.

```json
{
  "schema_version": "1.0",
  "generated_at": "…", "period": {…}, "coverage": {…},
  "companies": [ { "company": "…", "status": "full|thin|watchlist",
                   "dispersion": {…}, "propagation": {…} } ],
  "guards": {…},
  "commentary": { "text": "…", "is_model_output": true, "model": "…" },
  "not_supported": [ … ],
  "provenance": {…}
}
```

**Validation happens on the way out.** `contract.envelope()` validates before
returning and `contract.write()` validates before writing, so there is no path
from this module to a file that skips the contract. A test asserts an invalid
signal never reaches disk.

### Ten field names the signal will never carry

`valuation`, `company_valuation`, `implied_valuation`, `market_cap`,
`post_money`, `pre_money`, `shares_outstanding`, `return`, `irr`, `moic`.

Two layers enforce this, and they catch different things. The schema rejects
any unknown field wherever it reaches. The **name scan** is the standing
prohibition for anywhere it does not — a free string, or an object some future
version adds deliberately.

The reason is structural rather than stylistic: N-PORT reports a fund's share
count, never the company's shares outstanding. A field for a valuation would
invite a consumer to fill it from somewhere else and inherit that source's
error.

### Suppression is a value, not a missing key

A company that is `thin`, `watchlist`, or priced by fewer than three managers
publishes marks but not dispersion or propagation:

```json
"dispersion": { "groups": 0, "median_spread": null,
                "suppressed_reason": "only 2 managers priced this company…" }
```

A consumer can tell *"we did not publish this"* from *"there was nothing to
publish"*. A missing key cannot say which.

### The limits travel inside the payload

`not_supported` carries four stated limits — no valuation, no timeliness, no
complete coverage, no return — in the signal itself. A consumer parsing the
contract gets them; a consumer reading a README might not.

## The commentary, and the three guards

The model is the only prose writer in the project. It is handed a JSON block
of already-computed figures and **nothing else** — no database, no tools, no
retrieval — so any number in its output that is not in that block is a
fabrication. A test asserts the module contains no `connect(` and no `SELECT`.

Three mechanical checks stand between a draft and the note:

| Guard | Catches | Example draft that fails |
|---|---|---|
| **grounding** | a number not in the figures | *"The spread was 47.3 percent."* |
| **superlatives** | a ranking that is wrong | *"Databricks has the lowest number of marks, at 2151."* |
| **placeholders** | a serialiser artifact in prose | *"Figure AI had a maximum spread of null."* |

A failed draft is handed back to the model **with the specific complaint**, up
to three times. Unbounded retries would be a way to keep rolling until the
checks happen to pass; a fourth failure is a refusal.

### Why the superlative check exists

It was not planned. The first real run passed grounding cleanly — every number
in the prose was one the model had been given — and the prose still said:

> *"Anduril Industries, Inc. has the lowest number of marks, at 509…"*

one sentence before saying:

> *"Figure AI Inc. has the lowest number of marks, at 31."*

Both numbers were real. The ranking was invented, and it contradicted itself
within a paragraph. An 8B model cannot reliably rank ten rows across six
fields, which is precisely why `plan.md` specified a 70B model for commentary.

A check is better than a bigger model, because it fails the same way on any
model. The prompt now also forbids ranking outright, and the check is the
backstop for when the model does it anyway.

### What the guards cannot catch

A wrong qualitative judgment with no number attached. The accepted note
contains *"The dispersion is moderate, with a median spread of 0.3403"* — the
figure is right, "moderate" is the model's word, and nothing mechanical
disputes it. That is why every rendering of the commentary is labelled **model
output, not a verified claim**, and why `plan.md` reserves "verified" for a
human citing a source.

### When no model is reachable

The commentary is **refused**, with the reason recorded, and the signal is
emitted without it. There is no template.

A templated paragraph would be indistinguishable from model output while
carrying `is_model_output: true`, and a quarterly note is exactly the artifact
where that substitution would never be noticed. The deterministic figures are
unaffected — they are computed before any model is consulted.

### Backends

| Backend | When | Note |
|---|---|---|
| `groq` | `GROQ_API_KEY` is set | `plan.md`'s choice: `llama-3.3-70b-versatile`, free tier |
| `ollama` | a local server answers | fallback; `plan.md` rejected local models for commentary on prose quality, not correctness |
| none | neither | refuses |

This run used **ollama / llama3.1:8b**, because no `GROQ_API_KEY` is set in
this environment. The signal records which model wrote the text, so a later
Groq run is visible as a change rather than a silent improvement.

## The scheduler

Two halves. `scripts/schedule.py` needs nothing installed:

```
python -m scripts.schedule --show      # print the platform-native command
python -m scripts.schedule --install   # register it (asks first)
python -m scripts.schedule --run-now   # run the job once
```

`n8n/quarterly_digest.json` is the optional n8n half — a quarterly trigger, the
graph, a schema-version gate, and a digest email. **Credentials are referenced
from the n8n store by id; the file carries no secret.** A test asserts that
against node parameters rather than the file text, because the file's own notes
contain the sentence *"this file carries no password"* and a naive scan fails
on its own documentation.

### The schedule is the 20th, not the quarter end

Running on 31 March produces a digest about December. Verified lag is ~55–60
days from a fund's period end to its filing, and the DERA bulk sets lag those
again. So: **07:00 on the 20th of February, May, August and November**, about
seven weeks after each calendar quarter end.

A scheduler that fires on the obvious date and reports the wrong quarter looks
like working software, which is worse than one that does not run. A test
asserts the local scheduler and the n8n workflow carry the *same* cron
expression, so the two cannot drift apart.

The workflow halts rather than emailing if the signal reports a
`schema_version` it does not know. A contract change is not a digest to send.
