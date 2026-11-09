# Feasibility — Week 1

**Verified by:** Om Mali · **Dates:** 2026-08-07 / 2026-08-08
**Method:** every position below was read by hand from `primary_doc.xml` on EDGAR and the
arithmetic done manually, then re-derived programmatically by
`scripts/verify_week1_marks.py` against `tests/fixtures/week1_verified_marks.json`.
No figure in this document was inherited from `plan.md`.

**Scope:** one company (Anthropic PBC), 19 positions, 6 fund families, 4 period ends.

---

## 1. What was verified

### The core claim holds

Private AI company share prices are recoverable from N-PORT as `valUSD / balance`, and
independent managers agree closely.

| Period end | Managers | Price per share | Spread |
|---|---|---|---|
| 2026-03-31 | Fidelity, T. Rowe Price | $259.1400 / $259.1364 | 0.0014% |
| 2026-04-30 | Alger, ARK | $259.1364 / $259.1400 | 0.0014% |
| 2026-05-29 | BlackRock | $589.0095 | — |
| 2026-05-31 | Capital Group | $589.0095 | — |

**Four independent managers priced Anthropic identically to the cent** at the March/April
observation, then a new round repriced it and **BlackRock and Capital Group landed on the
same number to four decimal places**, two days apart, with no contact between them.

The 0.0014% spread is a rounding convention, not disagreement: Fidelity and ARK carry the
mark at $259.14; T. Rowe and Alger carry it at $259.1364. Same underlying round price.

### The stagger is real

Period ends observed: 3/31, 4/30, 4/30, 5/29, 5/31. Four distinct observation dates across
two months from six managers. **Propagation is observable**, which is the project's
distinctive claim.

### The repricing event is visible

$259.14 → $589.0095 is a 2.27x move, captured between 2026-04-30 and 2026-05-29. This is
the kind of event the propagation analysis is built to measure.

---

## 2. Finding: the private-position filter in `plan.md` is wrong

**This is the week's most consequential result and it blocks Week 2.**

`plan.md` line 106 and line 400 specify:

```sql
IS_RESTRICTED_SECURITY = 'Y' AND FAIR_VALUE_LEVEL = 3 AND CUSIP = 'N/A'
```

Applied to the 19 verified positions, that filter keeps **10 rows from 1 manager**.

| Manager | `isRestrictedSec` | `fairValLevel` | `cusip` | Survives |
|---|---|---|---|---|
| Fidelity | `Y` | `3` | `N/A` | ✅ |
| T. Rowe Price | `Y` | `3` | `000000000` | ❌ |
| Alger | `Y` | `3` | `000000000` | ❌ |
| ARK | `N` | `3` | `000000000` | ❌ |
| BlackRock | `Y` | `3` | `000000000` | ❌ |
| Capital Group | `N` | `3` | `N/A` | ❌ |

The filter deletes five of six managers — silently, with no error — and with them the entire
cross-manager comparison the project exists to produce.

**Two independent defects:**

1. **`CUSIP = 'N/A'` is too narrow.** Filers use `N/A` *or* `000000000` as the
   no-CUSIP placeholder. Both appeared here; other variants may exist.
2. **`isRestrictedSec` is not trustworthy.** ARK and Capital Group both report `N` on
   Anthropic preferred stock that is unambiguously restricted. It cannot be an `AND` gate.

**`fairValLevel = 3` was constant across all 19 rows and all 6 filers.** It is the only
field that held.

### Proposed replacement

```sql
FAIR_VALUE_LEVEL = 3
AND (CUSIP IN ('N/A','000000000','0','') OR CUSIP IS NULL OR IS_RESTRICTED_SECURITY = 'Y')
```

Recall on the verified set: 19/19, 6/6 managers. **Precision is untested** — see §5.

---

## 3. Finding: the write-up-all-classes convention is confirmed

Every manager holding multiple share classes marked them all at one price:

| Manager | Classes held | Price |
|---|---|---|
| Fidelity | Series E, F, G | all $259.1400 |
| T. Rowe Price | Ser F-1, G-1 | all $259.1364 |
| Capital Group | CL F-1, CL G-1, common | all $589.0095 |

