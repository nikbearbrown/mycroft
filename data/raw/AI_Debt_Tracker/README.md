# AI Debt Tracker

The AI build-out is increasingly paid for with borrowed money. This agent keeps an always-up-to-date
ledger of every bond and loan that ~25 AI-sector companies (cloud, chips, data centres, power, AI
software) owe — principal, interest rate, due date — built from SEC filings as they appear, and turns
it into a quarterly signal for Mycroft: total debt, new borrowing, the maturity wall (how much falls
due in the next 12–24 months), and the average interest rate.

It is graded against each company's next quarterly report, which tags debt per instrument, and it
runs on local models only (Ollama on an 8 GB laptop GPU) — no paid APIs.

## Status

**Week 5 complete — 2026-11-13.** The tracker now runs whole episodes: for one company-quarter, a LangGraph graph
lists the filings in the window, triages them, reads every relevant filing in parallel (`Send`), merges the events,
sweeps matured bonds and applies the rest to the opening ledger, then self-checks the result. **All 95 dev episodes ran
end to end** (the week 5 check). Opening from B0's ledger (oracle start), the tracker's L1 bond recall is **97.8%**
against B0's 90.9% (+6.9 points, paired), and it caught **30 of 34 new bonds** that B0 cannot; its precision is
**90.2%** against 92.8%, because 26 of the bonds it added are not in the target report (P56–P58, logged). One engine
defect found by the first run was fixed on dev and both runs are reported (P55). Fresh checks, each labelled before
its run: **triage 15 of 15** (passes, after Week 4's 8 of 9), **answer key 3 of 4** gradable reports, **reader 91% vs
B1 74%** (B2 96%). Om Mali delegated Weeks 3, 4 and 5 in advance and has reviewed none of them
(`manifests/week3_gate.json`, `week4_gate.json`, `week5_gate.json`); labels, truth and transcriptions are Claude's model
judgment. Weeks 1–2 gates: `manifests/week1_gate.json`, `manifests/week2_gate.json`.

- [`docs/episodes.md`](docs/episodes.md) — full episodes on dev against B0; the Week 5 check.
- [`docs/reader.md`](docs/reader.md) — the event reader against B1 and B2, on a fresh set (Week 5) and Week 4's.
- [`docs/reader_truth.md`](docs/reader_truth.md) — what each of the 24 filings announces, labelled before any run.
- [`docs/triage_labels_w5.md`](docs/triage_labels_w5.md), [`triage_labels_w4.md`](docs/triage_labels_w4.md) — the fresh 50-filing triage sets (Weeks 5, 4).
- [`docs/triage.md`](docs/triage.md) — triage on all three labelled sets, and over the dev pool.
- [`docs/triage_labels.md`](docs/triage_labels.md) — Week 3's 50 labelled filings and why each label.
- [`docs/answer_key.md`](docs/answer_key.md) — the answer key for every report, with its anomalies.
- [`docs/baseline_b0.md`](docs/baseline_b0.md) — baseline B0 (carry forward) scored on dev.
- [`docs/handcheck.md`](docs/handcheck.md) — the grader against printed debt tables, with four held-out sets.
- [`docs/changes_dev.md`](docs/changes_dev.md) — which bond changes were announced in a filing.

- [`DESIGN.md`](DESIGN.md) — data sources, problems and fixes (P1–P58), agents, MCP servers,
  models, evaluation, ten-week plan.
- [`docs/feasibility.md`](docs/feasibility.md) — every go/no-go check with its pass line and result,
  including the Week 1 re-runs.
- [`docs/universe_v1_review.md`](docs/universe_v1_review.md) → [`universe_v1.json`](universe_v1.json)
  — measured grading level, subsidiaries and coverage for the 25 companies (frozen).
- [`manifests/`](manifests) — `generalisation.csv` (75 companies), `dev.csv` (95 episodes),
  `test.csv` (400 episodes), all frozen; `week1_gate.json` (who cleared it, and on what basis);
  `bakeoff_truth_corrections.json`.
- [`docs/answer_key_week1.md`](docs/answer_key_week1.md) — the answer key for 10 companies.
- [`docs/bakeoff.md`](docs/bakeoff.md), [`docs/bakeoff_set.md`](docs/bakeoff_set.md) — the model
  bake-off and its 29 documents, each checked.
- [`docs/worklog.md`](docs/worklog.md) — what was done, week by week.

## Where things live

The repo holds code, documents and small manifests. Everything bulky lives in a local directory
**outside the repo**, configured in `.env` (gitignored):

| What | Configured by | In git? |
|---|---|---|
| Code, docs, manifests, small fixtures | this folder | yes |
| Filing cache, SEC monthly notes zips, run outputs | `AI_DEBT_DATA` (optionally reached through a `data` link in this folder) | no |
| Python environment | `UV_PROJECT_ENVIRONMENT` | no |
| Package cache | `UV_CACHE_DIR` | no |
| Model weights (`qwen3:8b`, 4.9 GB) | `OLLAMA_MODELS` | no |

One-time setup (PowerShell, from this folder):

```powershell
Copy-Item .env.example .env        # then fill in EDGAR_NAME / EDGAR_EMAIL and the local paths
# optional: let scripts find the data directory without AI_DEBT_DATA set
New-Item -ItemType Junction -Path data -Target <your AI_DEBT_DATA directory>
```

The scripts read `.env` automatically (`scripts/_localenv.py`); variables already set in the shell
win.

**Running Ollama against the project's model directory.** Ollama reads `OLLAMA_MODELS` from its own
environment, so start it with that set:

```powershell
$env:OLLAMA_MODELS = "<your models directory>"; ollama serve
```

**Python environment** (uv, outside the repo through `UV_PROJECT_ENVIRONMENT`):

```powershell
$env:UV_PROJECT_ENVIRONMENT = "<your venv directory>"; $env:UV_CACHE_DIR = "<your uv cache>"
uv sync                      # Python 3.11+, installs mcp (<2), scipy, langgraph (+ SQLite checkpointer) and pytest
uv run pytest                # 166 offline tests: parser, matcher, answer key, grader, B0, edgar_pit's cut-off rule,
                             # document parsing and store, timeline, triage rules, value parsers, event reader, B1,
                             # ledger engine, self-checks, ledger server, the episode graph on fakes
```

## Reproducing Week 1

Run in this order; each step reads the previous one's output (`PYTHONPATH=scripts` lets the
scripts share helpers):

