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
provider: no real request corpus exists in this repository. Two task types,
`summarization` and `rag_answer`, have **no quality measure at all** — the
model judge built for them agreed with a human at exactly chance level (Cohen's
kappa 0.00, FINDINGS section 10), so they are routed on cost alone. Those two
facts belong in any report that quotes the numbers above.

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