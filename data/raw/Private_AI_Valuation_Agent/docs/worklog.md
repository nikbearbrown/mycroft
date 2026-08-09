# Worklog

Newest first.

---

## 2026-08-08 (later) — Bulk data verified; filter precision problem found

**Done**
- Wrote `src/ingest/download_bulk.py` (User-Agent, 10 req/s throttle, resumable via HTTP
  Range) and downloaded `2026q2_nport.zip` — 440.7 MB, 32 files, 5,347,869 holding rows.
  2026Q3 returns 404, confirming the publication lag.
- Wrote `scripts/check_bulk_vs_xml.py` and compared the bulk TSVs against the hand-verified
  filing data.

**Result: the bulk data matches the raw XML exactly — 15/15, 0 mismatches.**
`N/A` and `000000000` are both preserved verbatim, and ARK's incorrect
`IS_RESTRICTED_SECURITY='N'` is passed through rather than repaired. The largest open risk
from this morning is closed; the §2 filter correction carries over to the bulk unchanged.

**New problem: filter precision.** `plan.md` predicts "a few thousand" private rows per
quarter. Measured: the plan's filter keeps **606,028** rows (11.3% of the quarter) and the
corrected filter keeps 693,951. `CUSIP='N/A'` is the generic no-CUSIP placeholder used by
bonds, derivatives and cash equivalents — it is not a private-company marker.

**Decision — invert the pipeline.** Match the universe by issuer name *first*, then confirm
with `FAIR_VALUE_LEVEL=3`. `plan.md`'s filter-then-resolve order would feed 600k rows into
entity resolution; name-first reduces it to ~1,000/quarter. Anthropic is 149 rows.

**Two name-matching traps caught**
- `%COHERE%` matches **Coherent Corp** (public NYSE optics), 1,094 rows, 0 at Level 3. Real
  Cohere has no 2026Q2 presence. A substring matcher would have invented a whole price series.
- `%X.AI%` is mostly `X.AI LLC TL 1L BANKDEBT` and 144A bonds priced per $100 face. Only
  `x.AI, Inc.` (7 rows) is Level 3 equity.

**Fixture correction**
- Three positions were recorded under accession `0000035402-26-003312`; the bulk shows they
  belong to `0000035402-26-003406`. Transcription error on our side, not a data discrepancy.
  Fixed; comparison then ran clean at 15/15.

**Gate cleared — universe v1 frozen (Om Mali, 2026-08-08)**
- Full members (6): Databricks, SpaceX, Anthropic, OpenAI, Anduril, Cerebras.
- Carried thin (1): Figure AI — marks published, dispersion/propagation suppressed.
- Excluded (5): Cohere (false positive), xAI (instrument mismatch), Perplexity, Groq
  (insufficient coverage), Scale AI (no presence).
- Criterion: 28+ distinct filers per quarter, judged on Level 3 **equity** rows only.
- Changes from `plan.md`: SpaceX added, Cohere removed. Cerebras kept despite being the
  smallest member because its Level 3 → Level 1 IPO transition is the only external validity
  check the project has.
- Record: `universe_v1.json`; rationale in `docs/feasibility.md` §8.

**Also confirmed**
- Field definitions checked against `nport_readme.htm` bundled in the zip. Mapping matches
  `plan.md` (C.1.d, C.2.a, C.2.c, C.6, C.8). **Every field is nullable — including
  `FAIR_VALUE_LEVEL`**, which the filter now depends on, so `NULL` must be handled explicitly.
- `ISSUER_CUSIP` is a free-text `VARCHAR2(9)`, not a validated CUSIP — which is why
  placeholder spellings vary by filer.

**Open**
- Only 2026Q2 is loaded — no cross-quarter movement observed yet.
- Supabase provisioned but no schema created.
- Downloaded 2026Q2 rather than 2026Q1 as `plan.md` Week 1 specifies: Q2 is the quarter
  containing the May/June filings that were hand-verified, so it is the one that can confirm
  them. Q1 remains un-downloaded.

**Next**
- Freeze universe v1 (human gate).
- Ingest 8+ quarters and reconcile counts.
- Build `funds` / `filings` / `raw_holdings` and `DATABASE_SETUP.md`.

---

## 2026-08-08 — Week 1: verification complete, filter defect found

**Done**
- Hand-verified 19 Anthropic PBC positions across 6 fund families (Fidelity, T. Rowe Price,
  Alger, ARK, BlackRock, Capital Group) from `primary_doc.xml` on EDGAR.
- Confirmed four-manager convergence at $259.14 (2026-03-31 / 2026-04-30) and the repricing
  to $589.0095 (2026-05-29 / 2026-05-31).
- Scaffolded the project: `.gitignore`, `.env.example`, `requirements.txt`, `src/`, `docs/`,
  `tests/fixtures/`, `scripts/`.
- Created Supabase project; `DATABASE_URL` in local `.env` (not committed).
- Wrote `scripts/verify_week1_marks.py` — recomputes every price from the recorded fixture,
  so `docs/feasibility.md` is reproducible rather than transcribed.
- Wrote `docs/feasibility.md`.

**Decisions**
- Compare at the **company** level, not share class. Confirmed on first-party data: Fidelity,
  T. Rowe and Capital Group each marked every class they hold at one identical price, common
  and preferred alike.
- **`fairValLevel = 3` is the load-bearing filter field.** `isRestrictedSec` and `cusip` are
  supporting signals only.

**Blocker / defect**
- The private-position filter specified in `plan.md` (lines 106, 400) keeps only 1 of 6
  managers. `CUSIP='N/A'` misses the `000000000` placeholder, and `isRestrictedSec` is
  reported `N` by ARK and Capital Group on restricted stock. Replacement proposed in
  `docs/feasibility.md` §2. **Must be settled before Week 2 ingestion.**
- Three factual errors in `plan.md` logged in `docs/feasibility.md` §6.

**Open**
- Universe v1 not yet frozen — human gate.
- Whether the bulk DERA TSVs preserve the raw XML's placeholder values is untested and is
  the largest remaining risk.
- Corrected filter has 100% recall on the verified set; precision untested.

**Next**
- Download 2026Q1 bulk, confirm the 30-TSV layout, and check whether `CUSIP` and
  `IS_RESTRICTED_SECURITY` in `FUND_REPORTED_HOLDING` match the raw XML for these same six
  accessions. That single check de-risks Week 2.
- Freeze universe v1 with written per-company rationale.
