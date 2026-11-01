# Worklog

Newest first.

---

## 2026-10-31 — Week 3: finding the debt news (timeline, triage, documents)

**Week 2's leftovers first.** P35–P37, Digital Realty's own tagging, are fixed in the answer key and
grader: a face-only bond due by the report's year in a report that tags balances elsewhere is repaid
(P35); face and carrying in different units leave the currency unknown (P36); principal is scored only
in a known currency (P37). Week 2's held-out set now agrees 3 of 3 — but it is no longer held out, so a
**fresh held-out set** of five dev reports was drawn by seed before reading and graded once: **1 of 3**
gradable agree (Dell's totals exactly). Super Micro's key double-counts an over-allotment option (P38) and
Core Scientific's small notes have no maturity anywhere in the XBRL (P39); both are diagnosed and left
open, not tuned away. Cipher Mining and TeraWulf had no debt at those dates, so they are not counted. The
check also caught a mistake by the checker: a Super Micro coupon was transcribed from the notes' original
terms (disclosed; the verdict does not change). The key now holds 9,630 bonds (was 9,653); B0's recall is
90.8%, new bonds caught still 0 of 35, removals 1 of 15.

**The `docs` server.** A filing becomes addressable pieces — headings `h3`, sentences `s12`, tables
`t2`, rows `t2.r4`, cells `t2.r4.c1` — with bounded tools (`sections`, `sentences`, `tables`, `search`,
`span`), so the agent cites ids instead of retyping numbers. Every document is opened through
`edgar_pit` (a new internal `raw` call), so the point-in-time rule holds: a live test found Oracle's
4.200% 2029 notes sentence by search and was refused the episode's own target report.

**Timeline and triage.** The timeline gathers 8-Ks, 424B prospectuses and FWP term sheets in an episode's
window, for the company *and* its issuing subsidiaries (Equinix's euro notes come from a subsidiary
CIK), with co-filings removed. Over every dev window that is **593 candidate filings**. Triage decides
them with five rules — item 2.03/2.04, prospectus covers, term sheets, a debt announcement in the lead,
no debt words at all — and asks `qwen3:4b` only about the doubtful **199 (34%)**, at a median 3.1 s.

**The check.** 50 filings were drawn by seed (30 at random, 20 from filings with any debt word) and
labelled by Claude against a written definition **before** triage ran; the labels file's hash is
unchanged after the run. Result: **recall 24 of 24**, precision 24 of 26 (an Alphabet *share*
mini-tender and a TeraWulf acquisition were false alarms), event type right on 20. All 22 filings that
Week 2 found announcing a bond change are kept.

**What went wrong, and is recorded.** The first run crashed: a runaway model answer hit its token cap
and returned broken JSON. Unreadable answers now keep the filing (flagged) and the whole pool was rerun.
The report's first version showed one Week 2 announcement dropped; it was Week 2's error — "0%" matched
inside "escalates 20%" — now P40, fixed. 8 of the model's 21 keeps quoted text that isn't in the filing,
so the Week 4 reader must re-ground every fact. Two rule weaknesses seen while labelling (`Item1.01`
without a space; a prospectus cover with blanks) were deliberately not fixed against the labelled set.

**Gate (P4):** Om delegated the whole week in advance and did not review it; `manifests/week3_gate.json`
says exactly that (status DELEGATED, not CLEARED). Git is Om's.

---

## 2026-10-23 — Week 2: the answer key, the grader and the do-nothing baseline

**Housekeeping first.** Weeks 0–1 were committed; their three RUN_LOG entries had not reached
`logs/RUN_LOG.md`, so they were appended and `run_log_pending.md` and `universe_draft.json` moved to
`docs/archive/` (the scripts now read the draft from there).

**The answer key, for everyone.** `scripts/build_answer_key.py` builds a record for every 10-Q/10-K of
all 100 companies: **1,093 reports**, Jan 2024 – Sep 2026 (the 2024 Q1–Q2 notes files were added so
annual-only itemisers have a prior 10-K), every episode finding both its records. Anomalies are counted
in `docs/answer_key.md`, not hidden.

**The grader** (`eval/grader.py`): L1 per bond (currency, coupon ±0.01 pp, maturity year; principal
within 1% of face or 2% of carrying; one-to-one optimal assignment), L2 per offering (amounts within
1%, issue periods compatible, ledger bonds summed by issue period), L3 totals (within 2%), change
detection, and 95% bootstrap intervals. The suite grew from 65 to 95 tests.

**B0 on dev** (`docs/baseline_b0.md`): bond recall **90.7%**, precision 90.3%, principal 99.2% — and
**0 of 36 new bonds** caught, 3 of 16 removals, 18 of 47 L1 episodes exact. Two things had made it look
worse than it is: the notes data started after Intel's and Oracle's previous 10-Ks, and B0 refused
Intel's FY2023 10-K for itemising 79% (bar 80%). Fixed by adding the earlier data and letting B0 walk
back to the best-itemised recent report. L2 recall is 76.2% — the first figure, 91.7%, compared static
original deal sizes and was flattering.

**The hand-check found real bugs.** Ten dev reports' *printed* debt tables were transcribed (a model
judgment, every row reviewed) and graded against the key. First pass: **8 of 10**. Each disagreement
was a defect on our side: Oracle's repaid notes resurrected by their face tags (P30), AMD's two-bond
member read as a duplicate bond (P31), Broadcom's assumed VMware notes dropped with their
`BusinessAcquisition` axis (P32) and named by due date or misspelt `SeniorNots` (P33), an Equinix Swiss
franc note the XBRL calls dollars (P34), and Microsoft's offerings measured on original deal size.
After the fixes: **10 of 10**. Because those ten found the fixes, three more were held out, chosen
before reading and graded once: **2 of 3** — Digital Realty's own tagging (a face-only repaid note, a
euro-tagged dollar note, translated face amounts) is P35–P37, left open on purpose for Week 3.