Common stock and preferred stock carry the identical mark (Capital Group). This reproduces
Gornall & Strebulaev on this cohort: funds write up all classes to the latest round price
and ignore liquidation preference. The marks are therefore comparable across classes — and
economically wrong in a known, documented direction.

**Design consequence:** company-level comparison is justified, as `plan.md` §"Trap 2"
argues. This observation supports that decision with first-party evidence.

---

## 4. Finding: entity resolution is as hard as budgeted

One company, 19 rows, and:

- **11 distinct title strings**, 5 distinct issuer-name strings
- **LEI present on only 3 of 6 managers** — ARK, Alger and BlackRock report `N/A`, despite
  Anthropic having LEI `984500B6DEB8CEBC4Z70`
- **`assetCat` is unreliable** — Alger and ARK tag preferred stock as `EC` (common)
- **Internal identifiers do not join** — Fidelity `LKV546000`, T. Rowe `TC0OOVXB7`,
  ARK `PPANTHROP`, Capital Group `ECA408707`
- **Name variants** — `ANTHROPIC PBC`, `Anthropic PBC`, `Anthropic, Inc.`,
  `Anthropic PBC SER F-1 CVT PFD PP`

The ARK row is the single hardest observed case and is case #1 of the golden set: wrong
entity name, no LEI, wrong `assetCat`, wrong `isRestrictedSec`, placeholder CUSIP.

The 30–40% time budget for entity resolution is supported. The problem is bounded, though:
~9 companies × ~20 fund families is a few hundred distinct combinations, not millions.

---

## 5. The bulk data matches the raw XML exactly

**The largest open risk is closed.** Downloaded `2026q2_nport.zip` (440.7 MB, 32 files,
`FUND_REPORTED_HOLDING.tsv` at 910 MB) and compared it against the hand-verified positions:

```
exact matches to hand-verified XML: 15   mismatches: 0
```

Every field survives the DERA pipeline verbatim. `N/A` stays `N/A`; `000000000` stays
`000000000`; ARK's incorrect `IS_RESTRICTED_SECURITY = N` is preserved rather than repaired.
**The bulk data can be trusted to behave like the filings**, so the filter logic derived in
§2 carries over unchanged.

The comparison also corrected a transcription error in our own fixture: three positions
(balances 14,900 / 46,814 / 33,200) were recorded under accession `0000035402-26-003312`;
they belong to `0000035402-26-003406`. Both are Fidelity filings at $259.14. Fixed in
`tests/fixtures/week1_verified_marks.json`.

### Schema confirmed against the bundled reference

`nport_readme.htm` (shipped inside the zip) confirms the field-to-item mapping `plan.md`
assumed:

| Column | Definition | Type | Nullable | Item |
|---|---|---|---|---|
| `ISSUER_CUSIP` | CUSIP | `VARCHAR2(9)` | **Y** | C.1.d |
| `BALANCE` | Balance | `NUMBER(36,12)` | **Y** | C.2.a |
| `CURRENCY_VALUE` | Value | `NUMBER(36,12)` | **Y** | C.2.c |
| `IS_RESTRICTED_SECURITY` | Is the investment a Restricted Security | `CHAR(1)` | **Y** | C.6 |
| `FAIR_VALUE_LEVEL` | Level within the fair value hierarchy per US GAAP | `VARCHAR2(10)` | **Y** | C.8 |

**Every field is nullable, including `FAIR_VALUE_LEVEL`** — the one field the filter now
depends on. Any filter must handle `NULL` explicitly rather than relying on `= '3'` to be
well-defined. `ISSUER_CUSIP` is a free-text `VARCHAR2(9)`, not a validated CUSIP, which is
why placeholder spellings vary by filer.

### But the filter has a precision problem `plan.md` did not anticipate

| | rows in 2026Q2 | share of quarter |
|---|---|---|
| all holding rows | 5,347,869 | 100% |
| `FAIR_VALUE_LEVEL = 3` | 713,956 | 13.35% |
| `IS_RESTRICTED_SECURITY = 'Y'` | 834,283 | 15.60% |
| `CUSIP = 'N/A'` | 1,169,603 | 21.87% |
| **`plan.md` filter (3-field AND)** | **606,028** | **11.33%** |
| **corrected filter (§2)** | **693,951** | **12.98%** |

