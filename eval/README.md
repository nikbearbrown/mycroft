# eval/ — Does the instruction scaffolding actually help?

The §19 answer: **treat the instruction/context files as measurable artifacts, not
assumed goods.** It turns "does `AGENTS.md` / `SNICKERDOODLE.md` / `_MANIFEST.md` improve
agent behavior?" into a number you can compare across configurations.

Mirrors MYCROFT's labor split: **machines verify conformance** (the scorer computes
deterministic metrics) and **humans verify adequacy** (you grade acceptance/burden).

## What it measures

A fixed **task suite** (`tasks/`) run under a **config matrix** (`configs.yaml`):
`full` (everything present) · `manifest-only` (only `_MANIFEST.md`) · `baseline`
(no instruction files). For each task × config × tool, one run. The scorer records,
**deterministically**: out-of-scope edits, deletes, forbidden ops (`rm -rf`,
force-push, staging `data/private/`), diff size, and (with `--validate`) the task's
own check. You record, **by hand**: acceptance (pass/partial/fail), manual edits
after, review burden (1–5), tokens (if reported), notes.

`report.mjs` aggregates into `results/scorecard.md` grouped by config — so you can
see whether `full` beats `baseline`, and **prune rules that don't earn their tokens.**

## Protocol (one run)

Runs are **disposable** — do them on a scratch branch/stash, score from the patch,
then discard. Nothing here lands in `main`.

1. **Pick a config.** For `baseline` / `manifest-only`, move instruction files aside
   first (and restore after) — use `git mv`, never `rm`:
   ```bash
   mkdir -p eval/.config-stash
   git mv AGENTS.md CLAUDE.md SNICKERDOODLE.md _MANIFEST.md eval/.config-stash/   # baseline
   # …run the task…
   git mv eval/.config-stash/* .                                            # restore
   ```
2. **Run the task.** Paste `tasks/<id>.md`'s prompt block into the agent on a scratch branch.
3. **Capture the change:** `git add -A && git diff --cached > eval/runs/<DATE>__<task>__<config>__<tool>/changes.patch ; git reset`. Add a `run.yaml` (see an existing run) and optionally `commands.log`.
4. **Score:** `npm run eval:score -- eval/runs/<DATE>__<task>__<config>__<tool>` (add `--validate` to run the task's check if the change is applied).
5. **Grade adequacy:** fill the `human:` block in that `metrics.yaml`.
6. **Aggregate:** `npm run eval:report` → `eval/results/scorecard.md`.

Repeat across configs/tools for the same tasks. The comparison is the point.

## Honest scope

The scorer and aggregator are fully automated. **Executing the agent is not** — that
step needs each tool installed and (for live runs) API access, matching §19's own
cross-tool process. Start with `full` vs `baseline` on your primary tool; even n=5
per config tells you whether the scaffolding is paying for itself.
