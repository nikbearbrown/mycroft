# finance-event-signals

Near-real-time pipeline that ingests public-company events (SEC 8-K filings, EDGAR latest-filings
feed, later FRED releases), runs each through a LangGraph agent that extracts a structured
material-event read — or **withholds** it when evidence is thin — persists and serves the reads
over gRPC/REST, **halts each read at a human review gate**, and then grades every cleared read
against the realized N-day price move.

**Financial problem it solves:** a junior analyst can't watch every 8-K, press release, and macro
print as it lands — and when the desk does react to one, nobody tracks whether the read was right.
This surfaces material events in near-real-time, forces a human sign-off, and grades every call
against what the market did.

This is a monitoring queue for an analyst. **Not investment advice; nothing here decides or
places a trade.**

## Status

**Week 2 done — GIGO gate + LangGraph agent + human ClearGate.**
`events.raw → validation-svc → events.validated → enrichment-svc (LangGraph) → events.enriched
→ persistence-svc → PostgreSQL`; signals land `pending_review`/`withheld`; a named human calls
`ClearGate` to move one to `actionable` (which is the only way anything reaches
`events.actionable`). Review UI at `localhost:18501`. Deterministic LLM by default; set
`LLM_PROVIDER=anthropic` + `ANTHROPIC_API_KEY` for the real model.

Recipe lifecycle status: **DRAFT** (`recipes/finance-event-signals.md`), `todos_open: 3`.
Next: Week 3 (OpenTelemetry + Kubernetes), Week 4 (outcome-grader + promotion).
See `docs/PLAN.md` and `logs/RUN_LOG.md`.

## Architecture (target)

```
sources ─▶ ingest-gateway (Go) ─events.raw─▶ validation-svc (Go) ─events.validated─▶
          enrichment-svc (Python + LangGraph) ─events.enriched─▶ persistence-svc (Go) ─▶ PostgreSQL
          query-api (Go: gRPC + REST)  ·  outcome-grader (Python)  ·  dashboard (Streamlit)
OpenTelemetry traces every hop through Kafka headers → Jaeger + Prometheus + Grafana.
```

Week 1 wires only: `ingest-gateway → events.raw → enrichment-svc (passthrough) → events.enriched → persistence-svc → PostgreSQL`.

## Run

```bash
cp .env.example .env                  # set EDGAR_USER_AGENT to "<name> <email>"
make up                               # full stack (9 services)
make signals STATUS=pending_review    # the review queue
open http://localhost:18501           # or use the dashboard
make clear SIG=sig_<accession> WHO=you VERDICT=actionable   # clear the gate
make deadletter                       # rejected events + reasons
make test                             # LangGraph branch tests
make down
```

Ports: query-api REST `:18080`, gRPC `:19090` · ingest gRPC `:19091` · dashboard `:18501`.

## Layout

```
services/ingest-gateway/   (Go)      poll EDGAR, dedup, rate-limit, produce events.raw
services/persistence-svc/  (Go)      consume events.enriched, upsert PostgreSQL
services/enrichment-svc/   (Python)  Week 1: passthrough + stub signal. Week 2: LangGraph.
data/verified/SCHEMA_REFERENCE.md    the event envelope contract
deploy/postgres/001_init.sql         schema
recipes/finance-event-signals.md     Snickerdoodle recipe spec (DRAFT)
logs/RUN_LOG.md                      every meaningful run + gate decision
GOVERNANCE.md  PRE_REGISTRATION.md   Snickerdoodle governance
```
