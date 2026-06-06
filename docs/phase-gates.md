# Phase Gates

Automation expands only after explicit gates pass.

## Standard Gates

1. Problem gate: the task, scope, and success condition are explicit.
2. Local evidence gate: relevant local data, docs, and recipes have been checked.
3. Stored script gate: existing scripts have been checked before writing ad hoc
   automation.
4. Small-run gate: the smallest useful test has passed before broad execution.
5. Verification gate: outputs have been checked against inputs or expected
   contracts.
6. Review gate: a human review path exists for risky, ambiguous, or high-impact
   results.
7. Logging gate: meaningful runs are recorded in `logs/RUN_LOG.md` or a
   nearby audit/report.

If a gate has no failure path, it is not a gate.

## Failure Paths

- If the problem is unclear, stop and restate it before acting.
- If local evidence is missing, mark it as missing; do not invent it.
- If no stored script exists, document that before creating one.
- If the small run fails, fix or narrow the workflow before scaling.
- If verification is inconclusive, keep the result provisional.
- If review is required, do not present output as final.
- If logging is skipped, the run should not be treated as durable evidence.

## High-Risk Work

Financial, legal, medical, HR, regulatory, publishing, deletion, and committing
work require stricter gates. For those tasks, include a human review point and a
clear rollback or correction path.
