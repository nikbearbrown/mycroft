# Design Decisions Log

Every sequencing or dependency choice not directly sourced gets an entry here
before it's allowed into the orchestrator. Entries are dated to the session
in which the decision was made.

---

### 2026-DD-001 — Extraction belongs to Intake, not a separate step

**Context:** The case study (`Section 4b`) carries two open PENDING markers
asking whether structured claim-detail extraction (amount/merchant/date) is
part of "understanding intent," part of "verifying details," or a fourth,
unnamed function. Jermyn's quote groups "getting information from the
customer" with "understanding intent" as one described phase but does not
explicitly assign extraction to either function.

**Decision:** Extraction is implemented inside Intake.

**Justification:** Extraction has to happen before verification can check
anything — Verification's whole job is comparing *extracted* claim fields
against a record. There's no function between "customer describes a
transaction in free text" and "system knows the claimed amount/merchant/date"
other than Intake itself. Putting it anywhere else would require an
undocumented fourth step this case study has no basis to invent.

**Status:** CONSTRUCTED. Not sourced. Consistent with this project's own
prior reasoning on the same open question, reached independently the same
way here as it was elsewhere.

---

### 2026-DD-002 — Verification's record-not-found is fail-fast; a found-but-mismatched record is not

**Context:** Two different "verification didn't succeed" outcomes exist:
(a) no transaction matching the claimed merchant/date exists at all, and
(b) a transaction exists but its amount doesn't match the claim.

**Decision:** (a) escalates immediately and skips Gate. (b) is passed to
Gate as a normal `match_result=False` result; Gate decides.

**Justification:** Gate's stated job is deciding auto-lodge vs. escalate
*based on a match outcome*. If no record exists, there is no match outcome
to hand Gate — Gate would have nothing to evaluate, so this is treated as a
different, earlier failure category rather than routed through Gate's logic.
A mismatch (record exists, amount is wrong) is exactly the kind of decision
Gate exists to make, so it is not intercepted early.

**Status:** CONSTRUCTED. No source addresses this distinction; it follows
from Gate's stated purpose in the case study, not from a CBA disclosure.

---

### 2026-DD-003 — Verification must guard against incomplete input rather than raise

**Context:** Discovered by actually running the test suite (not by prose
review) — `tests/test_intake_verification_dependency.py`'s deliberately
malformed-input test crashed Verification with an unhandled
`AttributeError` instead of returning a graceful escalation.

**Decision:** Added an explicit guard at the top of `run_verification` that
returns `escalate=True, escalation_reason="incomplete_claim_details"` when
`claimed_merchant` or `claimed_date` is `None`, before attempting any match.

**Justification:** This is precisely the category of error this project's
test-design discipline exists to surface: a dependency test that runs a
downstream component with the upstream output "withheld or malformed" is
supposed to confirm the downstream step "fails, waits, or behaves in the
documented way — not silently succeeding with missing data." An unhandled
crash is neither "behaving in the documented way" nor a graceful failure —
it's an undocumented third outcome. Fixed immediately rather than left in
place, per this project's own standard for CRITICAL/MAJOR findings.

**Status:** CONSTRUCTED (defensive coding choice). This is also the
concrete, in-repo demonstration of why actually running the test suite
matters — this bug did not exist in prose, and would not have been found
without running the suite.

---

### 2026-DD-004 — Auto-lodge threshold set at $500 (CONSTRUCTED, arbitrary)

