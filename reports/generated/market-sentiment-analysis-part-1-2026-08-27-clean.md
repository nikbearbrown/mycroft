# Market Sentiment Analysis - Part 1 — 2026-08-27

**Run:** `sample-001` · **Mode:** `sample` · **Fixture set:** `clean` · **Frozen clock:** `2026-08-27T14:30:00+00:00`

**Reader:** compliance or audit reviewer who must reconstruct how any score was produced.

**Decision enabled:** approve the run for the next phase, request source/schema fixes, or block live execution.

> **Nothing here is a market observation.** The fixture set is synthetic; ticker `FAKE` does not exist. No live call, external write, or model call was performed.

---

## Run summary

Six of six steps ran against the `clean` fixture set. 10 row(s) were seen and 10 passed shape validation; the run produced an overall sentiment of **64/100 (SLIGHTLY BULLISH)**, which is a heuristic score and not a measurement.

## Purpose

Market Sentiment Analysis - Part 1 collects news, price, and social signals and asks whether the available local evidence is sufficient for a human decision, without unapproved external writes or unsupported analytical claims.

## Source inventory

Every file this run rests on, with the hash a reviewer can re-verify.

| Path | Role | Present | SHA-256 (first 16) |
|---|---|---|---|
| `recipes/market-sentiment-analysis-part-1.md` | recipe under test - authoritative for intent (P6) | yes | 14bb8f811a02a9f5… |
| `conductor/market-sentiment-analysis-part-1.md` | conductor flow | yes | 02681428081972d1… |
| `data/raw/market-sentiment-analysis-part-1/run-envelope.json` | run control file - declares mode and the frozen clock | yes | 33828ed47a8c38fc… |
| `data/raw/market-sentiment-analysis-part-1/sample/fixture-manifest.json` | fixture manifest - schema and defect catalogue | yes | 7ee88528523d5780… |
| `data/raw/market-sentiment-analysis-part-1/sample/FIXTURE_MANIFEST.md` | fixture manifest, human view (P5) | yes | 7033d7e4fd68306b… |
| `data/raw/market-sentiment-analysis-part-1/sample/clean/news-finnhub.json` | source fixture - news stream | yes | 441291ec39aed12c… |
| `data/raw/market-sentiment-analysis-part-1/sample/clean/price-alpha-vantage.json` | source fixture - price stream | yes | a7d3c58fdf0a388b… |
| `data/raw/market-sentiment-analysis-part-1/sample/clean/reddit-wallstreetbets.json` | source fixture - reddit stream | yes | 6df0b3e31e6f08af… |
| `data/raw/market-sentiment-analysis-part-1/runs/sample-001-clean/news-finnhub.json` | step-2 raw output | yes | 3f50bf072a20e622… |
| `data/raw/market-sentiment-analysis-part-1/runs/sample-001-clean/price-alpha-vantage.json` | step-2 raw output | yes | ceb9c6f531462079… |
| `data/raw/market-sentiment-analysis-part-1/runs/sample-001-clean/reddit-wallstreetbets.json` | step-2 raw output | yes | b067b3b61d694e14… |
| `data/verified/market-sentiment-analysis-part-1/runs/sample-001-clean/news-finnhub.json` | verified output (step 3 or 4) | yes | 0426c978df6dc6ac… |
| `data/verified/market-sentiment-analysis-part-1/runs/sample-001-clean/price-alpha-vantage.json` | verified output (step 3 or 4) | yes | 7b36b2220877b9e8… |
| `data/verified/market-sentiment-analysis-part-1/runs/sample-001-clean/quality-checked/news-finnhub.json` | verified output (step 3 or 4) | yes | 9f34975eddd7fd8c… |
| `data/verified/market-sentiment-analysis-part-1/runs/sample-001-clean/quality-checked/price-alpha-vantage.json` | verified output (step 3 or 4) | yes | a983e5e65fc688f3… |
| `data/verified/market-sentiment-analysis-part-1/runs/sample-001-clean/quality-checked/reddit-wallstreetbets.json` | verified output (step 3 or 4) | yes | a7f06bd4857a79ce… |
| `data/verified/market-sentiment-analysis-part-1/runs/sample-001-clean/reddit-wallstreetbets.json` | verified output (step 3 or 4) | yes | 4bc69f0b35ba5e38… |
| `logs/market-sentiment-analysis-part-1/runs/sample-001-clean/sentiment-scores.json` | step-5 sentiment scores | yes | 3bdfdce2a9a3ffef… |
| `scripts/tools/market-sentiment-analysis-part-1-verify-provenance.py` | step script | yes | 718a29747223925c… |
| `scripts/ingest/market-sentiment-analysis-part-1-ingest-inputs.py` | step script | yes | f558f93393a1177e… |
| `scripts/gigo/market-sentiment-analysis-part-1-validate-data-shape.py` | step script | yes | bc83ad6ad643d1dd… |
| `scripts/gigo/market-sentiment-analysis-part-1-transform-quality-check.py` | step script | yes | 2cc69f0e1f81ee86… |
| `scripts/tools/market-sentiment-analysis-part-1-run-approved-tools.py` | step script | yes | edb664608bbd2b21… |
| `scripts/tools/market-sentiment-analysis-part-1-produce-human-report.py` | step script | yes | 3e65b2eb4117ced4… |

