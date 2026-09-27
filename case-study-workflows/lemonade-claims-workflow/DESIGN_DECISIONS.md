# Design Decisions

This document records every decision made while designing this pipeline that
required judgment beyond what the case study's public-record findings
disclosed — including deliberate deviations from this project's own
standing conventions. It is repo documentation, not an internal process
log: it cites the case study's confirmed findings by section where
relevant, but does not reference any internal design-process document, and
it exists so a future maintainer understands *why* the code looks the way it
does, not just what it does.

---

## 1. Authorization Gate — No Shipped Default

**Decision:** the Authorization Gate ships with zero settlement criteria —
no dollar threshold, no claim-type restriction, no confidence cutoff,
anywhere in the codebase, under any `[DEV]` marker.

**Why:** Lemonade has not disclosed what determines whether a claim falls
inside or outside AI Jim's settlement authority — no 10-K, shareholder
letter, investor presentation, blog post, or executive interview states a
dollar threshold, claim-type restriction, or confidence score. This is the
case study's central finding, not an incidental gap. Inventing a labeled
placeholder number — the approach used for other illustrative values in this
pipeline (confidence threshold, matching tolerance) — would have made the
Gate's behavior easier to demonstrate, but it would also have quietly
implied a shape of answer ("it's probably a dollar amount") that nothing in
the public record supports. The absence is the finding, and this design
preserves it rather than papering over it for the sake of a cleaner demo.

**Consequence:** the Authorization Gate requires a real, callable
`policy_fn` at every use — the pipeline does not run end-to-end without one.
See Decision 2 for how a full run is still possible without compromising
this.

## 2. Demo Harness Supplies the Only Policy That Exists — And It's Not `[DEV]`

**Decision:** `demo/run_sample_claims.py` defines `demo_only_policy`, a
trivial `amount < 500` rule, used only to exercise every branch of the
pipeline end-to-end, including automatic settlement.

**This is a deliberate, named exception to this project's standing rule that
every invented value carries a `[DEV]` marker.** `demo_only_policy`'s `$500`
line is an invented value, and it deliberately does **not** carry a `[DEV]`
marker — unlike the confidence threshold and matching tolerance, which do.
The reasoning: a `[DEV]` marker signals "this is a legitimate illustrative
default, replace it with your own tuned value." The demo policy is not
that — it has no relationship to any real authorization criteria, exists
solely to make the pipeline runnable, and marking it `[DEV]` risked implying
it was a serious placeholder rather than a test prop. Confirmed explicitly
during design, logged here per this project's own discipline that
disagreements and deviations get recorded, not smoothed over.

## 3. Escalation Reasons Use a Single Naming Convention

**Decision:** every escalation reason across every component is
`snake_case`: `unclassified`, `low_confidence`, `incomplete_extraction`,
`no_record_found`, `fraud_flag`, `mismatch`, `not_authorized`.

**Why it's worth recording:** an early draft of this design used
`"not authorized"` (with a space) for the Gate's reason while every other
component used `snake_case`. This was caught during structured review before
any code existed — the kind of schema drift that doesn't break a single
test but breaks any code, log parser, or enum written against the
inconsistent version. If you're adding a new escalation reason, match this
convention.

## 4. One Shared Exception Hierarchy for Configuration/Wiring Errors

**Decision:**

```
PipelineConfigurationError (base, exceptions.py)
  ├── MissingPolicyError    — raised by Orchestrator construction
  ├── UnknownProviderError  — raised by Configuration
  └── MissingAPIKeyError    — raised by Configuration
```