**Context:** Evident Insights confirms a gate exists ("lodged automatically
upon satisfaction of the right criteria") but names no criteria.

**Decision:** `AUTO_LODGE_MAX_AMOUNT = 500.00`.

**Justification:** None beyond illustration — this number is explicitly
invented, marked `[DEV]` in `gate.py`, and called out in the README's
Explicit Non-Claims section so no reader mistakes it for CBA's actual
threshold, which has never been disclosed.

**Status:** CONSTRUCTED. Arbitrary by design; flagged as a `[DEV]`
customization point rather than presented as a considered business rule.

---

### 2026-DD-005 — Gate's auto-lodge threshold now varies by dispute_type (risk-tiered)

**Context:** Review Pass 1 found that Gate's spec declared `dispute_type` as
a required input but never used it in the criteria — an unused declared
dependency. Three resolutions were presented: (a) remove `dispute_type`
from Gate entirely, (b) give it a real job via risk-tiered thresholds, (c) a
hybrid — remove it from decision logic but keep it flowing as logged
context with a `[DEV]` extension marker for future use.

**Recommendation given:** (c), the hybrid — on the reasoning that (a) is the
most disciplined but leaves `dispute_type` doing nothing, and (b) invents a
second unsourced number to justify a first design mistake, doubling
invented content rather than reducing it, with zero basis in Section 3.1 or
6.3 for a specific risk-tiering rule.

**Decision made:** (b) — risk-tiered thresholds by dispute type,
**against the stated recommendation above**. This is recorded here
explicitly, not smoothed over, per this project's own standard of stating
disagreements rather than picking the more convenient version silently.

**Thresholds:** `duplicate_charge` → $750, `unrecognized_charge` → $500
(baseline), `unauthorized_transaction` → $250, `other` → $500 (falls back
to baseline).

**Justification for the values themselves (stated once, per the Ranked
Improvements MINOR finding from Review Pass 1, which asked for at least a
one-line rationale beyond "arbitrary"):** a duplicate charge is typically a
merchant/system billing error, not a compromised account, so a bank might
reasonably tolerate a higher auto-resolve ceiling; an unauthorized
transaction claim implies no customer consent at all, which carries higher
fraud-risk if wrongly auto-approved, so a tighter ceiling forces earlier
human review. This reasoning is this project's own risk logic, not CBA's —
CBA has never disclosed any criteria, tiered or otherwise (Section 6.3).

**Status:** CONSTRUCTED, with no sourcing basis whatsoever for the specific
tiering or dollar figures. Flagged in the README's Explicit Non-Claims
section so no reader mistakes this for a documented CBA risk model.

---

### 2026-DD-006 — Unclassified dispute_type now escalates at Intake, doesn't default through Gate

**Context:** Review Pass 2 found that entry 005 (risk-tiered Gate
thresholds) created a case that didn't matter before: Intake's escalation
criteria never checked whether `dispute_type` itself was classifiable — only
`extraction_confidence` and whether amount/merchant/date were missing. A
claim with a cleanly extracted amount, merchant, and date, but an
unclassifiable type, would previously pass through to Gate and silently
default to the `other` / $500 tier — the one case with the least
information about risk would get the middle-of-the-road treatment.

**Decision:** Added `dispute_type is None` as an Intake escalation
condition, alongside the existing missing-field and low-confidence
triggers. An unclassified dispute type now routes to human review directly,
before Verification is even called.

**Justification:** Entry 005's entire premise is that knowing the dispute
type lets the system calibrate risk. Not knowing it is the one scenario
that premise doesn't cover — defaulting it to a middle tier would have
applied risk-tiering logic to a case it was never designed to handle, and
done so silently. Escalating instead keeps the tiering honest: it only ever
fires when the input it depends on actually exists.

**Consequence:** Gate's `other`/unclassified $500 fallback is now a
defensive-only branch (reachable if Gate is unit-tested directly, not
reachable via the actual pipeline). This is intentional layered defense,
not dead code to be deleted — the same pattern already used for Gate's
`record_found=False` guard.

**Status:** CONSTRUCTED. No source addresses this case; it follows from
entry 005's own logic once actually pressure-tested against an edge case,
which is the value a second review pass was meant to add.

---

### 2026-DD-007 — Removed the never-produced `other` dispute_type from the schema

**Context:** Found during a direct case-study/design-spec/code consistency
audit, not during either structured review pass. `DESIGN_SPECS.md`'s Intake
output schema listed `dispute_type` as
`enum[unrecognized_charge, unauthorized_transaction, duplicate_charge, other]`.
The actual `_classify_dispute_type` function in `intake.py` only ever
returns one of the first three, or `None` — it never produces the literal
string `"other"`. This was a schema-vs-implementation mismatch, not a
sequencing or dependency error, which is why neither review pass's
structured categories caught it — it required directly comparing the spec
document's claims against the code.

**Decision:** Corrected the documentation and code comments to state
plainly that this classifier produces exactly three named types or `None` —
`other` is not implemented. Did not add a rule to make `other` a real
output, since no source suggests one and doing so would be new invented
richness with no basis (the same reasoning that shaped entry 005's
alternatives).

**Note on Gate's defensive fallback:** Gate's threshold lookup still uses
`.get(dispute_type, DEFAULT_AUTO_LODGE_THRESHOLD)`, which would also catch
a literal `"other"` string if one were ever passed in directly (e.g. in a
unit test bypassing Intake) — this is left in place as cheap defensive
coding, not because `other` is an expected value from the actual pipeline.

**Status:** Documentation/schema correction, not a new design decision.
Recorded here anyway, per this project's own standard, rather than treated
as too small to log.
