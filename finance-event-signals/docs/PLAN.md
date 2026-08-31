# Plan: Real-Time Financial-Event Signal Pipeline — 4-week build

## Context

One portfolio-grade learning project that (a) exercises the full stack — **Go, Python, Kafka,
Redis, PostgreSQL, gRPC, Docker, Kubernetes, Linux, OpenTelemetry, LangGraph** — with every
tool load-bearing, and (b) makes decent use of the **Snickerdoodle framework**
(`SNICKERDOODLE.md`): a recipe spec, the `raw → verified` gate, two-customer outputs, a named
human phase gate, and an honest `RUN_LOG`.

**The project:** a near-real-time pipeline that ingests public company events (SEC 8-K filings,
IR/PR news feeds, FRED releases), runs each through a LangGraph agent that extracts a structured
trading-relevant signal — or **withholds** it when evidence is thin — persists and serves the
signals over gRPC/REST, **halts each signal at a human review gate**, then grades every cleared
signal against the realized N-day price move.

CV line: *agentic streaming pipeline that turns filings into graded, human-gated signals and
scores its own accuracy.*

Schedule matches the contributor cadence in this repo (Sachin's `insider-cluster-signals`,
Amruta's `Runway-Risk-Scorer`): **Week 1 data spine → Week 2 brain + gate → Week 3 observability
+ k8s → Week 4 honest loop + Snickerdoodle promotion.** Each week ends in a working, demoable
system, a `RUN_LOG.md` entry, and a defined recipe-lifecycle status.

---

## Reference — architecture

```
 SEC EDGAR full-text search  ┐
 company IR / PR RSS feeds   ├─▶ ingest-gateway (Go) ──events.raw──▶ validation-svc (Go)
 FRED releases               ┘     • polls on schedule                  • schema + freshness +
                                   • gRPC SubmitEvent                       ticker resolution
                                   • Redis dedup + token-bucket limit    • rejects ─▶ events.deadletter (audit)
                                                                        │
                                                              events.validated
                                                                        │
                                        enrichment-svc (Python + LangGraph)
                                        classify ─▶ route ─▶ LLM extract ─▶ self-consistency
                                                 ─▶ multi-turn verify ─▶ emit Signal | withhold
                                                                        │
                                                              events.enriched
                                                                        ▼
                                        persistence-svc (Go) ─▶ PostgreSQL   (idempotent upsert)
                                                                        │  status = 'pending_review'
              ┌─────────────────────────────────────────────────────────┤
              ▼                                                          ▼
   query-api (Go: gRPC + grpc-gateway REST)                   outcome-grader (Python, k8s CronJob)
     • GetSignals (server-streaming)                            • realized N-day price move
     • Redis hot-query cache                                    • writes signal_outcomes
     • ClearGate(reviewer, verdict, note)                       • recomputes accuracy scorecard (audit)
        └─▶ gate_decisions row  +  publish to events.actionable
              │
              ▼
   dashboard (Streamlit) — live feed · review queue · scorecard

OpenTelemetry: SDK in every service; trace context propagated through Kafka message headers;
Collector ─▶ Jaeger (traces) + Prometheus (metrics) + Grafana (dashboards, HPA source).
```

## Reference — every tool's non-optional job

| Tool | Job |
|---|---|
| **Go** | `ingest-gateway`, `validation-svc`, `persistence-svc`, `query-api` — throughput path + API surface |
| **Python** | `enrichment-svc` (LangGraph), `outcome-grader`, `dashboard` |
| **LangGraph** | enrichment state graph: `classify → route → extract → self-consistency → verify → emit \| withhold` (conditional edges + loop nodes + a `withhold` terminal) |
| **Kafka** | `events.raw → validated → enriched → actionable` (partition by ticker) + `events.deadletter`; **replay** for backfills; consumer lag = HPA signal |
| **Redis** | dedup (`SETNX` accession-hash + TTL), token-bucket for EDGAR's ~10 req/s cap, hot-query cache, pub/sub → dashboard |
| **PostgreSQL** | `events`, `signals`, `signal_outcomes`, `gate_decisions`, `accuracy_scorecard`; `ON CONFLICT` upserts |
| **gRPC** | `SubmitEvent`, `GetSignals` (server-streaming), `ClearGate`; `grpc-gateway` → REST for the dashboard |
| **Docker** | multi-stage image per service; `docker-compose` for the full local stack |
| **Kubernetes** | Deployments; **HPA on `enrichment-svc` keyed to Kafka lag**; `CronJob` grader; operators for Kafka/Redis/Postgres; isolated feed adapters |
| **Linux** | containers on Linux; `systemd` poller pre-k8s; `cron` pre-`CronJob`; shell ops runbook; ulimit / HTTP-client tuning |
| **OpenTelemetry** | one filing accession = one trace across all services (through Kafka headers); metrics: throughput, lag, LLM latency, withhold-rate, gate-clear latency |

## Reference — Snickerdoodle mapping

| Snickerdoodle | This project |
|---|---|
| ingest layer / `data/raw/` (P2: only ingest touches the network) | `ingest-gateway` + `events.raw` |
| GIGO layer / promotion to `data/verified/` | `validation-svc`; `events.deadletter` = the reject audit |
| tool layer (verified only) | `enrichment-svc` reads `events.validated`, never `events.raw` |
| two customers (P5) | per-run **JSON log** (+ OTel trace) *and* generated **Markdown report** |
| phase gate (P4) — hard stop, named human, logged | `status='pending_review'`; `ClearGate` writes `gate_decisions`; nothing hits `events.actionable` / the dashboard "confirmed" view until cleared |
| `logs/RUN_LOG.md` | one entry per batch / backfill / prompt-or-schema change / gate decision — the lifecycle-promotion evidence |
| recipe lifecycle | `DRAFT → SPECIFIED → RUNNABLE-SAMPLE → RUNNABLE-LIVE → VERIFIED`, each backed by a RUN_LOG artifact |
| conformance (machine half of P4) | CI: YAML/JSON parse, `.proto` compiles, schema files valid |
| pre-registration (Amruta's move) | `PRE_REGISTRATION.md`: predicted precision by `event_type`; falsification criterion |
| audits (`*-audit.md`) | `audits/deadletter-<date>.md`, `audits/scorecard-<date>.md` |
| human-only boundary | *is this event material enough to act on, and is the extracted direction right?* — AI extracts / withholds, human decides |

**Folder** (model on `origin/feature/insider-cluster-signals` + `projects/Runway-Risk-Scorer/`):

```
projects/finance-event-signals/
  recipes/finance-event-signals.md   GOVERNANCE.md   PRE_REGISTRATION.md
  logs/RUN_LOG.md   proto/   audits/   reports/generated/
  data/samples/   data/verified/SCHEMA_REFERENCE.md
  services/{ingest-gateway,validation-svc,persistence-svc,query-api}/   (Go)
  services/{enrichment-svc,outcome-grader,dashboard}/                   (Python)
  deploy/docker-compose.yml   deploy/k8s/   otel/collector-config.yaml
  Makefile   README.md
```

## Reference — data sources (all free)

- **SEC EDGAR** — full-text search API (`efts.sec.gov/LATEST/search-index`), submissions API,
  company-facts API (structured XBRL). No key; `User-Agent` required; ~10 req/s.
- **FRED** — `api.stlouisfed.org` (free key), macro releases.
- **News** — company IR / PR RSS feeds; 8-Ks are the primary event source.
- **Prices (grader)** — Yahoo chart API (stdlib-friendly; used by `insider-cluster-signals`) or stooq CSV.

---

# Week 1 — Data spine

**Goal:** an event flows `external source → events.raw → events.enriched → PostgreSQL` under
`docker-compose`, with no LLM yet. Prove the plumbing, the schema, and idempotency.

**Tasks**
- Repo scaffold (folder above). `Makefile`, `docker-compose.yml` with Kafka (Redpanda), Postgres.
- `services/ingest-gateway` (Go): poll EDGAR full-text search for recent 8-Ks on a timer;
  publish normalized events to `events.raw`. Redis `SETNX` dedup by accession hash. Redis
  token-bucket for the 10 req/s cap. Add one RSS feed source.
- `services/persistence-svc` (Go): consume `events.enriched`, upsert into Postgres
  (`events` table) with `ON CONFLICT DO NOTHING`. Postgres migrations (goose/atlas).
- `services/enrichment-svc` (Python): a **plain function** for now — pass-through +
  a stub `signal` object. Publish to `events.enriched`. (LangGraph is Week 2.)
- `data/samples/`: 20–30 sanitized sample events. `data/verified/SCHEMA_REFERENCE.md`.
- Scaffold `recipes/finance-event-signals.md` at `status: DRAFT` with the step list + gate
  placeholders. First `logs/RUN_LOG.md` entries.

**Deliverable / demo:** `docker-compose up`; a real 8-K published by the gateway shows up as a
row in Postgres within seconds.

**Verify:** (1) hand-check 3 sample events' extracted `{ticker, event_type}` against the filing
text — record in `RUN_LOG.md`. (2) Kill `persistence-svc` mid-stream, restart → **no duplicate
rows**.

**End-of-week Snickerdoodle status:** recipe `DRAFT`; `RUN_LOG` has the Phase-0 verification
entry + the Week-1 run entry.

**Cut line if behind:** drop the RSS source, EDGAR only. Drop migrations tooling, raw SQL.

---

# Week 2 — The brain + the human gate

**Goal:** events are validated (GIGO), enriched by a **LangGraph** agent that emits *or
withholds* a signal, land `pending_review`, and a human `ClearGate` call promotes them.

**Tasks**
- `services/validation-svc` (Go): `events.raw → events.validated`. Checks: schema, freshness
  (event timestamp vs. now), ticker resolution against a CIK map. Rejects → `events.deadletter`
  with a reason string.
- `services/enrichment-svc` (Python + **LangGraph**): replace the stub with the graph —
  `classify event_type → route → LLM extract {ticker, direction, magnitude, rationale,
  confidence} → self-consistency at 2 temps → multi-turn verify (CONFIRM/REVISE/REJECT) →
  emit Signal | withhold`. Consumes `events.validated` only.
- `proto/`: `signal.proto`, `ingest.proto`, `query.proto`. Codegen for Go + Python.
- `services/query-api` (Go): gRPC + `grpc-gateway` REST. `GetSignals` (incl. server-streaming
  live feed), Redis hot-query cache. `ClearGate(reviewer, verdict, note)` → writes a
  `gate_decisions` row → publishes the cleared signal to `events.actionable`.
- Add `gRPC SubmitEvent` to `ingest-gateway` (manual / webhook path).
- `services/dashboard` (Streamlit): pending-review queue + a "Clear" button calling `ClearGate`.
- `audits/deadletter-<date>.md` generator (reject counts + top reasons).

**Deliverable / demo:** submit a filing → it's validated, the agent extracts a signal (or
withholds) → it appears in the review queue → click Clear → it moves to `events.actionable`.

**Verify:** (1) feed the graph a deliberately contradictory input → it **withholds**, not a
confident wrong signal. (2) A malformed event → `events.deadletter` with a reason. (3) A signal
appears in `events.actionable` **only after** a `ClearGate` call carrying a reviewer name.

**End-of-week Snickerdoodle status:** the `raw → validated → enriched` gate and the human
phase gate both exist and are enforced. `RUN_LOG` entry. Recipe still `DRAFT` (no full sample
run yet).

**Cut line if behind:** self-consistency at 1 temp; skip multi-turn verify; `ClearGate` as a
REST endpoint only (defer the streaming `GetSignals`).

---

# Week 3 — Observability + Kubernetes

**Goal:** one filing accession = one end-to-end trace in Jaeger; the whole system runs on a
local k8s cluster; HPA scales the agent on load; a killed pod doesn't take the pipeline down.

**Tasks**
- **OpenTelemetry**: SDK in all 6 services. **Propagate trace context through Kafka message
  headers** (inject on produce, extract on consume) so the trace is not broken at each topic.
  Metrics: throughput, consumer lag, LLM latency, withhold-rate, gate-clear latency.
- `otel/collector-config.yaml` → Jaeger (traces) + Prometheus (metrics) + Grafana. Add a
  Grafana dashboard + a "trace one event" saved query.
- `systemd` unit for the gateway + a `cron` line for a manual grader run (the pre-k8s
  milestone: deployable on one Linux box). Short `README` ops runbook.
- Multi-stage `Dockerfile` per service. `deploy/k8s/`: Deployments, Services, ConfigMaps,
  Secrets; Kafka/Redis/Postgres via operators or Bitnami charts on **kind**/minikube.
- **HPA** on `enrichment-svc` keyed to Kafka consumer lag (KEDA or a custom metric).
- Feed adapters as **separate Deployments** (isolated failure domains).

**Deliverable / demo:** in Jaeger, a single accession's trace spans
`gateway → validation → enrichment → persistence`. In Grafana, kick a backfill and watch
consumer lag rise then HPA add `enrichment-svc` replicas.

**Verify:** (1) Jaeger shows **one unbroken trace** across four services (context survived the
Kafka boundary). (2) `kubectl delete pod` on `ingest-gateway` → the stale-source stop-condition
fires, pipeline continues. (3) Replay backfill → HPA scales up, drains, scales down.

**End-of-week Snickerdoodle status:** OTel traces = the machine-readable audit trail (P3/P7).
`RUN_LOG` entry noting the k8s milestone + the chaos-test result. Recipe still `DRAFT`.

**Cut line if behind:** skip kind, ship the `docker-compose` + OTel version and a *written*
k8s manifest set that's been `kubectl apply --dry-run` validated. Skip KEDA, use CPU-based HPA.

---

# Week 4 — The honest loop + Snickerdoodle promotion

**Goal:** the system grades its own accuracy against `PRE_REGISTRATION.md`, and the recipe is
promoted `DRAFT → RUNNABLE-SAMPLE → RUNNABLE-LIVE` with logged evidence + an attestation.

**Tasks**
- `services/outcome-grader` (Python, k8s `CronJob`): for cleared signals older than N days,
  fetch the realized price move, write `signal_outcomes`, recompute `accuracy_scorecard`
  and emit `audits/scorecard-<date>.md`.
- `PRE_REGISTRATION.md`: predicted precision by `event_type`; falsification criterion
  ("withhold-rate ≈ 0% while accuracy is at chance").
- Dashboard: add the running accuracy scorecard panel + backfill/replay controls.
- Finalize `recipes/finance-event-signals.md`: purpose, source inventory, inputs/schemas,
  phase gates (source · GIGO · extraction-adequacy · human-clear · report), numbered steps
  (AI vs. human), output contract (JSON log + Markdown report), stop conditions.
- `GOVERNANCE.md` ("follows SNICKERDOODLE P1–P8"). CI conformance job.
- **Promotion run 1 (sample):** full pipeline over `data/samples/` → conformance green →
  `audits/` generated and read → `RUN_LOG` entry → bump `status: RUNNABLE-SAMPLE`.
- **Promotion run 2 (live):** a live batch where a human clears **every** gate → logged gate
  decisions → `RUN_LOG` entry → bump `status: RUNNABLE-LIVE`.
- Write the **attestation** block: what was run, seen vs. expected, **what was NOT tested**,
  what broke and was fixed.
- `README.md`: architecture, the per-tool table, how to run (compose + k8s), the demo script.

**Deliverable / demo:** replay a historical window → the scorecard populates → it's compared
against the pre-registered predictions in `RUN_LOG.md`, mismatches explained not silently fixed.

**Verify:** (1) scorecard is byte-reproducible from the same inputs (P3). (2) Every
`events.actionable` message traces to a `gate_decisions` row. (3) Each recipe-status bump has
a matching `RUN_LOG` entry as its evidence. (4) `conformance` CI green.

**End-of-week Snickerdoodle status:** recipe at `RUNNABLE-LIVE` with attestation, populated
`RUN_LOG.md`, `PRE_REGISTRATION.md`, and ≥1 `audits/scorecard-*.md`. (`VERIFIED` needs an
independent reviewer — record as `acting-reviewer SOLO`, like Amruta.)

**Cut line if behind:** grader as a manual script instead of a `CronJob`; stop at
`RUNNABLE-SAMPLE` and note the live gated run as the next step.

---

## Definition of done (end of Week 4)

- All services run under `docker-compose` **and** on local k8s.
- One filing → one OTel trace, end to end, in Jaeger.
- HPA visibly scales `enrichment-svc` on a backfill; a killed pod doesn't take the pipeline down.
- `recipes/finance-event-signals.md` at `status: RUNNABLE-LIVE` with attestation +
  `logs/RUN_LOG.md` + `PRE_REGISTRATION.md` + ≥1 `audits/scorecard-*.md`.
- Dashboard shows: live signal feed, pending-review queue, running accuracy scorecard.

## First step (Week 1, day 1)

`services/ingest-gateway/main.go` — a ~50-line Go program that hits the EDGAR full-text search
API for recent 8-Ks and prints them. `services/enrichment-svc/spike.py` — ~30 lines that send
one filing to an LLM and print the extracted signal. Confirm both, write the first
`logs/RUN_LOG.md` entry, then stand up `docker-compose` with Kafka + Postgres.
