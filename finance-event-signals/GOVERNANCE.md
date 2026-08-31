# Governance

This project follows the **Snickerdoodle constitution** of the upstream Mycroft project
(principles P1–P8: labor separation, verified data layer, provenance, human gates,
two-customer logging, recipe lifecycle, the margin as record, earned trust). The constitution
text is **not reproduced here** — the upstream repo is all-rights-reserved. This repo references
and complies with it.

## How the principles land here

| Principle | Enforcement in this repo |
|---|---|
| P1 labor separation | the pipeline extracts and withholds; a named human calls `ClearGate` before anything is "actionable" |
| P2 verified data | `ingest-gateway` is the only service with outbound network; `events.raw → events.validated` gate (Week 2); `enrichment-svc` reads verified only |
| P3 provenance | every event carries its unmodified source record in `raw`; OTel traces (Week 3); no invented reads |
| P4 hard gates | `gate_decisions` row required before `events.actionable`; `conformance` CI is the machine half |
| P5 two customers | machine JSON log + `reports/generated/run-*.md` per run |
| P6 recipe lifecycle | `recipes/finance-event-signals.md` status only advances with a matching `logs/RUN_LOG.md` artifact |
| P7 the margin is the record | `RUN_LOG.md` entries, `audits/*.md`, gate decisions — append-only, attributed |
| P8 earned trust | `PRE_REGISTRATION.md` written before the first grading run; mismatches explained, not silently fixed |

## Solo-development honesty note

Developed by one person. The P4 human gate has no independent reviewer. Gate decisions in
`logs/RUN_LOG.md` are recorded as **acting-reviewer, SOLO**, and each records what could not be
independently verified. Recipe frontmatter status advances only when matching evidence exists in
the run log — never on feeling. `VERIFIED` is not reachable solo.

## Financial / advisory boundary

This is an educational project and a monitoring queue. It produces research observations and
model-and-workflow output, **never** personalized financial advice, a recommendation, a
position size, or a trade. Nothing here connects to a brokerage or places an order.

## License / distribution

Original code and sample data in this repo are the author's. The upstream Snickerdoodle
constitution and Mycroft recipe conventions are **not** redistributed here. Before any public
publication or PR into the upstream repo, confirm with the upstream maintainer.
