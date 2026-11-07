# Feasibility — is the AI Debt Tracker worth ten weeks?

> Started 2026-10-16. Every number here comes from a script run against live SEC data, not from
> documentation. Reproduce with `python scripts/probe_debt_filings.py`.

The question this document answers before ten tracked weeks are committed: **can this project fail
in a way that leaves nothing to show?** Each remaining risk gets a cheap test with a pass/fail line
decided *in advance*. If a test fails, the project pivots or stops at the end of week 1.

---

## Already verified (2026-10-16)

| Check | Result | How |
|---|---|---|
| **Mission fit** (preliminary) | Mycroft has ~99 recipes covering news, sentiment, talent, patents, funding news, SEC filings, earnings calls and portfolios — **none on debt or credit**. AI-related bond issuance is one of 2026's central AI-investing questions. | Listed `recipes/`; Morningstar and Reuters reporting (see `DESIGN.md` §1) |
| **The universe resolves** | All 25 CIKs map to the expected EDGAR company names (Cipher Mining now files as "Cipher Digital Inc.") | `data.sec.gov/submissions` |
| **There are events to read** | Jan 2025 – Sep 2026: **70** new-debt 8-Ks (item 2.03), **123** material-agreement 8-Ks (item 1.01), **130** bond prospectus supplements (424B2/5), **63** final term sheets (FWP) | `scripts/probe_debt_filings.py` |
| **There is an answer key to grade against** | **173** quarterly/annual reports in the same window | Same |
| **The answer key is detailed enough** | **21 of 25** companies tag debt instrument by instrument in their latest report; Meta, Alphabet and Amazon tag (mostly) by offering; Oracle tags totals only | Same (debt-dimension members); Alphabet/Amazon reclassified after the spike (P18) |
| **The answer key exists in bulk** | SEC monthly *Financial Statement and Notes* data (≈53 MB/month) contains per-instrument facts with dimensions — e.g. CoreWeave's June 2026 10-Q: 6 face amounts, 12 rates, 25 carrying amounts | Downloaded `2026_08_notes.zip` |
| **The smaller bulk files do not work** | The quarterly *Financial Statement Data Sets* contain **zero** per-bond facts (no notes) — so they are not used | Checked 2025 Q1 for 17 AI companies |
| **Big issuers don't use 8-Ks for bonds** | Alphabet: 0 item-2.03 8-Ks but 28 prospectus supplements and 13 term sheets → the tracker must read all four document families | Same probe |
| Hardware | RTX 4070 Laptop 8 GB VRAM, 32 GB RAM, i9-14900HX; Ollama installed | `nvidia-smi`, `ollama list` |

---

## The spike — run on 2026-10-16

The checks were run automatically on real data instead of by hand, across **23 companies × 2
consecutive quarters = 46 company-quarters** (reports filed Dec 2025 – Sep 2026). Scripts:
`scripts/spike_f1_f3_matching_and_headroom.py` and `scripts/spike_f2_f4_announcements_and_model.py`.
The run used the universe *before* Alphabet and Amazon were reclassified to L2 (P18), so it covered
23 companies; re-running the script today covers the 21 that remain at L1.