`plan.md` line 401 predicts "10-15M rows/qtr in, **a few thousand out**." The real numbers
are 5.3M in and **606,028 out** — off by roughly two orders of magnitude.

The cause: `CUSIP = 'N/A'` is the standard placeholder for *anything without a CUSIP* —
bonds, derivatives, cash equivalents, foreign securities — not a private-company marker. And
Level 3 is full of illiquid debt. Neither field, alone or together, isolates private
operating companies.

**Design consequence — the pipeline must invert.** `plan.md`'s architecture filters to
private positions and *then* resolves entities, which would feed 600,000 rows into entity
resolution. Instead: **match the universe by issuer name first, then confirm with
`FAIR_VALUE_LEVEL = 3`.** Anthropic is 149 rows in the quarter, not 600,000. This makes the
project's hardest component roughly 500x smaller.

## 6. What was NOT tested

- **Any period before 2026-03-31.** Historical depth for this cohort is assumed, not shown.
  Only 2026Q2 has been downloaded.
- **Split detection.** The Perplexity 12x case was not reproduced. SpaceX's 10x unit artifact
  *is* visible (price range $204.64-$5,265.90 in one quarter) but the detector does not exist.
- **Opaque SPVs.** No `FSOIFD`-style row was examined.
- **Whether marks move across quarters.** Only one quarter is loaded, so re-mark versus
  carry-forward is untested.
- **The database.** Supabase is provisioned; no schema has been created and nothing has been
  loaded.

---

## 7. Corrections to `plan.md`

| Location | Says | Measured |
|---|---|---|
| line 26 | Series F `valUSD` = `12131380.00000000` | **12,131,379.96** |
| line 46 | Alger and ARK marked $259.14 | **$259.1364** (Alger, T. Rowe); $259.14 (Fidelity, ARK) |
| line 47 | BlackRock $589.01 *vs* Capital Group $589.00 | **both $589.0095** — the plan rounded in opposite directions and implied a disagreement that does not exist |
| line 106, 400 | three-field `AND` filter | drops 5 of 6 managers — §2 |
| line 401 | "10-15M rows/qtr in, a few thousand out" | **5.35M in, 606,028 out** — §5 |
| line 214 | "Order 10-15M holding rows per quarter" | **5,347,869** in 2026Q2 |
| line 301 | Scale AI dropped at 0 hits | **confirmed — 0 rows in 2026Q2** |

---

## 8. Universe v1 — FROZEN 2026-08-08

**Gate cleared by Om Mali, 2026-08-08.** Machine-readable record: `universe_v1.json`.
Additions occur only at a version boundary, and a boundary is a discontinuity in every series.

**Full members (6):** Databricks, SpaceX, Anthropic, OpenAI, Anduril, Cerebras.
**Carried thin (1):** Figure AI — marks published, dispersion and propagation suppressed.
**Excluded (5):** Cohere (false positive), xAI (instrument mismatch), Perplexity, Groq
(insufficient coverage), Scale AI (no presence).

**Selection criterion:** a full member needs enough distinct filers in one quarter to support
cross-manager dispersion. The observed floor is 28 submissions (Cerebras); below that the
next company drops to 12. Membership is judged on Level 3 *equity* rows only.

Two changes from `plan.md`'s universe: **SpaceX is added** (69 funds — better coverage than
four companies the plan listed) and **Cohere is removed** as a false positive.
**Cerebras is retained despite being the smallest full member**, because its Level 3 → Level 1
transition at IPO is the only external validity check available to this project.

### The evidence behind the decision

Measured across all 5.35M rows of 2026Q2. `funds` counts distinct submissions.

