---
title: Accounting checks
slug: f-checks
section: Features
order: 50
summary: Whether each agent's figures add up on their own, match the filing values it was given, and whether the filing itself is consistent — hard rules gate, heuristics only inform.
---

Two agents can agree and both be wrong. The accounting checks ask a different question from the
comparison: does each agent's own answer hold together, and does it match what it was given?
They live in [[validation/constraints.py]] and run on every compare run, stored as
`cross_agent_comparison.structural_flags` under policy `b3-v1`.

## Three passes

1. **Internal consistency.** Definitional rules over the figures one agent stated, tried on every
   combination whose periods are compatible. A rule passes if any combination passes.
2. **Claim versus source.** Each figure an agent cites for a concept it was given is compared with
   the filing value it was given. Rounding is not misquoting: "$94.9B" is allowed $0.1B either
   way. Citing the prior period beside the current one is fine; one agreeing figure passes.
3. **Source sanity.** Rules over the filing itself, from the companyfacts payload already fetched.
   No new request.

A rule whose figures an agent didn't state isn't shown at all; a rule whose figures are for
different periods is `skipped`, with the reason.

## The rules

| Rule | Kind | Checks | Runs on |
|---|---|---|---|
| `eps_basic_ge_diluted` | hard | Diluted EPS is at most basic EPS (with a loss, the two are close) | agents, filing |
| `fcf_identity` | hard | Free cash flow = operating cash flow − capital expenditure, within 1% | agents |
| `balance_sheet` | hard | Assets = liabilities + equity, within 2% | agents |
| `balance_sheet_filed` | hard | Filed assets = filed liabilities and equity, within 0.1% | filing |
| `matches_source` | hard | A cited figure agrees with the filing value that agent was given | agents |
| `net_le_operating` | heuristic | Net income ≤ operating income | agents, filing |
| `operating_le_gross` | heuristic | Operating income ≤ gross profit | agents, filing |
| `gross_le_revenue` | heuristic | Gross profit ≤ revenue | agents, filing |

## What gates

A check becomes a [gate item](f-gate.html) only when it is **hard**, it **failed**, and it is
about **an agent's** figures ([D-37](decisions.html#d-37)).

- Heuristics are shown as "unusual, worth a look" and never gate: a one-off gain or tax benefit
  legitimately puts net income above operating income.
- Checks on the filing never gate: they state what the company filed, not what an agent claimed.
- A gated check's decisions are `confirmed_error`, `not_a_conflict` or `override_value`.

## Tested and observed

- **Tested** in [[tests/test_constraints.py]]: every rule, rounding, prior-period citations,
  mismatched periods, source sanity on a real filing sample, and the gate.
- **Observed live** on 2026-09-25: AAPL's claim-versus-source and filing checks passed; GOOGL's
  `net_le_operating` heuristic failed for agent B and for the filing itself, read as a real
  non-operating gain and not gated (`logs/RUN_LOG.md`, "B2 + B3"). A failed claim-versus-source
  check was recorded on NVDA run `9b1a9e0e` on 2026-09-26.

## Limits

- The checks see only figures the tagger recognises. A check that doesn't run isn't shown, so *no
  failure is not evidence of a correct figure*
  ([checks-lexical-coverage](ledger.html#checks-lexical-coverage)).
- Source sanity may check a different period from the one the agents were given; the period is
  printed on every result.
