# RUN_LOG — Insider Signal Intelligence

Append-only execution history (SNICKERDOODLE P7). Concrete, dated, attributed.
Newest entries at top.

---

## 2026-11-03 — INGEST built; live run on 2026 Q3

**Fellow:** Gomathy S.
**Recipe:** insider-signal-agent v0.1.0 (DRAFT)

**Built:** `ingest.py` (stdlib only): SEC_USER_AGENT required (name + email), 1 req/s
default, rates >= 10/s refused, ZIP URLs read from SEC's data-set page, manifest with
SHA-256, request log, checkpoint/resume via `.part` + hash, backoff then halt on 403/429/5xx,
safe extraction. `tests/test_ingest.py`: 33 unittest tests, no network. All pass.

**Live run (real data):** `python ingest.py --quarters 2026q3`, User-Agent set (value not logged).
- 2 requests to SEC (data-set page, ZIP), both HTTP 200, started 1.005 s apart.
- `2026q3_form345.zip`: 8,660,776 bytes, SHA-256 `a4e6a681cfcfa43a3d9e4ca9cfec1fd26a59d0a01eac7e9f7b5a0122092c90f3`.
- Extracted 8 TSVs + SEC's metadata JSON and readme HTM.
- Re-run: skipped (hash matched), 0 requests.

**G1 check:** `python ingest.py --quarters 2026q3 --verify` → PASS. G1 itself is not
cleared; that requires the full study period and the owner's logged decision.

**Resolved [verify] items (from the 2026 Q3 file, read locally):**
- `AFF10B5ONE` exists in SUBMISSION; values `0` (22,834), `false` (6,314), `1` (3,798),
  `true` (1,237), blank (3,969). PARSE must normalize them; blank = unknown.
- `RPTOWNER_RELATIONSHIP` is comma-separated and mixed case (e.g. `Director,Officer`), not the
  readme's uppercase.
- The file header says `FORM3_HOLDINGS_REPORTED`; the readme says `FORM3_HOLDING_REPORTED`.

**Raw counts (before any filter):** NONDERIV_TRANS 59,885 records, of which 5,184 have `TRANS_CODE = P`.

**Changed:** recipe (manifest field `user_agent` → `user_agent_set`, AFF10B5ONE note),
DATA_CONTRACT (resolved [verify] items, extracted file list), fixture rebuilt from real headers.

---

## 2026-11-03 — TODO closure batch: study period, G6 reviewer

**Fellow:** Gomathy S. · **Decided by:** Gomathy S.
**Recipe:** insider-signal-agent v0.1.0 (DRAFT)

- [TODO: DEFINE] Study period → **2023 Q1 – 2026 Q3**. Reason: SEC's 10b5-1 flag (`AFF10B5ONE`) exists for 2023+ data.
- [TODO: APPROVE] G6 reviewer → **Gomathy S. (self-attestation during development; external review pending)**.
  Attestations and reports must state they are self-attested until an external reviewer is named.

**Result:** `todos_open` 12 → 10.

---

## 2026-11-03 — Module scaffold (spec only)

**Fellow:** Gomathy S.
**Recipe:** insider-signal-agent v0.1.0 (DRAFT)

**Built:** README, _MANIFEST, DATA_CONTRACT, status, requirements, recipe, empty `tests/`.
**Checked:** SEC's Insider Transactions Data Sets page and readme PDF (coverage, tables,
fields, Trans Code List) and SEC's "Accessing EDGAR Data" fair-access rules, on 2026-11-03.
**Runs against real data:** none.
**Open:** 12 recipe TODOs at scaffold time; 2 `[verify]` items (AFF10B5ONE column, RPTOWNER_RELATIONSHIP format).
