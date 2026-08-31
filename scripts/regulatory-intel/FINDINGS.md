# Regulatory Intelligence — Hardening Verification & Output Findings

**Date:** 2026-07-24 · **Workflow:** `workflow.dev.json` (hardened copy of Darshan's original) · **DB:** local `mycroft_intelligence` @ `localhost:5431`

How this was tested: the actual `Normalize Data` and `Keyword Analysis` code nodes were extracted from `workflow.dev.json` and run against the 5 live RSS feeds; the parameterized insert was exercised against the local DB in rolled-back transactions. Aggregate numbers were then cross-checked against the real n8n-produced rows in `regulatory_feeds` (authoritative — they agree).

> Caveat: the standalone harness uses a simplified regex RSS parse, so its per-source counts are *indicative*. The DB figures below are authoritative.

## 1. Fix verification — applied & working on live data

| Fix | Evidence | Status |
|---|---|---|
| A1 report path | `fileName` → local `scripts/regulatory-intel/reports/` | ✅ |
| A2 parameterized insert | 370 real items inserted (rolled back): **46 new, 324 dedup-skip, 0 errors**; nasty inputs (apostrophe/backslash/>255-char/RFC-822 date) bind cleanly | ✅ |
| A3 feed isolation | per-feed retry + `continueRegularOutput` on all 5 RSS nodes | ✅ |
| A4 HTML escape | `esc()` round-trips already-encoded entities, escapes raw Google-News anchors | ✅ |
| A5 timezone | `settings.timezone = America/New_York` | ✅ |
| A6 dup-detect | `Number.isInteger(id) && title` (rejects empty placeholder items) | ✅ |
| B1 recover empty-content | live filter: **OLD 297 → NEW 370 pass = +73 recovered** | ✅ |
| B4 threshold | report high-priority aligned to alert gate (`>7` → `>6`) | ✅ |

**Data integrity (sanity checks on 370 scored items):** 0 empty titles · every `urgency_score` in 1–10 · every `impact_level` in enum · no unexpected `source_feed` values. The fixes emit clean data.

**B1 recovered items are genuine signal** (previously dropped): `Cboe Clear U.S.`, `MEMX LLC`, `Nasdaq GEMX` SRO notices, `US v. Edwards LifeSciences` (DOJ antitrust). These are real SEC/exchange filings that arrive title-only.

## 2. Output-quality findings (the noise problem, measured)

Distributions from the real DB (`regulatory_feeds`, 411 rows at time of check):

- **Impact:** Medium **280** · High **98** · Critical **33**
- **Source feed:** Federal Register - Securities **157** · FINRA **101** · SEC **94** · Investment Advisor **38** · **Unknown Source 21**
- Live single-run urgency histogram: `{5:214, 6:45, 7:81, 8:6, 9:23, 10:1}` — **~58% of items floor at exactly 5** (the hardcoded baseline).

### C1 — keyword scorer misfires (INTENTIONALLY UNFIXED — this is the Layer-2 baseline)
The "Critical" bucket is led by noise:
- `Medicare Program: Hospital Outpatient Prospective Payment…` → **10/Critical**. Healthcare payment rule, no financial-regulatory relevance; scored top because the title contains "**Emergency** Medical Treatment" (`emergency` → +3).
- A **cluster of routine `Nasdaq … Notice of Filing and Immediate Effectiveness`** SRO filings → **9/Critical each**. Procedural boilerplate inflated to Critical purely by the word "**Immediate**" (`immediate` → +3).

Named false-positive patterns for the benchmark: **"Immediate Effectiveness"** and **"Emergency Medical Treatment"**.

### B2 — source classification (still open)
- **21 items = `Unknown Source`** — the classifier fell through entirely.
- **157 items dumped into `Federal Register - Securities`** regardless of actual issuing agency (non-financial rules included).

## 3. Implications for the plan
- **Layer 1 (hardening):** A1–A6/B1/B4 verified. Remaining: A7 (scope "Mark email sent"), B2 (classifier + 21 Unknown), B3 (Google URL unwrap), + apply A4/B4 to `Generate Email`.
- **Layer 2 (benchmark):** freeze the baseline on the post-B1 pipeline; the misfires above are ready-made labeled false-positives.
- **Layer 3 (LLM second-pass):** ecosystem convention is **local Ollama** (`Regulatory_QA` uses it); target the "Immediate/Emergency" misfire class.
- **Compatibility:** `Regulatory_QA` (FastAPI + RAG) reads this same `regulatory_feeds` table — check its `crud.py` before any schema/`source_feed` change (B2).