```powershell
$env:PYTHONPATH = "scripts"
uv run python -m ai_debt_tracker.eval.fsn 2024_07 2026_09 3   # SEC notes data -> debt subset (2.8 GB zips, ~10 min)
uv run python scripts/review_universe.py                        # -> universe_v1.json, docs/universe_v1_review.md
uv run python scripts/select_generalisation.py                  # -> manifests/generalisation.csv
uv run python scripts/build_splits.py                           # -> manifests/dev.csv, manifests/test.csv
uv run python scripts/load_answer_key.py                        # -> docs/answer_key_week1.md
uv run python scripts/f1_matching.py dev                        # F1 re-run
uv run python scripts/bakeoff.py build                          # -> docs/bakeoff_set.md
uv run python scripts/bakeoff.py run qwen3:8b                   # Ollama running (see above)
uv run python scripts/bakeoff.py run qwen3:4b
uv run python scripts/bakeoff.py report                         # -> docs/bakeoff.md
```

The frozen steps (`review_universe.py`, `select_generalisation.py`, `build_splits.py`) now refuse to
overwrite their outputs; `--refreeze` exists only for use with a new, logged gate decision.

## Reproducing Week 2

```powershell
$env:PYTHONPATH = "scripts"
uv run python -m ai_debt_tracker.eval.fsn 2024_01 2024_06 2     # earlier notes data (prior 10-Ks)
uv run python scripts/build_answer_key.py                       # -> docs/answer_key.md
uv run python scripts/score_baseline.py dev                     # -> docs/baseline_b0.md
uv run python scripts/handcheck.py grade                        # -> docs/handcheck.md (transcriptions in manifests/handcheck/)
uv run python scripts/explain_changes.py                        # -> docs/changes_dev.md
```

**The `edgar_pit` MCP server** (point-in-time EDGAR for the agent): one process per episode,
configured by the environment. It refuses the target report and anything accepted after it, and
logs every call to `$AI_DEBT_DATA/logs/edgar_pit_access.jsonl`. Start it from the episode's target
report — not from a timestamp, because EDGAR's acceptance times have moved by hours (P29):

```powershell
$env:EDGAR_PIT_TARGET = "<cik>:<target_adsh>"                   # both columns of manifests/*.csv
uv run python -m ai_debt_tracker.mcp_servers.edgar_pit          # stdio; tools: timeline, exhibits, fetch
```