| # | Risk | Pass line (set in advance) | **Result** | Verdict |
|---|---|---|---|---|
| **F0** | Professor agrees it belongs in Mycroft | Written OK, logged | Professor approved (reported by Om Mali, 2026-10-16) | **Pass** — attach the written OK (email or comment) to the PR for the record |
| **F1** | Bonds can be matched from one report to the next | ≥ 90% of instruments match unambiguously | **489 of 588 (83%)** instruments in one report reappear in the next under the same name (478) or the same rate + maturity year (11). The misses cluster in a few companies (below). | **Partial.** Inside the "fall back to coarser grading for messy companies" band (70–90%). The causes are specific and fixable — see the new problems P17–P21. |
| **F2** | Changes are actually announced | ≥ 80% of changes explained by a filing | Of 73 new instruments with a stated rate: **56 announced** in an 8-K, prospectus or term sheet in the window, **9** were old bonds newly tagged (not real changes), **8** unexplained. → **56 of 64 real new bonds = 87.5%** explained. 52 of the 56 were found in 8-Ks. | **Pass.** Removals are noisier: Intel alone accounts for most unexplained removals (see P19), and keyword matching for "redeem" also hits new-issue filings, so removal checks need a proper method in week 2. |
| **F3** | There is room to beat doing nothing | Carry-forward wrong on ≥ 30% of episodes | Raw: carry-forward differs from the next report in **33 of 46** episodes — but some of that is tagging changes. Counting only episodes with **at least one change confirmed by an announcement: 21 of 46 (46%)**. 12 of 46 had no instrument change at all. | **Pass**, with the conservative 46% as the number to quote. |
| **F4** | A local model can read announcements on this GPU | ≥ 95% valid JSON; ≥ 85% field accuracy; ≤ 30 s per document | **`qwen3:8b`** (thinking off), one naive call per document — no tools, no checks, i.e. baseline B2 — on **all 33** real single-bond announcements the spike found: valid JSON **33/33**; interest rate **33/33**; maturity year **29/33**; principal **7/13** where the answer key has one; **all fields 69/79 = 87%**; **3.7 s** per document, ~43 tokens/s, **5.3 GB** of the 8 GB GPU. On the first 15 (the set `llama3.1:8b` saw): 28/35 = 80% for both models. | **Pass**, narrowly — and only on the naive baseline. **Principal (54%) is the weak field** (details below); it's what the design's span-pointing reader and tranche-sum checks exist to fix. |

### New problems the spike found (added to `DESIGN.md` §3.4)

| # | Problem | Evidence | Fix |
|---|---|---|---|
| **P17** | The bulk notes data **rounds interest rates** to 4 decimals of a fraction: 6.125% is stored as 0.0613 → 6.13%. | CoreWeave 9.625% notes stored as 9.63; Nvidia 5.625% as 5.63. | Take exact rates from the filing's own XBRL with Arelle (D5) for the answer key; match with ±0.005 tolerance. |
| **P18** | Some "per-instrument" members are really **offerings** (several bonds sold on one day). | Alphabet `A2026USDollarNotes` = $20 bn across several tranches; Amazon `March2026SeniorUnsecuredNotes` = $37 bn. | Alphabet and Amazon are graded at **L2 (per offering)**; every company's level is hand-checked in week 1. |
| **P19** | **Annual and quarterly reports tag debt at different detail.** | Intel: 42 instruments in its 10-K, 1 in the next 10-Q; Nvidia 0 → 7; Vistra 0 → 5. | A per-episode consistency check: if the target report tags far fewer instruments than the previous one, that episode is graded at **L3 (totals)**, and the count of downgraded episodes is reported. |
| **P20** | Member names **spell numbers in words** and contain typos. | Equinix `FourPointSixZeroZeroPercentSeniorNotesDueTwoThousandThirty`, `ThreePointTwoFieveZero…`. | A number-word parser for member names, plus matching on the human labels in `pre.tsv`. |
| **P21** | A bond **priced before quarter-end but settling after** is announced *before* the window. | CoreWeave 9.625% 2032 notes: in the next report, no announcement inside the quarter. | The event window starts ~30 days before the previous quarter-end; the settlement date decides which quarter a bond belongs to. |

### F4 in detail — where `qwen3:8b` went wrong

Raw answers: `$AI_DEBT_DATA/spike/f4_results_qwen3_8b.json` (local, not in git). Of the 10 field misses:

| Miss | Count | Cause | Already handled in the design by |
|---|---|---|---|
| Wrong maturity year on Nvidia 2031/2040/2050 notes and Intel 5.000% 2033 | 4 | The excerpt was cut around the first match of the rate, and those filings list **several bonds with the same rate** (e.g. Intel has 5.000% notes due 2031 *and* 2033) — so the model read the wrong one | Reading whole tables and sentences with ids (§7.3), not ±1,500-character windows |
| Principal in euros vs. the answer key in US dollars (Amazon EUR floating notes, CoreWeave EUR notes) | 2 | Currency, not reading: the report states the USD equivalent | Currency stored per instrument (P8) |
| `$2,000` instead of `$2,000,000,000` (Cipher 6.125%) | 1 | The model scaled "$2,000 million" wrongly | Code parses amounts from the cited span (§7.1); the AI never types a number |
| $2.25 bn vs. answer key $2.2 bn (Intel 5.30%) | 1 | Probably answer-key rounding | Exact values from Arelle (P17) |
| Wrong bond (Intel 5.000%) / unclear (Cipher 7.125%, $1.73 bn vs $1.40 bn) | 2 | Multi-bond filing / possibly an upsized or add-on tranche | Tranche-sum self-check and investigators (§7.3) |

So every miss has a specific cause the design already addresses — and the speed (3.7 s per
document) leaves plenty of room for the extra steps.

### Verdict

**Go.** All five checks are now recorded: F0 (professor), F2 (announcements) and F3 (headroom) pass;
F1 (matching) is partial with five known fixes (P17–P21); F4 (local model) passes narrowly on the
naive baseline, with principal as the field to watch. The two risks that could have killed the
project — *"most debt changes are never announced"* and *"there's nothing to beat"* — are ruled
out on real data. What's left is engineering with known fixes, not open research risk.

### The pitch for F0 (paste to the professor)

> I'd like to build an **AI Debt Tracker** for Mycroft. AI is increasingly financed with borrowed
> money — the five biggest cloud companies sold $121B of US bonds in 2025 against a 2020–24 average
> of $28B a year — but Mycroft has no debt or credit signal. The agent reads every debt-related SEC
> filing for ~25 AI-sector companies (cloud, chips, data centres, power) as it appears, keeps a
> ledger of each bond and loan, and publishes a quarterly signal: total debt, new borrowing, how
> much falls due in the next 12–24 months, and the average interest rate. It is graded against each
> company's next quarterly report, which tags debt per instrument (21 of the 25 companies do), and
> it runs on local models only. Is this a good fit for Mycroft, and is there anything you'd want in
> or out of scope?

---

## Week 1 re-checks — run on 2026-10-18

Week 0 left two checks short of a clean pass: F1 (matching, partial) and F4 (local model, narrow
pass on a task that named the coupon). Week 1 re-ran both on the **dev** split, so fixes are
judged where they were built, and measured the universe instead of trusting member counts.