**Why:** an earlier draft had three different components each independently
inventing an unnamed "configuration error," and two of them (Configuration
and the LLM Provider Layer's `factory.py`) both claimed to validate the same
condition (an unrecognized provider name). Consolidating into one hierarchy
with one owner per check removed the duplication and made a real guarantee
explicit: `PipelineConfigurationError` and its subclasses represent
caller/wiring mistakes and are never confusable with a claim-level
`ESCALATED` outcome in logs, return types, or exception handling.

**Ownership split:** Configuration validates provider name and API key
presence, at load time, before anything else is constructed.
`llm_provider/factory.py` receives an already-validated provider name and
only maps it to an adapter class — it does not re-validate.

## 5. Configuration Stays a Single File (Option 1)

**Decision:** `config.py` holds provider choice, API key, confidence
threshold, and matching tolerance together, in one file — not split into a
separate secrets module.

**Why:** these three categories of setting (infrastructure choice, secret,
tunable default) fail differently in practice, and a genuine argument exists
for structurally isolating the secret in its own file so that code needing
only the tunables never has import-level access to the API key. This design
chose the simpler single-file shape instead, for two reasons: it keeps every
implementer-facing setting in one place a first-time reader can find without
hunting across files, and this is a reference scaffold, not a production
deployment, where the cost of a slightly larger blast radius is lower than
the cost of extra files to navigate. The API key itself is still sourced
only from the environment, with no default value, and is kept in its own
clearly separated section of the file rather than interleaved with the
`[DEV]`-labeled tunables.

**If you're adopting this pattern for a real deployment:** revisit this
decision. The two-file split is the more defensible default once real
credentials and real stakes are involved.

## 6. `FakeAdapter` Is the Default LLM Provider

**Decision:** `LLM_PROVIDER` defaults to `"fake"` if unset. A person cloning
this repo runs the full demo and full test suite with zero API keys and zero
cost.

**Why:** the LLM Provider Layer's entire purpose is to make the underlying
model swappable without touching pipeline logic. Requiring a real API key
just to see the pipeline run at all would undercut that purpose for anyone
evaluating the scaffold before committing to a provider. `FakeAdapter`
returns deterministic, scenario-keyed canned responses (see `fixtures.py`)
for a known set of demo/test inputs, and degrades to a generic
low-confidence response for anything else — it does not fabricate a
plausible-looking result for arbitrary input.

**Consequence:** `FakeAdapter` is shipped, working infrastructure, not a
`[DEV]` customization point itself. The `[DEV]` marker stays on the *choice*
of provider in `config.py`, including the fact that leaving it unconfigured
(defaulting to `"fake"`) is itself a deliberate, known-consequence default.

## 7. Fraud Signal Is a Separate Mock Component, Not a Field on the Visit Record

**Decision:** `mock_fraud_signal.py` is a standalone module with its own
lookup table, entirely independent of `mock_policy_visit_records.py`. The
two modules have no import of, or dependency on, each other — enforced by a
structural test on each side.

**Why:** the case study this pipeline is modeled on documents, as one of its
own explicit findings, that Lemonade's real fraud-detection system
(Forensic Graph) is a separate, company-wide system — not a step internal to
its claims bot — and that secondary coverage sometimes incorrectly
conflates the two. Storing a `fraud_flag` field directly on the same record
object Verification uses for policy/visit comparison would have reproduced
that exact conflation in this scaffold's own code, even though a fraud
signal and a policy/visit record represent two conceptually distinct things
Lemonade itself treats as separate systems. Splitting the mock data source into
two files, checked independently inside `Verification.process()`, keeps the
code's structure honest about the distinction the case study is making.

## 8. Missing-Policy Validation Happens at Orchestrator Construction, Not Per-Claim

**Decision:** `Orchestrator.__init__` raises `MissingPolicyError` immediately
if `policy_fn` is missing or not callable. The Authorization Gate itself
performs no such check.

**Why:** an earlier design had the Gate raise an error per-claim when no
policy was configured. This meant a mis-wired pipeline would process every
claim through Intake and Verification — doing real work, calling the LLM,
checking mock records — before failing at the very last step, every single
time. Moving the check to construction means a mis-wired pipeline fails
once, loudly, before any claim is ever processed, which is both more useful
to a developer debugging a bad deployment and more consistent with this
pipeline's overall fail-fast philosophy.

## 9. Dependency-Provision Rule: Scalars vs. Swappable Behavior

**Decision, stated once, applied everywhere:**

- **Scalar/tunable settings** (`confidence_threshold`, `matching_tolerance`,
  provider choice) are read directly from `Configuration` by whichever
  component needs them.
- **Callable/object dependencies representing swappable behavior**
  (`llm_client`, `policy_visit_lookup`, `fraud_signal_lookup`, `policy_fn`)
  are always constructor-injected into the component that uses them, never
  imported directly.

**Why:** this is what makes a real database swappable in for
`mock_policy_visit_records`, a real fraud system swappable in for
`mock_fraud_signal`, and a real LLM swappable in for `FakeAdapter`, without
editing `Intake`, `Verification`, or the `AuthorizationGate` at all. Stating
the rule once here means it doesn't need re-deriving component by component.

## 10. `demo/run_sample_claims.py` Doubles as the Reference Wiring Example

**Decision:** the demo script is not just a smoke-test — its
`build_pipeline()` function is the canonical example of how to construct
this pipeline's four top-level components (`Intake`, `Verification`,
`AuthorizationGate`, `Orchestrator`) from their swappable dependencies. A
real deployment copies this pattern, replacing `FakeAdapter`,
`mock_policy_visit_records.lookup`, `mock_fraud_signal.check`, and
`demo_only_policy` with real implementations.

**Why:** the `Orchestrator` accepts four already-built components and
constructs none of them itself — something has to show how those four get
built in the first place, or an implementer has no documented starting
point beyond reverse-engineering the test suite's mocks.

## 11. Environment Note: Test Suite Runs on `unittest`, Not `pytest`

**Decision:** the shipped test suite uses only the Python standard library's
`unittest` module — no `pytest`, no `pytest`-specific fixtures or
decorators.

**Why:** this is an environment constraint from the sandbox this pipeline
was built and validated in, which had no network access to install
`pytest`. It is not a design preference — `pytest` would have been the more
natural choice for parametrized tests in particular. If your environment
has `pytest` available, the test suite can be ported with minor changes
(mainly converting `subTest` loops back to `@pytest.mark.parametrize` and
`assertRaises` back to `pytest.raises`).