## Inputs used

| Input | Value |
|---|---|
| Run envelope | `data/raw/market-sentiment-analysis-part-1/run-envelope.json` |
| Declared mode | `sample` |
| Fixture set | `clean` |
| Frozen clock (only clock any step reads) | `2026-08-27T14:30:00+00:00` |
| Raw run directory | `data/raw/market-sentiment-analysis-part-1/runs/sample-001-clean` |
| Shape-validated directory | `data/verified/market-sentiment-analysis-part-1/runs/sample-001-clean` |
| Quality-checked directory | `data/verified/market-sentiment-analysis-part-1/runs/sample-001-clean/quality-checked` |
| Step-5 scores | `logs/market-sentiment-analysis-part-1/runs/sample-001-clean/sentiment-scores.json` |

## Phase-gate results

An audit reports what it found; it does not say "pass". Every gate below is cleared by a named human, not by this script.

| Gate | Capacity | Evidence observed | Blocking | Cleared by |
|---|---|---|---|---|
| 1 — Source gate | [TO] | 24 declared sources present and hashed | none | _awaiting_ |
| 2 — Scope gate | [PF] | envelope declares mode='sample', fixture_set='clean', frozen_clock=2026-08-27T14:30:00+00:00 | none | _awaiting_ |
| 3 — Data-shape gate | [PA] | 6 verified artifact(s) written; 0 JSON file(s) failed to parse | none | _awaiting_ |
| 4 — Script-readiness gate | [IJ] | 6 of 6 step scripts exist | none | _awaiting_ |
| 5 — Approval gate | [EI] | approval record absent at logs/gate-decisions/market-sentiment-analysis-part-1-approval.json; no live call, external write, or model call was performed | **1** | _awaiting_ |
| 6 — Report gate | [TO] | agent log and human report written by this step; section and field coverage listed below | none | _awaiting_ |

- **Gate 4 caveat:** This gate as written is satisfiable by doing nothing: it passes if the script exists OR if the [TODO: DEV] text is still in the recipe. Both are currently true.

## Steps completed

| # | Step | Script | Exists |
|---|---|---|---|
| 1 | Verify provenance | `scripts/tools/market-sentiment-analysis-part-1-verify-provenance.py` | yes |
| 2 | Ingest declared inputs | `scripts/ingest/market-sentiment-analysis-part-1-ingest-inputs.py` | yes |
| 3 | Validate data shape | `scripts/gigo/market-sentiment-analysis-part-1-validate-data-shape.py` | yes |
| 4 | Transform and quality check | `scripts/gigo/market-sentiment-analysis-part-1-transform-quality-check.py` | yes |
| 5 | Run approved tools | `scripts/tools/market-sentiment-analysis-part-1-run-approved-tools.py` | yes |
| 6 | Produce human report | `scripts/tools/market-sentiment-analysis-part-1-produce-human-report.py` | yes |

## Records seen

| Stream | Declared by source | Recounted | Passed shape | After dedup |
|---|---|---|---|---|
| news | 5 | 5 | 5 | 5 |
| price | 1 | 1 | 1 | 1 |
| reddit | 4 | 4 | 4 | 4 |

## Rejects

_None._

## Duplicates

Counting rule: every occurrence of an identity key beyond the first.

_None._

## Flags

Stale and wrongly-typed rows are flagged and **kept**, never silently dropped or coerced.