**Frozen means frozen.** A rerun of the selection scripts with the fixed parser swapped Molson Coors
for Post Holdings in the frozen generalisation set. The frozen files were restored from the commit,
the three scripts now refuse to overwrite a frozen artifact without `--refreeze`, and
`docs/answer_key.md` lists the 5 of 495 episode levels today's rules would grade differently.

**EDGAR's clock moved.** The same rerun showed 43 of 495 episode cut-offs shifted by 4–5 hours in
EDGAR's own index since 18 October (9 filers, Eastern → UTC). `edgar_pit` now pins the cut-off to the
target report (`for_episode`, `EDGAR_PIT_TARGET`) and keeps a 5-hour margin on the cut-off day (P29).

**Changes explained, properly** (`docs/changes_dev.md`): with the grader's change list, `edgar_pit`'s
view at each cut-off, and exits counted only when named next to the bond, **30 of 32** searchable new
bonds and **5 of 6** early removals were announced. The first run under-counted four because it searched
for rounded coupons (3.62% for 3.625%); fixed.

**Gate (P4):** Om Mali accepted the hand-check as the Week 2 check the same day
(`manifests/week2_gate.json`). Week 3 starts with P35–P37 and a fresh held-out check. Git is Om's.

---

## 2026-10-18 (later) — Week 1 gate cleared on the basis of Claude's review

Om asked Claude to do the review on Om's behalf, since it needs financial reading Om does not
have. The record says exactly that: the review is a model judgment (`docs/week1_review.md`), and
the decision to accept it is Om's (`manifests/week1_gate.json`).

- **Bake-off set:** all 29 passages are genuine announcements. 6 rows had truth values the
  document contradicts, all caused by using the next report as truth: euro notes reported in
  dollars, pricing releases quoted before the banks' extra allotment, a floating-rate spread taken
  as a coupon, and one 8-K with no amount. These are corrected in
  `manifests/bakeoff_truth_corrections.json` and the scorer applies them. Re-scored: `qwen3:4b`
  **99%**, `llama3.1:8b` 91%, `qwen3:8b` 88%; the order did not change. Lesson for the Week 2 grader:
  an announcement and the next report can both be right about different moments, so the event
  reader must score against the document and the ledger against the report.
- **Universe:** 14 companies' levels checked against their own tagging; all hold. The two 4–4 ties
  were resolved on substance rather than by the default: Meta → L2 (it tags every offering when it
  tags at all) and TeraWulf → L1 (it has itemised 100% since its first bond). Final: L1 15, L2 4, L3 6.
- **Generalisation set:** no banks, insurers, REITs or AI companies among the 75.
- **Frozen:** `universe_v1.json`, `manifests/generalisation.csv`, `dev.csv`, `test.csv`; model `qwen3:4b`.
  The scripts read the gate file, so re-running them keeps the record consistent.
- **Still Om's:** branch, commit, and copying `docs/run_log_pending.md` into `logs/RUN_LOG.md`.

---

## 2026-10-18 — Week 1: universe measured, answer key loaded, `edgar_pit`, F1 re-run, bake-off

