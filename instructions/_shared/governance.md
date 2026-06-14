## Governance

Read `MYCROFT.md` (the constitution — principles, the verification stack, the recipe lifecycle, the logging rules) and `DOMAIN.md` (this project's index — layout and what is runnable today) before acting. If any file conflicts with `MYCROFT.md`, `MYCROFT.md` governs and the conflict is a bug — log it in `logs/RUN_LOG.md`.

The contract in brief (MYCROFT.md governs in full):

1. Verified local data before external lookup; stored scripts before ad-hoc code.
2. Never invent a count, rate, or confidence; label model judgments as judgments.
3. Gates are hard stops cleared by a named human and logged.
4. Machines verify conformance; humans verify adequacy.
5. Log meaningful runs, blockers, and artifacts in `logs/RUN_LOG.md`.