_None._

### Scoring-step flags

Substitutions the ported arithmetic made, each of which changes what the score means.

| Flag | Where | Why it matters |
|---|---|---|
| scoring_params_unattributed | `run` | the weights, thresholds and keyword lists have no recorded author |
| untested_threshold_path | `reddit` | a branch in the original that this corpus cannot exercise |
| ticker_not_derived_from_question | `run` | no question-parsing step exists in this recipe, so the ticker comes from the price rows |

## Typed TODOs

| Type | Item | Closed by | Status |
|---|---|---|---|
| DEFINE | scoring_params v1.0.0 constants are unattributed | human | OPEN |
| APPROVE | Gate 5 approval for the model, Slack, and email calls | human | OPEN |
| DEFINE | No type contract exists in the declared schema | human | OPEN |
| DEFECT | Step 3's output contract has no field for a type violation | human | OPEN |
| DEFECT | Report reader mismatch | human | OPEN |
| DEFECT | reports/templates/ contradicts the recipe on the log path | human | OPEN |
| DEFECT | Gates 4 and 5 are satisfiable by doing nothing | human | OPEN |
| DEV | Live mode is unimplemented | AI, after gate 5 | OPEN |
| DEV | Recipe lifecycle frontmatter is absent | human | OPEN |

- **[DEFINE] scoring_params v1.0.0 constants are unattributed** — The weights (price .4 / news .3 / social .3), the label thresholds (65/55/45/35) and both keyword lists appear in the source workflow with no derivation, backtest, or author. They are reproduced, not endorsed.

- **[APPROVE] Gate 5 approval for the model, Slack, and email calls** — Step 5 rendered three live-call handoffs with approved_for_live_action=false. Each needs a logged gate decision and a named approver before it runs.

- **[DEFINE] No type contract exists in the declared schema** — fixture-manifest.json declares required fields, identity keys and freshness windows but no value types. Step 4 carries a step-scoped TYPE_CONTRACT table as the closure; it is not a promoted schema and belongs in DATA_CONTRACT.md.

- **[DEFECT] Step 3's output contract has no field for a type violation** — Its declared fields are record_count, required_fields_present, missing_fields, parse_errors, schema_version. A wrong-typed value is none of them, so D02/D11/D17 surface in step 4 flags instead. The recipe should add type_errors to step 3 or state that type checking belongs to step 4.

- **[DEFECT] Report reader mismatch** — The recipe names the reader as "domain lead or human boss". This report is written for the stricter reader a compliance or audit reviewer represents, and carries per-score trace chains and artifact hashes accordingly. The recipe line was not edited -- that is a recipe change and out of scope.

- **[DEFECT] reports/templates/ contradicts the recipe on the log path** — reports/templates/market-sentiment-analysis-part-1.md cites logs/market-sentiment-analysis-part-1/[RUN_ID].json; the recipe Output Contract and the gate-6 test cite logs/market-sentiment-analysis-part-1-[DATE].json. The recipe governs; the template is wrong and untouched.

- **[DEFECT] Gates 4 and 5 are satisfiable by doing nothing** — Each passes if its artifact exists OR if the typed TODO text is still present in the recipe. A gate with no failure path is not a gate.

- **[DEV] Live mode is unimplemented** — Step 2 stops in live mode. Real fetchers need credentials from the environment (ALPHA_VANTAGE_API_KEY, FINNHUB_API_KEY, REDDIT_USER_AGENT) plus 401/403/429/timeout/empty-200 handling that the fixture corpus explicitly does not cover.

- **[DEV] Recipe lifecycle frontmatter is absent** — The recipe carries no status/todos_open/last_gate/attestation/recipe_version block, so its lifecycle stage cannot be stated. The six [TODO: DEV] markers also still stand even though all six scripts now exist.

## Human approvals

| Approval | Required for | Record | Status |
|---|---|---|---|
| Gate 5 — live/model calls | Anthropic, Slack, email | `logs/gate-decisions/market-sentiment-analysis-part-1-approval.json` | **absent — all three blocked** |
| Attestation | promotion to VERIFIED | — | not recorded |

No live call, external write, or model call was performed by this run.

## Verified findings

Facts a record supports. Counts are recomputed, never copied from an envelope.