**Set-up.** `.env` now carries the SEC identity (Om Mali, university email — local only, gitignored).
`qwen3:4b` pulled into the project's models directory. Ollama stays at 0.34.0 (Om's call: keep
Week 0 and Week 1 speeds comparable; 0.40.6 is out). A uv project (`pyproject.toml`, `uv.lock`) with
the environment outside the repo; `mcp` held below 2.0 because 2.x renamed FastMCP and
`langchain-mcp-adapters` (week 5) targets 1.x.

**The answer key, at scale.** `eval/fsn.py` downloads the SEC notes data for July 2024 –
September 2026 and keeps only the debt part, for every filer: 2.8 GB of zips → 170 MB. The SEC
publishes only the last 12 months as monthly files; older months are quarterly (P28).
`eval/answer_key.py` turns one filing into instruments (coupon, maturity, face, carrying, class)
and totals. Loaded for 10 companies chosen to cover every hard case: 87 reports, 1,833 instrument
records (`docs/answer_key_week1.md`).

**The member parser** (`ledger/parsers.py`) reads the filer's label first, then the name: number
words and typos (`ThreePointTwoFieveZero…`, P20), years glued to coupons (`A20319.00SeniorNotes`),
offerings (P18), facilities and buckets. Over one month's 6,547 bond-like labels it gives a full
key for 2,189 of them; what remains is mostly securitisation series, outside the universe. It
also fixes P17 at the source: when the bulk data rounds 9.625% to 9.63, the member name usually
keeps 9.625, and the key uses that.

**The universe was measured, and member counts turned out to mislead.** The first pass agreed with
the Week 0 probe. Looking at the instruments showed why that was wrong:
- Microsoft's 13 members are `IssuanceOfLongTermDebtOne…Thirteen`: issuance groups, not bonds (P22).
- Oracle's 10-Qs tag only that quarter's new bonds, 4–14 of ~56 (P23). Intel's 10-Qs tag almost none.
- IBM tags maturity-year buckets (P24). Digital Realty and Oracle tag subtotals next to the bonds (P26).
- Total debt hides under several tags (P25).
So a report's level is now decided by **coverage**: itemised instruments must account for ≥ 80% of
total debt for L1. Result: **L1 14, L2 3, L3 8** (draft 21 / 3 / 1). Issuing co-registrants found
from filing headers for Dell, Equinix, Digital Realty, Vistra and Constellation. Every 10-Q/10-K on
EDGAR in the window is in the notes data. `universe_v1.json` is **proposed**, not frozen
(`docs/universe_v1_review.md`).

**Generalisation set and splits.** 75 US non-financial, non-AI companies chosen by a written rule
(`scripts/select_generalisation.py`) from 496 that tag per bond in ≥ 3 of 4 test reports, at most
3 per SIC major group. Episodes: **dev 95**, **test 100 AI + 300 generalisation**, none dropped,
7 downgraded to L3 by the P19 check. Each episode's cut-off is the target's EDGAR acceptance time
from the submissions index. The notes data's own `accepted` field is hours off for the same
filing, so it is never used for cut-offs (P29). All proposed.

**`edgar_pit`** (`mcp_servers/edgar_pit_core.py` + a thin FastMCP binding): timeline / exhibits /
fetch, refusing the target report and anything accepted at or after the cut-off, failing closed
on undatable filings, logging every call. 14 offline tests, plus a structural test that nothing
outside `eval/` imports the answer key. Smoke-tested live over stdio on CoreWeave's June 2026
episode: 477 filings visible, target refused, 8-K and exhibits read. The bake-off reads all its
documents through it.

**F1 re-run on dev — pass where per-bond grading applies.** New matcher (`ledger/matcher.py`:
name → normalised name → label → key → year + amount, unambiguous only). L1-graded episodes: dev
93.4%, test 90.7%. All episodes: dev 85.0%, test 82.2%, the gap being Intel's and Oracle's 10-Q
tagging. Being honest about where the gain came from: the Week 0 method scores 92.1% on the same
dev L1 episodes. The matcher adds a point or two; grading each episode at its true level does
the rest.