| # | Check | Pass line (Week 0) | **Week 1 result** | Verdict |
|---|---|---|---|---|
| **F1** | Instruments match from one report to the next | ≥ 90% unambiguous | Episodes graded L1 at both ends: **dev 594/636 = 93.4%**, test 696/767 = 90.7% (92.1% excluding 11 plausibly matured). All episodes: dev 85.0%, test 82.2%. The gap is almost all P19/P23 episodes — Intel (43 bonds in dev, 41 in test) and Oracle (43 in test) itemise in 10-Ks and not in 10-Qs — which are graded at L3 anyway. The Week 0 method on the same dev L1 episodes: 586/636 = 92.1%. | **Pass** where per-bond grading applies. The matcher itself adds 1–2 points; most of the gain comes from grading each episode at the level its tagging supports. `scripts/f1_matching.py` |
| **F4** | A local model reads announcements on this GPU | ≥ 95% valid JSON; ≥ 85% field accuracy; ≤ 30 s per document | Bake-off on **29** dev-window announcements (FWP 8, 424B 8, 8-K 13; 54 true instruments), one call per document and **no hint**, unlike Week 0. **`qwen3:4b`**: valid JSON 29/29, fields **138/145 = 95%**, median 6.1 s, max 12.6 s. `llama3.1:8b`: 26/29, 88%, max 65.7 s. `qwen3:8b`: 27/29, 84%, max 65.9 s. Both 8B models had runaway answers (2–3 each) that hit the output cap. After the row-by-row review corrected 7 truth fields the documents contradict: **`qwen3:4b` 141/143 = 99%**, `llama3.1:8b` 91%, `qwen3:8b` 88%. | **Pass** — `qwen3:4b` meets every line, and is the only model that does. Confirmed at the Week 1 gate. [`bakeoff.md`](bakeoff.md) |
| — | **Universe levels** (P2, P18) | Hand-check in week 1 | Measured by coverage of total debt on every report Jul 2024 – Sep 2026: **L1 14, L2 3, L3 8** (draft 21 / 3 / 1). 0 reports missing from the notes data; 5 companies have issuing co-registrants (Dell, Equinix, Digital Realty, Vistra, Constellation). | **Frozen** 2026-10-18 with two overrides (Meta → L2, TeraWulf → L1): **L1 15, L2 4, L3 6**. [`universe_v1_review.md`](universe_v1_review.md) |
| — | **Enough episodes** | ~100 dev, ~100 + ~300 test | **dev 95, test 100 AI + 300 generalisation**; L1-graded: 47 / 60 / 293. | Pass. `manifests/` |

New problems found in Week 1 are P22–P29 in `DESIGN.md` §3.4: issuance-numbered members
(Microsoft), partial per-bond tagging (Oracle, Intel), maturity buckets (IBM), total debt under
many tags, subtotal members, subsequent-event facts in the target report, quarterly-only older
notes data, and two clocks for "accepted".

## Week 2 re-checks — run on 2026-10-23

| # | Check | Pass line | **Week 2 result** | Verdict |
|---|---|---|---|---|
| **F2** | Changes are announced | ≥ 80% of changes explained by a filing | Re-run on the **dev** split with the grader's change list and a proper removal method (an exit word must sit next to the bond, not anywhere in the document), reading only what `edgar_pit` allows at each cut-off: **new bonds 30 of 32 announced (94%)**; removals: 9 of 16 scheduled maturities, **5 of the other 6 announced**. 3 changes unexplained, $0.9 bn. | **Pass.** Removals now have a method, as Week 0 asked. [`changes_dev.md`](changes_dev.md) |
| **F3** | Room to beat doing nothing | Carry-forward wrong on ≥ 30% of episodes | B0 scored by the real grader on dev: bond recall 90.7%, but **0 of 36 new bonds** and 3 of 16 removals caught; only **18 of 47** L1 episodes reproduced exactly (62% wrong). | **Pass.** [`baseline_b0.md`](baseline_b0.md) |
| — | **Grader vs printed reports** (§11 week 2) | 10 of 10 hand-checked company-quarters | **10 of 10** after fixing five defects the first pass (8 of 10) exposed (P30–P34); a held-out set graded once afterwards: **2 of 3**, all 3 disagreements on Digital Realty's own tagging (P35–P37, open). | **Pass**, with the held-out caveat; accepted by Om Mali, 2026-10-23. [`handcheck.md`](handcheck.md) |

## Why this can't end with "nothing to show"

| By the end of | You have, even if everything after fails |
|---|---|
| Week 1 | This feasibility record and a go / pivot / stop decision backed by evidence. |
| Week 2 | **A benchmark:** a point-in-time answer key of every AI-sector bond and loan per quarter (Q2 2024 – Q2 2026), a grader, and the carry-forward baseline — usable by anyone as an "AI debt ledger" dataset on its own. |
| Week 4 | Three baselines scored on real announcements. |
| Week 6 | The full multi-agent system on the dev window, with its self-catch rate. |
| Week 8 | Test results with confidence intervals. |

A negative result with solid measurement is still a result — for example, "a third of AI debt
changes are never announced in a filing" would itself be a useful finding for Mycroft.