## Reproducing Week 3

```powershell
$env:PYTHONPATH = "scripts"
uv run python scripts/build_answer_key.py                       # after the P35-P37 fixes
uv run python scripts/score_baseline.py dev
uv run python scripts/handcheck.py grade                        # incl. the fresh held-out set (HOLDOUT_W3)
uv run python scripts/explain_changes.py
uv run python scripts/triage_eval.py pool                       # every candidate filing in every dev window (~600)
uv run python scripts/triage_eval.py sample 3                   # the 50-filing labelled set; refuses once labelled
uv run python scripts/triage_eval.py run qwen3:4b               # Ollama running; rules first, model for the rest
uv run python scripts/triage_eval.py report qwen3:4b            # -> docs/triage.md, docs/triage_labels.md
```

**The `docs` MCP server** reads a filing as addressable pieces — headings `h3`, sentences `s12`,
tables `t2`, rows `t2.r4`, cells `t2.r4.c1` — so the agent cites ids instead of retyping numbers.
It is started like `edgar_pit` (same environment, same point-in-time rule: every document is opened
through `edgar_pit`, and the target report is refused). Document keys are
`<cik>/<accession>/<file name>`, the file name coming from `edgar_pit`'s `exhibits` tool:

```powershell
$env:EDGAR_PIT_TARGET = "<cik>:<target_adsh>"
uv run python -m ai_debt_tracker.mcp_servers.docs               # tools: sections, sentences, tables, search, span
```

## Reproducing Week 4

```powershell
$env:PYTHONPATH = "scripts"
uv run python scripts/build_answer_key.py                       # after the P38-P39 fixes
uv run python scripts/score_baseline.py dev
uv run python scripts/handcheck.py extract                      # fetches the fresh held-out reports (HOLDOUT_W4)
uv run python scripts/handcheck.py grade                        # graded once; transcriptions in manifests/handcheck/
uv run python scripts/explain_changes.py
uv run python scripts/triage_eval.py sample 4                   # the fresh labelled set; refuses once labelled
uv run python scripts/triage_eval.py run qwen3:4b               # -> $AI_DEBT_DATA/week4/
uv run python scripts/triage_eval.py report qwen3:4b            # -> docs/triage.md, triage_labels*.md
uv run python scripts/reader_eval.py dev reader                 # development on the bake-off documents only
uv run python scripts/reader_eval.py run b1                     # then b2, reader: once each, after the truth exists
uv run python scripts/reader_eval.py report                     # -> docs/reader.md, docs/reader_truth.md
```

The event reader (`graph/nodes/reader.py`) is a function of a filing's parsed documents; Week 5 wires it into
the episode graph.

## Reproducing Week 5

```powershell
$env:PYTHONPATH = "src;scripts"
uv run python scripts/build_answer_key.py                       # after the P41-P44 fixes
uv run python scripts/score_baseline.py dev
uv run python scripts/handcheck.py extract                      # the fresh held-out reports (HOLDOUT_W5)
uv run python scripts/handcheck.py grade                        # graded once
uv run python scripts/triage_eval.py sample 5                   # third fresh set, one copy per document; refuses once labelled
uv run python scripts/triage_eval.py run qwen3:4b               # -> $AI_DEBT_DATA/week5/
uv run python scripts/triage_eval.py report qwen3:4b
uv run python scripts/reader_eval.py run reader 5               # then b1, b2 (fresh set); `run reader 4` re-runs Week 4's set
uv run python scripts/reader_eval.py report
uv run python scripts/run_episodes.py run                       # every AI-25 dev episode; resumes from checkpoints
uv run python scripts/run_episodes.py score                     # -> docs/episodes.md (with B0, paired)
uv run python -m ai_debt_tracker.mcp_servers.ledger             # the ledger MCP server (stdio)
```

On an 8 GB laptop, start Ollama with `OLLAMA_NUM_PARALLEL=1` and `OLLAMA_MAX_LOADED_MODELS=1`, and run one model job at a
time: the first Week 5 run was stopped by the machine running low on memory and resumed from the saved episodes.

## Reproducing the feasibility numbers (Week 0)

```powershell
python scripts/probe_debt_filings.py                                  # filing counts, tagging detail
python scripts/spike_f1_f3_matching_and_headroom.py                   # F1 matching, F3 headroom
python scripts/spike_f2_f4_announcements_and_model.py qwen3:8b all    # F2 announcements, F4 model (Ollama running)
```