**F4 bake-off — the smaller model won.** 29 dev-window announcements (FWP 8, 424B 8, 8-K 13; the
dev window had too few redemption notices and credit agreements to include), found and read
through `edgar_pit` at each episode's cut-off. Truth comes from the next report's XBRL. Earnings
releases are excluded, and no deal appears in more than 2 documents. The task is harder than Week 0's on
purpose: the spike's prompt named the coupon to look for, so its 33/33 coupon score was built in;
here the model gets only the document. Results (`docs/bakeoff.md`): **`qwen3:4b` 138/145 = 95% of
fields, 29/29 valid JSON, median 6.1 s, max 12.6 s**; `llama3.1:8b` 88%; `qwen3:8b` 84%. Both 8B
models had runaway answers that looped on their own instrument list until the output cap (the
first `qwen3:8b` run had one loop for 10 minutes before the cap existed). Even with runaways left
out, `qwen3:8b` reaches 89% against 95%: it also labels new issues as "redemption" or "exchange"
(action 40/54). By the rule set in advance, the pick is `qwen3:4b`. That reverses §8.2's main pick
and is provisional until the set is attested. Caveats: 29 documents and 12 companies is small;
one prompt; thinking off; zero-coupon convertibles answered as `null` rather than 0 cost a coupon
point each.

**Waiting on a human (P4):** freeze the universe and the generalisation set (or override with a
reason); attest the bake-off set and confirm the model; commit, and append
`docs/run_log_pending.md` to `logs/RUN_LOG.md`.

---

## 2026-10-16 (evening) — Week 0 closed: professor approval, local setup, qwen3:8b test

**F0 — professor approved** the project for Mycroft.

**Local data directory** created outside the repo, with `data`, `ollama-models`, `venv` and
`uv-cache`; the spike's cached SEC data (1.9 GB) moved there; a gitignored `data` link in this folder
points to it.

**F4 re-run with `qwen3:8b`** (pulled into the local models directory, 4.9 GB; thinking off),
one naive call per document on all 33 real single-bond announcements: valid JSON 33/33, interest rate
33/33, maturity year 29/33, principal 7/13 → **87% of fields**, 3.7 s per document, ~43 tokens/s,
5.3 GB VRAM. **Pass, narrowly.** All 10 misses have causes the design already handles: multi-bond
filings cut into short excerpts, euro vs. dollar amounts, one mis-scaled "$2,000 million", and
answer-key rounding.

**Overall verdict: go.** The `logs/RUN_LOG.md` entry is waiting in `docs/run_log_pending.md` until
the project branch exists.

---

## 2026-10-16 (later) — Week 0: the feasibility spike, run on real data

Ran the go/no-go checks automatically instead of by hand, on **46 company-quarters** (23 companies ×
2 consecutive quarters, reports filed Dec 2025 – Sep 2026). Full table in `docs/feasibility.md`.

- **F2 announcements — pass.** 56 of 64 genuinely new bonds (87.5%) were found in an 8-K, prospectus
  or term sheet inside the window; 52 of those in 8-Ks.
- **F3 headroom — pass.** Carrying last quarter forward misses an announced change in 21 of 46
  company-quarters (46%).
- **F1 matching — partial.** 83% of instruments reappear under the same name or key. The misses have
  five specific causes, now P17–P21 in `DESIGN.md`: rounded rates in the bulk data, offering-level
  members (Alphabet, Amazon → L2), annual-vs-quarterly tagging detail (Intel 42 → 1), numbers
  spelled in words (Equinix), and bonds priced before quarter-end.
- **F4 model — partial (lower bound).** The old installed `llama3.1:8b`, one naive call per document:
  valid JSON 15/15, interest rate 15/15, maturity year 11/15, 3.7 s per document, 31.8 tokens/s.

**Verdict:** go, conditional on the professor's OK and a `qwen3:8b` re-run in week 1.

---

## 2026-10-16 — Week 0: design and feasibility before commitment

**Chose the project** after checking which ideas fit Mycroft's "Using AI to Invest in AI": Mycroft
has no debt or credit agent, and AI-related borrowing is one of 2026's central AI-investing
questions.

**Wrote** `DESIGN.md` (data, answer key, agents, MCP servers, local models, evaluation, ten-week
plan) and `docs/feasibility.md` (what is verified, what is not, pass/fail lines).

**Verified against live SEC data** (`scripts/probe_debt_filings.py`):
- 25-company AI universe resolves on EDGAR (`universe_draft.json`).
- Jan 2025 – Sep 2026: 70 new-debt 8-Ks, 123 material-agreement 8-Ks, 130 prospectus supplements,
  63 term sheets, and 173 quarterly/annual reports to grade against.
- 23 of 25 companies tag debt per instrument; Meta per offering; Oracle totals only.
- The SEC's monthly notes data holds the per-instrument answer key in bulk; the quarterly
  statement-only files do not.

**Set up** the folder with all bulky files kept outside the repo.

**Open**
- F0: professor sign-off on fit and scope.
- F1–F4: bond matching across reports, how much change is announced, headroom over carry-forward,
  local model on the GPU.