| Finding | Kind | Basis |
|---|---|---|
| news: 5 row(s) seen, 5 promoted, 0 withheld on shape | record count, recomputed | `data/verified/market-sentiment-analysis-part-1/runs/sample-001-clean/news-finnhub.json` |
| price: 1 row(s) seen, 1 promoted, 0 withheld on shape | record count, recomputed | `data/verified/market-sentiment-analysis-part-1/runs/sample-001-clean/price-alpha-vantage.json` |
| reddit: 4 row(s) seen, 4 promoted, 0 withheld on shape | record count, recomputed | `data/verified/market-sentiment-analysis-part-1/runs/sample-001-clean/reddit-wallstreetbets.json` |

## Inferred findings

Judgments, kept separate from the verified findings above (P3, P8). **The sentiment score belongs here, not above.**

- **Overall sentiment 64/100 (SLIGHTLY BULLISH) for ticker FAKE** — _heuristic score - NOT a market observation_
  - Method: keyword counts combined by scoring_params v1.0.0 (price .4 / news .3 / social .3)
  - Why inferred: The score is arithmetic over keyword matches using weights and thresholds with no recorded author. It is not a measurement and not a recommendation.
  - Caveats: scoring_params_unattributed, ticker_not_derived_from_question, untested_threshold_path
- **news component score 70/100** — _heuristic component score_
- **social component score 62/100** — _heuristic component score_
- **price component score 60/100** — _heuristic component score_

### How to reconstruct the score

Scoring parameters, reproduced so the arithmetic can be recomputed by hand:

| Parameter | Value |
|---|---|
| Version | `1.0.0` |
| Ported from | `Aggregate & Calculate Sentiment` |
| Attribution | **none recorded** — see typed TODOs |
| Weights | `{"news": 0.3, "price": 0.4, "social": 0.3}` |
| Label thresholds | `{"BEARISH": 35, "BULLISH": 65, "SLIGHTLY BEARISH": 45, "SLIGHTLY BULLISH": 55}` |
| News formula | `(positive − negative) / total_rows × 50 + 50` |
| Overall formula | `price*0.4 + news*0.3 + social*0.3, rounded` |

Trace chain — every row that moved the score, back to a byte range in a named file:

| Stream | Raw locator | Source file | Source SHA-256 (first 16) | Fetched at |
|---|---|---|---|---|
| news | `records[0]` | `news-finnhub.json` | 441291ec39aed12c… | 2026-08-27T14:30:00+00:00 |
| news | `records[1]` | `news-finnhub.json` | 441291ec39aed12c… | 2026-08-27T14:30:00+00:00 |
| news | `records[2]` | `news-finnhub.json` | 441291ec39aed12c… | 2026-08-27T14:30:00+00:00 |
| news | `records[3]` | `news-finnhub.json` | 441291ec39aed12c… | 2026-08-27T14:30:00+00:00 |
| news | `records[4]` | `news-finnhub.json` | 441291ec39aed12c… | 2026-08-27T14:30:00+00:00 |
| price | `records[0]."Global Quote"` | `price-alpha-vantage.json` | a7d3c58fdf0a388b… | 2026-08-27T14:30:00+00:00 |
| reddit | `records[0].data.children[0].data` | `reddit-wallstreetbets.json` | 6df0b3e31e6f08af… | 2026-08-27T14:30:00+00:00 |
| reddit | `records[0].data.children[1].data` | `reddit-wallstreetbets.json` | 6df0b3e31e6f08af… | 2026-08-27T14:30:00+00:00 |
| reddit | `records[0].data.children[2].data` | `reddit-wallstreetbets.json` | 6df0b3e31e6f08af… | 2026-08-27T14:30:00+00:00 |
| reddit | `records[0].data.children[3].data` | `reddit-wallstreetbets.json` | 6df0b3e31e6f08af… | 2026-08-27T14:30:00+00:00 |

## Decision recommendation

**Recommended:** approve the sample run for the next phase

No rejects and no quality flags on this run. Live execution remains blocked by gate 5.

| Option | Available |
|---|---|
| approve the run for the next phase | yes |
| request source or schema fixes | yes |
| block live execution | yes |

**Live execution:** BLOCKED - no gate-5 approval record exists and no live call was made

_This is a recommendation, not a decision. Adequacy is the human gate (P1)._

---

_Generated by `scripts/tools/market-sentiment-analysis-part-1-produce-human-report.py` (step 6 of 6)._
