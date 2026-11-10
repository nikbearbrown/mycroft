# Inference Gateway

One door for every model request Mycroft makes. It picks a tier, builds the
prompt, checks the answer, retries once if the check fails, and records what
happened — cost, latency, model, tier, and why that tier — before the caller
gets anything back.

**Status:** measured and decided. Policy 0.3.0 sends every task type to the
cheap tier, which was 31% cheaper and 31% faster than the previous policy at
unchanged correctness (FINDINGS section 12).

---

## For the person deciding whether to use it

**What question this answered.** Can Mycroft route each request to the cheapest
model that still answers correctly, and can the saving be *measured* rather
than assumed? Model choice was previously hardcoded four incompatible ways
across the repository, and nothing recorded what any of it cost.

**What the measurement said.** Running all 24 benchmark fixtures on all three
tiers, three times each (216 calls, $0.0147):

| tier | correct | mean cost | p50 latency |
|---|---|---|---|
| cheap | 92% | $0.000063 | 438 ms |
| mid | 98% | $0.000103 | 610 ms |
| strong | 92% | $0.000198 | 280 ms |

The expensive tier leads on no task type and loses on two. Every wrong answer
across the whole run came from two fixtures whose answer keys are disputed.

**What was decided.** Six candidate policies were replayed against that
baseline — fitted on two repeats, evaluated on a held-out third — against
thresholds fixed in August, before anything was measured: at least 20% cheaper
at equal quality, at most 20% slower. Only "always cheap" cleared them. The
adaptive break-even rule, reserved since Sprint 3 as the clever version, came
out 14% cheaper and made choices identical to a table a human would write by
eye.

**What this does not tell you.** The benchmark is 24 synthetic fixtures on one
provider, and no live traffic exists in this repository to test against: of 509
model requests here, 493 are the gateway's own (FINDINGS section 14). Two task
types, `summarization` and `rag_answer`, have **no quality measure at all** —
the model judge built for them agreed with a human at exactly chance level
(Cohen's kappa 0.00, FINDINGS section 10), so they are routed on cost alone.
Those facts belong in any report that quotes the numbers above.

---

## For the agent or engineer calling it

```python
from gateway.client import GatewayClient
from gateway.gateway import Gateway
from gateway.logbook import Logbook
from gateway.policy import Policy
from gateway.prices import PriceTable
from gateway.tiers import TierConfig
from gateway.adapters.groq import GroqAdapter

prices = PriceTable.load()
tiers = TierConfig.load()
policy = Policy.load(tiers)

client = GatewayClient(
    logbook=Logbook("logs/gateway/<your-run>.jsonl", prices),
    adapters={"groq": GroqAdapter(api_key=os.environ["GROQ_API_KEY"])},
    tiers=tiers.as_client_map(),
    policy_version=policy.version,
)
gateway = Gateway(client=client, policy=policy, tiers=tiers, caller="your-script.py")

result = gateway.handle(task_type="sentiment_classification",
                        text="Fake Industries beats estimates and raises guidance.")

result.text            # the answer
result.passed          # did the free check pass
result.final_tier      # which tier answered in the end
result.total_cost_usd  # cost of every attempt, rolled up
result.escalated       # was a retry needed
result.error           # a provider error, or None
```

`handle()` does not raise on a provider failure. It returns a `GatewayResult`
with `error` set, and the failure is in the logbook either way.

**The six task types** are locked in `policy.json`: `sentiment_classification`,
`topic_classification`, `structured_extraction`, `contradiction_detection`,
`summarization`, `rag_answer`. An unknown task type raises rather than falling
back to a default tier — a silent default is how a request ends up on the wrong
model forever.

### Rules worth knowing before you rely on it

- **One retry, never a chain.** There is no loop in `gateway.py`, so a chain is
  structurally impossible rather than discouraged.
- **A terminal error is never retried** — a bad key or an unknown model fails
  identically on every tier, because they share one credential.
- **A request you cannot price is never made.** An unpriced model raises before
  the adapter is touched. This is not hypothetical: the 16 prepared requests in
  `contradiction-detection-agent` name a model with no published rate, and the
  gateway refuses all of them.
- **Cost is frozen at log time** with the price table's version on the row, so
  a later price change cannot rewrite history.
- **One request, many attempts.** A retry keeps its `request_id`; averaging per
  attempt reported $4.65 where a two-attempt request actually cost $9.30.
- **Checks see shape, not correctness.** A fluent wrong answer passes every
  check and is never retried. Two checks have failed *correct* answers over
  formatting — a quoted span and a fullwidth bracket — and each one bought an
  escalation to a dearer tier.

### Configuration

| File | Holds |
|---|---|
| `policy.json` | the six task types, start tier, escalation target, token budget, validator |
| `tiers.json` | which model serves each tier, its context limit, and the pins |
| `prices.json` | per-1k-token rates, versioned; retired models keep their entry |

Changing `policy.json` after a baseline makes later results incomparable. Any
change is a version bump plus a RUN_LOG entry.

### Commands

```bash
python -m pytest scripts/gateway/tests -q          # 222 tests, no network
python scripts/gateway/first_live_call.py cheap    # one live call per tier, gated
python scripts/gateway/bench/audit.py              # fixture coverage
python scripts/gateway/bench/run.py --dry-run      # full sweep, cost bound only
python scripts/gateway/bench/baseline.py --dry-run # every tier, repeated, resumable
python scripts/gateway/bench/decide.py             # replay policies, apply thresholds
python scripts/gateway/bench/corpus.py --check     # every request in the repo
```

Anything that spends money shows a cost ceiling and waits for a typed `yes`.

### Layout

```text
schema.py       the logbook record contract
logbook.py      append-only writer, process lock + OS file lock
prices.py       versioned price table; refuses to price what it does not know
report.py       read the log back: per-request cost, percentiles, provenance
adapters/       one per provider, plus a scriptable fake used by every test
client.py       the one door -- no answer is returned without a row written
tiers.py        the cheap/mid/strong ladder and the pins
policy.py       the locked task types and their rules
router.py       pure function: task type + input length -> tier, with a reason
prompts.py      one prompt per task type
validators.py   the free checks: usable, not correct
gateway.py      route, call, check, retry once
bench/          fixtures, labelling, grading, baseline, judging, the decision
```

---

## Honest limits

- 24 synthetic fixtures, 4 per task type, against a target of 30.
- No live traffic has ever passed through it. Every recipe in this repository
  runs in sample mode with its live calls gated.
- One provider and one credential: a rate limit or an auth failure takes out
  every tier at once.
- `summarization` and `rag_answer` have no quality measure.
- Two fixture answer keys (`contra-003`, `extract-004`) are disputed and
  account for every wrong answer in the baseline.
- The retry rule is barely exercised: no check failed at all in the held-out
  repeat used for the decision.

Full evidence trail: `FINDINGS.md` (sections 1–14), `logs/RUN_LOG.md`,
`ATTESTATION.md`, and the run logs under `logs/gateway/runs/` and
`bench/results/`.