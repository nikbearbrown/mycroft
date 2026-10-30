# Evidence-Gap Planner and Specialist Routing

## Boundary

- Classification: `EVIDENCE_GAP_WORK_QUEUE_NOT_CAUSAL_ANALYSIS`
- Specialists collect and verify evidence; they do not infer causation.
- Recommendation: `NONE`
- Human gate: `OPEN`

## Supervisor Summary

- Run ID: `week36-routing`
- Trend run: `week35-trend`
- Delegations: 4 of 4

## Prioritized Work Queue

| Rank | Category | Specialist | Cumulative adverse impact | Missing evidence |
|---:|---|---|---:|---|
| 1 | revenue | `revenue-specialist` | 200000.00 | OWNER_CAUSAL_EXPLANATION |
| 2 | cogs | `cost-specialist` | 100000.00 | OPERATIONAL_DRIVER_RECORDS, OWNER_CAUSAL_EXPLANATION |
| 3 | opex | `cost-specialist` | 36000.00 | OPERATIONAL_DRIVER_RECORDS, OWNER_CAUSAL_EXPLANATION |

## Handoff Trace

| Sequence | From | To | Task | Result |
|---:|---|---|---|---|
| 1 | `supervisor` | `lineage-specialist` | `verify-source-chain` | `VERIFIED_INPUT_CHAIN` |
| 2 | `supervisor` | `revenue-specialist` | `gap-revenue` | `EVIDENCE_COLLECTED_PENDING_OWNER` |
| 3 | `supervisor` | `cost-specialist` | `gap-cogs` | `EVIDENCE_COLLECTED_PENDING_OWNER` |
| 4 | `supervisor` | `cost-specialist` | `gap-opex` | `EVIDENCE_COLLECTED_PENDING_OWNER` |

## Human Review

- [ ] Judge whether the routed evidence is adequate
- [ ] Supply additional operational evidence for unresolved gaps
- [ ] Provide and support any causal explanation
- [ ] Approve or block distribution

_A prioritized queue is not an approved explanation or decision._