| Company | rows | funds | Level 3 | price range | verdict |
|---|---|---|---|---|---|
| Databricks | 360 | 152 | 306 | 0.00 – 8,876,589.86 | **include** — best coverage |
| SpaceX | 154 | 69 | 154 | 204.64 – 5,265.90 | **include** — not in `plan.md`'s universe |
| Anthropic | 149 | 84 | 148 | 140.97 – 388.19 | **include** |
| OpenAI | 142 | 73 | 142 | 653.30 – 693.90 | **include** |
| Anduril | 130 | 50 | 130 | 40.88 – 96.60 | **include** |
| Cerebras | 37 | 28 | 37 | 89.02 – 100.26 | **include** — the IPO event study |
| Figure AI | 12 | 12 | 12 | 135.00 – 195.40 | thin — carry, label coverage |
| xAI | 58 | 47 | **11** | 0.97 – 75.46 | **see below** |
| Perplexity | 7 | 6 | 7 | 58.26 – 69.54 | too thin for dispersion |
| Groq | 3 | 3 | 3 | 61.90 – 87.97 | too thin for dispersion |
| Cohere | 1,094 | 1,062 | **2** | 0.96 – 319.71 | **false positive — see below** |
| Scale AI | 0 | 0 | 0 | — | **drop, confirmed** |

### Two name-matching traps, found before they did damage

**Cohere is not Cohere.** All 1,094 rows are **Coherent Corp**, a public NYSE optics company
— 561 + 266 + 256 rows across three spellings, **zero at Level 3**. Real Cohere does not
appear in 2026Q2 at all. A substring matcher would have produced a confident, entirely
fictitious Cohere price series.

**xAI is mostly debt, not equity.** Of 58 rows, only `x.AI, Inc.` (7 rows) is Level 3 equity.
The rest are `X.AI LLC TL 1L BANKDEBT` and `X.AI LLC/X.AI CO ISSUER 144A` — loans and 144A
bonds priced per $100 of face value, which is why the range starts at 0.97. Mixing them into
a per-share series would be meaningless.

Both confirm the precision-over-recall rule in `plan.md`, and both are golden-set cases.

### Entity-resolution load, measured

Distinct issuer-name spellings among Level 3 rows, per company:

| Databricks | OpenAI | SpaceX | Anduril | Anthropic | Cerebras |
|---|---|---|---|---|---|
| **50** | 18 | 16 | 13 | 10 | 3 |

~110 distinct names across six companies in one quarter. Hard, but bounded and finite — not
an open-ended matching problem.

### Other traps confirmed present

- **Zero balances:** 985 Level 3 placeholder-CUSIP rows have `BALANCE = 0`, plus 32
  unparseable. The null-price rule in `plan.md` is required, not hypothetical.
- **Unit artifacts:** SpaceX spans $204.64–$5,265.90 and Databricks reaches $8.9M per unit in
  a single quarter. The split/unit detector is required before any change series.

---

## 9. Assessment

The hypothesis — that fund marks are an informative, stepwise, cross-checkable record of
private AI pricing — is **supported by first-party evidence**: six managers, one repricing
event, and 15/15 agreement between hand-read filings and the bulk data set.

**The project is feasible.** Two risks that were open at the start of the week are now closed:

1. The bulk data behaves exactly like the raw XML.
2. Entity resolution is bounded — ~110 name variants across six companies, and the pipeline
   inversion in §5 shrinks its input from ~600,000 rows to ~1,000 per quarter.

**Three scope changes follow from the evidence:**

- **The universe shrinks to six companies** with real coverage (Databricks, SpaceX,
  Anthropic, OpenAI, Anduril, Cerebras), plus Figure AI carried with a thin-coverage label.
  Cohere is a false positive, Scale AI has no presence, and Perplexity and Groq (7 and 3 rows)
  cannot support dispersion analysis. SpaceX should be added — it has better coverage than
  four companies currently in the universe.
- **The pipeline inverts**: name-match first, Level-3 confirm second.
- **The usable panel is shorter than 27 quarters.** Anthropic's Series E/F/G are recent
  rounds and the AI cohort barely existed in fund portfolios before ~2023. Expect roughly
  12 usable quarters. This changes what can be claimed about history, not the design.

The infrastructure is also lighter than planned: 5.35M rows per quarter rather than 10–15M,
so 27 quarters is ~144M rows — comfortable for DuckDB.