---

## Decision log

| Date | Check | Result | Decided by |
|---|---|---|---|
| 2026-10-16 | Filing volume, answer-key detail, bulk answer key | Verified (above) | — (evidence only; gates are cleared by a named human) |
| 2026-10-16 | F1 matching | 83% — partial; fixes P17–P21 | — (evidence only) |
| 2026-10-16 | F2 announcements | 87.5% of real new bonds — pass | — (evidence only) |
| 2026-10-16 | F3 headroom | 46% of episodes have announced changes — pass | — (evidence only) |
| 2026-10-16 | F4 model (lower bound, llama3.1:8b) | format/speed pass, field accuracy partial | — (evidence only) |
| 2026-10-16 | **F0 Mission fit** | **Approved** | **Professor** (reported by Om Mali; written OK to be attached to the PR) |
| 2026-10-16 | F4 re-run with qwen3:8b (33 announcements) | 87% of fields, 3.7 s/doc, 5.3 GB VRAM — pass (narrow) | — (evidence only) |
| 2026-10-16 | **Overall** | **Go** | Om Mali, with professor approval |
| 2026-10-18 | Ollama version | Stay on 0.34.0 (latest 0.40.6) so Week 0 and Week 1 speeds are comparable | Om Mali |
| 2026-10-18 | F1 re-run on dev | 93.4% on L1-graded episodes — pass | — (evidence only) |
| 2026-10-18 | F4 bake-off | `qwen3:4b` 95% of fields, 29/29 JSON, ≤ 12.6 s — pass; `qwen3:8b` 84% (2 runaways) fails the rule | — (evidence only) |
| 2026-10-18 | Bake-off set review | All 29 passages genuine; 7 truth fields on 6 rows corrected to what the documents say; re-scored `qwen3:4b` 99%, `llama3.1:8b` 91%, `qwen3:8b` 88% | Claude (model judgment, [`week1_review.md`](week1_review.md)) |
| 2026-10-18 | **Week 1 gate:** universe v1 (overrides Meta → L2, TeraWulf → L1), generalisation set, splits, bake-off set, model `qwen3:4b` | **Frozen / confirmed** | **Om Mali**, on the basis of Claude's review, without checking the filings personally (`manifests/week1_gate.json`) |
| 2026-10-23 | F2 re-run on dev (new removal method) | 94% of new bonds, 5 of 6 early removals announced — pass | — (evidence only) |
| 2026-10-23 | B0 scored on dev | recall 90.7%, 0 of 36 new bonds caught, 18 of 47 exact — the headroom is real | — (evidence only) |
| 2026-10-23 | Hand-check (week 2 check) | 10 of 10 calibration, 2 of 3 held-out | **Accepted** — **Om Mali**, 2026-10-23 (`manifests/week2_gate.json`); transcriptions are Claude's model judgment |
| 2026-10-31 | Fresh held-out hand-check (after P35–P37) | 1 of 3 gradable agree; P38–P39 found, left open | — (evidence only) |
| 2026-10-31 | Triage (week 3 check) | recall 24 of 24, precision 92% on 50 labelled filings; 22 of 22 Week 2 announcements kept — pass | **Delegated** in advance by **Om Mali**, not reviewed (`manifests/week3_gate.json`); labels are Claude's model judgment |
| 2026-11-07 | Fresh held-out hand-check (after P38–P39) | 1 of 5 agree (Amazon); P41–P44 found, left open | — (evidence only) |
| 2026-11-07 | Fresh triage check | recall 8 of 9 (89%) — **below the 95% line**; the miss is a blank preliminary cover (P46), left open | — (evidence; part of the Week 4 gate record) |
| 2026-11-07 | Event reader (week 4 check) | 157 of 167 fields (94%) vs B1 84% — pass; B2 100% | **Delegated** in advance by **Om Mali**, not reviewed (`manifests/week4_gate.json`); truth is Claude's model judgment |
