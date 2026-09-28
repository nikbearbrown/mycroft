"""
Self-report — what this subsystem knows to be broken about itself.

Why this module exists
    The UI is supposed to show what has actually been tested and what is actually
    going wrong, not a marketing view of the pipeline. Hard-coding that into app.js
    would drift from the record the moment anything changed, and there would be no
    way to tell which claims were measured and which were assumed.

    So every item here carries provenance: the date it was measured, the source
    document or log entry that records it, and whether it is OPEN, RESOLVED, or
    BY_DESIGN. Nothing in this file is a guess. Anything not measured is marked
    UNVERIFIED rather than given an optimistic default.

Sourced from (all inside this subsystem)
    logs/RUN_LOG.md            2026-08-28 / 2026-08-29 entries
    divij/model-test-report-2026-08-29.md
    divij/cross-agent-validation-status.md   §2b (live tests), §3.3 (open items)
    divij/cross-agent-validation-proposal.md §9  ("Explicitly not claimed")
    divij/sdd.md                             §14 ("Explicitly deferred")
    accountability-layer-audit.md            the four original CRITICAL findings

Keeping it honest
    When a limitation here is fixed, change its status and add the fixing date —
    do not delete the entry. Per P7 the record is append-only; a limitation that
    silently disappears is indistinguishable from one that was never found.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from typing import Any

# ── Status vocabulary ──────────────────────────────────────────────────────────
# OPEN       — known broken or unfinished, not fixed
# RESOLVED   — was broken, has since been fixed (date recorded)
# BY_DESIGN  — deliberately not built; a scope decision, not a defect
# UNVERIFIED — cannot currently be claimed either way; no measurement exists

_TESTS_DIR = Path(__file__).resolve().parent.parent / "tests"


# ── The five live model tests (2026-08-29, qwen2.5:7b via Ollama) ──────────────
# Run once against a real local model to find out what a model actually does,
# rather than what the code assumes. These are results, not aspirations.

LIVE_MODEL_TESTS: list[dict[str, Any]] = [
    {
        "n": 1,
        "name": "Claim verification",
        "purpose": "Do validation/claims.py + validation/verification.py catch a fabricated number by tracing it to its cited source?",
        "expected": "Every asserted number is extracted as a claim; each citation resolves verified true or false, never silently skipped.",
        "actual": "The fabricated 0.34 debt-to-equity ratio was never extracted as a claim at all. The regex only matched $ / % / x / bps-suffixed numbers, so a bare decimal had no suffix to match.",
        "verdict": "The verification logic that did run worked correctly. The extraction step never gave it a chance.",
        "outcome": "gap_found",
        "status": "RESOLVED",
        "resolved_note": "Regex widened to catch bare decimals on 2026-08-29, in all three files that carried an identical copy of it (validation/claims.py, validation/consistency.py, validation/verification.py). tests/test_claims.py added — no test file existed for that module before.",
    },
    {
        "n": 2,
        "name": "Consistency probe",
        "purpose": "Same query, same agent, second call — score word and number overlap.",
        "expected": "HIGH agreement is a positive signal; LOW is a flag worth investigating.",
        "actual": "score = 0.111 (LOW). The second call fabricated a different unsupported pair (asset turnover 0.13, net profit margin 38.0%) rather than repeating the first fabrication.",
        "verdict": "Worked exactly as designed, and produced a stronger finding than test 1: this agent invents a different unsupported number each time.",
        "outcome": "worked",
        "status": "OPEN",
        "resolved_note": "Caveat still open: some of the divergence score was a number-formatting artifact ($383.266 billion vs $383,266,000,000), not separated from genuine disagreement.",
    },
    {
        "n": 3,
        "name": "Determinism replay",
        "purpose": "Re-run identical input with seed 42 and temperature 0.0, testing ollama_adapter.py's documented determinism claim.",
        "expected": "Byte-for-byte identical output — the literal bar the docstring sets.",
        "actual": "Not identical. Third call said 38.1% where call 2 said 38.0%; call 1 had produced a different invented metric entirely. Follow-up at n=5: 4 of 5 byte-identical apart from a rounding wobble, so 3 distinct answers across 6 total calls.",
        "verdict": "The documented determinism claim is false for this model on this hardware — measured, not theorised.",
        "outcome": "gap_found",
        "status": "OPEN",
        "resolved_note": "Anywhere the project relies on same-seed-same-answer (e.g. /api/runs/{id}/replay) should not assume it holds for a local Ollama model without re-checking.",
    },
    {
        "n": 4,
        "name": "Guardrail stress test",
        "purpose": "Real-world parse-failure rate for ADR-07 retry/halt, against a real model instead of mock_adapter.py's scripted failures.",
        "expected": "Informative either way: retries would prove the retry path fires on real quirks; 100% success is good news but leaves retry/halt unproven.",
        "actual": "8 of 8 real agent-runs succeeded on attempt 1 (4 tickers x 2 producers). Zero retries, zero halts. Later runs took this to 24 real agent-runs with the same result.",
        "verdict": "Good reliability signal, but a non-result for the retry/halt path specifically.",
        "outcome": "inconclusive",
        "status": "UNVERIFIED",
        "resolved_note": "The retry/halt code still has zero real-world evidence of firing correctly against a live model. It is only proven against mock_adapter.py's scripted failures.",
    },
    {
        "n": 5,
        "name": "Multi-ticker breadth",
        "purpose": "Is the contradiction flag's behaviour an AAPL quirk or systematic?",
        "expected": "Flag fires on genuine numeric disagreement; does not fire when agents simply report on different, non-overlapping concepts.",
        "actual": "Of 5 tickers, only MSFT came back unflagged — and that was the one where neither agent cited any number. TSLA, where both agents were fully correct and simply reported different metrics, was flagged anyway. At n=12: 11 of 12 flagged before the comparator fix, 7 of 12 after.",
        "verdict": "The most important finding of the batch. The comparator cannot distinguish 'these numbers differ because the agents disagree' from 'they differ because they were asked about different things' — and the deliberate information-asymmetry design makes the second case the common one.",
        "outcome": "gap_found",
        "status": "OPEN",
        "resolved_note": "Addressed 2026-09-11: /api/compare now uses contradiction_rule=\"concept_aware\" (validation/concept_linkage.py), wired in and measured against the real corpus at 15 of 16 disjoint-concept flags killed with the one confirmed true positive preserved — see tests/test_concept_linkage.py and tests/test_real_run_corpus.py::TestConceptAwareRuleAgainstCorpus. Still can't tell a legitimate derived ratio from a fabricated one, since both are untagged numbers by the same mechanism — see disjoint-concepts's KNOWN_ISSUES entry for that residual caveat.",
    },
    {
        "n": 6,
        "name": "Overlapping-concept live test",
        "purpose": "Nothing in 31 real stored runs had ever put two producers in a position to genuinely agree or disagree about the SAME fact — Producer A/B's concept sets are disjoint by construction. Does contradiction_flag fire correctly when it's finally given the chance to?",
        "expected": "Either a clean agreement (both models correctly transcribe the identical input, unflagged) or a genuine numeric mismatch the flag correctly catches — informative either way.",
        "actual": "4 of 4 live runs (AAPL x2 with roles swapped, MSFT, NVDA; qwen2.5:7b vs. mistral-7b via local Ollama, identical EDGAR-derived context on both sides) flagged. qwen2.5:7b correctly transcribed every real figure every time (while still adding unsupported derived ratios not grounded in the input, e.g. NVDA's 'simulated ROE of 47.2%' -- the same fabrication shape as the historic AAPL 0.34 case). mistral-7b never grounded its answer in the real input: 3 of 4 runs invented an unrelated historical fiscal quarter and a fake source URL with zero real figures cited; the 4th (role-swapped AAPL) cited the real Assets/Revenues figures but mangled NetIncomeLoss into 'net income loss (-$101 million)' -- wrong sign, wrong magnitude by 1000x, and a rounding artifact was not the cause.",
        "verdict": "This is the first observed case of Cross-Agent Validation's contradiction_flag firing on genuinely overlapping evidence rather than a disjoint-concepts artifact -- the mechanism itself works. It surfaced a different, more basic problem: one of the two available local models does not reliably use the context it is given at all. That is a producer-reliability finding, not a comparator finding.",
        "outcome": "gap_found",
        "status": "OPEN",
        "resolved_note": "scripts/run_overlap_concept_live.py is the reusable script; see logs/RUN_LOG.md's 2026-09-11 entry for full transcripts. mistral-7b should not be used as a live producer in this pipeline until its context-grounding failure is understood -- this was not previously tested because every prior live test used qwen2.5:7b only (LIVE_MODEL_TESTS_CAVEATS below, now partially addressed).",
    },
]

# What the live tests do NOT establish. Stated because a reader looking at five
# green-ish rows will otherwise assume more coverage than exists.
LIVE_MODEL_TESTS_CAVEATS: list[str] = [
    "Sample size (5 then 12 tickers, 3 then 6 determinism calls, 4 overlapping-concept runs) is enough to show these failure modes are real and reproducible in kind, not enough to cite a stable rate.",
    "Tests 1-5 used one model only (qwen2.5:7b via Ollama). Test 6 (2026-09-11) is the first to use a second model (mistral-7b) and found it unreliable at grounding in context -- that finding has one data point's worth of models behind it, not a survey. Nothing here has been reproduced on Gemini or any hosted model.",
    "Some of test 2 and 3's measured divergence is number-formatting noise, not separated from genuine reasoning inconsistency.",
]


# ── Known limitations ──────────────────────────────────────────────────────────

KNOWN_ISSUES: list[dict[str, Any]] = [
    {
        "id": "disjoint-concepts",
        "severity": "high",
        "area": "Comparator",
        "title": "Over-flags when agents are asked about different concepts",
        "detail": "RESOLVED for the known-concept case, 2026-09-11: /api/compare now uses contradiction_rule=\"concept_aware\" (validation/concept_linkage.py), which excludes a number tagged to a known lens concept from comparison entirely — the two producers' vocabularies are disjoint by construction, so it could never be corroborated by the other side. Measured against all 31 real stored runs: 15 of 16 disjoint_concepts flags are now suppressed; the 16th is the confirmed true positive (correctly still flags). See tests/test_concept_linkage.py and tests/test_real_run_corpus.py::TestConceptAwareRuleAgainstCorpus. NOT fully solved: an untagged bare ratio/percentage (a derived metric with no known-concept keyword nearby) is syntactically identical whether it's legitimate or fabricated — concept-linkage narrows the false-positive surface from 'any disjoint number' to 'any untagged number', it doesn't resolve that remaining ambiguity. See divij/cross-agent-validation-disjoint-concepts-diagnosis.md for the original diagnosis. "
                  "UPDATE 2026-09-25 (B2, lens v2): the root cause is now addressed as the diagnosis proposed — both producers are also handed "
                  "NetIncomeLoss and EarningsPerShareDiluted, and concept_aware compares figures for those shared concepts by value instead of "
                  "excluding them (validation/concept_linkage.py; the shared set is derived from the lens definitions). First live result: AAPL's "
                  "two agents independently cited the same net income ($29.79B vs $29.788B) and EPS ($2.02) and matched. In the same batch two of "
                  "three agent-A runs that parsed said diluted EPS was not in their context although it was — agents don't reliably use the new line.",
        "status": "RESOLVED",
        "source": "Live test 5; status doc §3.3; divij/cross-agent-validation-disjoint-concepts-diagnosis.md; validation/concept_linkage.py; logs/RUN_LOG.md 2026-09-11 entry",
    },
    {
        "id": "asymmetry-fix-suppresses-historic-true-positive",
        "severity": "high",
        "area": "Comparator",
        "title": "The 2026-08-29 false-positive fix silently turns off the one confirmed true positive",
        "detail": "RESOLVED 2026-09-11 as a side effect of switching /api/compare to contradiction_rule=\"concept_aware\": that rule never imposed the both-sides-non-empty gate that caused this suppression (validation/concept_linkage.py's contradiction_flag_concept_aware compares untagged-number sets directly, with no emptiness precondition). Confirmed by replay: run f4a4c782 (the historic AAPL 0.34 case) now flags correctly again — see tests/test_cross_validation.py::TestContradictionRuleConceptAware.test_fabrication_with_empty_other_side_is_still_flagged and tests/test_real_run_corpus.py::TestConceptAwareRuleAgainstCorpus.test_preserves_the_one_confirmed_true_positive. The underlying bug is UNCHANGED in the legacy contradiction_rule=\"symmetric_difference\" + concepts_expected_to_overlap=False combination — that code path still exists (default-compatible, used by existing tests) and still has this failure mode if a caller explicitly requests it; production (/api/compare, scripts/run_cross_agent_live.py) no longer does.",
        "status": "RESOLVED",
        "source": "divij/cross-agent-validation-disjoint-concepts-diagnosis.md §3a; tests/test_real_run_corpus.py; logs/RUN_LOG.md 2026-09-11 entry",
    },
    {
        "id": "regex-truncates-comma-grouped-numbers",
        "severity": "medium",
        "area": "Extraction",
        "title": "QUANTITATIVE_RE truncates a large number with no $/%/x/bps suffix down to its last digit group",
        "detail": "RESOLVED 2026-09-11: core/numeric.py's QUANTITATIVE_RE gained a dedicated comma-grouped alternative (\\b\\d{1,3}(?:,\\d{3})+(?:\\.\\d+)?\\b), tried before the bare-decimal fallback, so a figure like '13,971,000,000.0' is now taken whole instead of truncating to '000.0'. tests/fixtures/cross_agent_real_runs_corpus.json's replay_today for run 515f263a was updated to the corrected extraction (its historical stored_* fields are untouched, per the append-only convention). See core/numeric.py's module docstring and tests/test_numeric.py.",
        "status": "RESOLVED",
        "source": "divij/cross-agent-validation-disjoint-concepts-diagnosis.md §3b (addendum); tests/fixtures/cross_agent_real_runs_corpus.json (run 515f263a); logs/RUN_LOG.md 2026-09-11 entry",
    },
    {
        "id": "fabrication-not-caught",
        "severity": "high",
        "area": "Verification",
        "title": "Nothing automated catches a fabricated number in this path",
        "detail": "RESOLVED (wired in) 2026-09-11: /api/compare now calls extract_claims + verify_claims on each producer's own thought_log independently, the same mechanism /api/chat has used since Week 7, previously never called anywhere in the cross-agent path. Tested against the exact historic case, not just wired blind: replaying Producer A's real 2026-08-29 thought_log (the fabricated 0.34 debt-to-equity ratio, cited to the generic https://www.sec.gov/ URL) through the now-wired code produces verification_rate=0.0 — the citation does not support ANY of the numbers attributed to it, correctly and automatically. Precisely what this does NOT do, so it isn't overclaimed: it does not isolate which specific number is fabricated, only that the cited source fails to back the claims made under it — a rate/per-citation signal, not a per-number fabrication flag. See web/server.py's /api/compare route and tests/test_compare_route.py. "
                  "UPDATE 2026-09-25 (B3): per-number checks now exist for figures an agent was GIVEN — validation/constraints.py compares each "
                  "cited lens figure with the filing value handed to it (rounding to the digits written is allowed) and a miss gates the run for a "
                  "human decision. Observed live the same day: MSFT's agent A wrote revenue $828.9B and net income $317.8B against $82.9B/$31.8B given "
                  "(a 10x slip); that attempt failed the format check, so the misquote never reached a comparison. A derived or outside figure (the "
                  "0.34 debt-to-equity case) is still only caught by B1's UNCORROBORATED/recompute rows, not by this check.",
        "status": "RESOLVED",
        "source": "logs/RUN_LOG.md 2026-08-29 first-observed-live-run entry; logs/RUN_LOG.md 2026-09-11 entry; tests/test_compare_route.py",
    },
    {
        "id": "ollama-determinism",
        "severity": "medium",
        "area": "Adapters",
        "title": "ollama_adapter.py's determinism claim is false as written",
        "detail": "Seed + temperature=0 did not produce reproducible output for qwen2.5:7b: 3 distinct answers across 6 identical-input calls. The docstring's claim needs scoping or correcting, and /api/runs/{id}/replay should not assume it.",
        "status": "OPEN",
        "source": "Live test 3",
    },
    {
        "id": "mistral-7b-context-grounding-failure",
        "severity": "high",
        "area": "Adapters",
        "title": "mistral-7b (via Ollama) does not reliably use the context it is given",
        "detail": "In the overlapping-concept live test (Live test 6), mistral-7b failed to ground its answer in the real EDGAR data in 3 of 4 runs -- it invented an unrelated historical fiscal quarter and a fake source URL, citing none of the real figures at all. The 4th run cited the real Assets/Revenues figures but mangled NetIncomeLoss into 'net income loss (-$101 million)' -- wrong sign, wrong magnitude by 1000x. qwen2.5:7b, given the identical prompts, transcribed every real figure correctly across all 4 runs. This is a producer-reliability finding, not a comparator-logic one: this pipeline should not use mistral-7b as a live producer until its context-grounding behaviour is understood, independent of anything cross_validation.py does with its output.",
        "status": "OPEN",
        "source": "Live test 6, logs/RUN_LOG.md 2026-09-11 entry",
    },
    {
        "id": "session-scope-leak",
        "severity": "high",
        "area": "Security",
        "title": "Nested session object ignores caller scope",
        "detail": "build_run_payload() writes full auditor-level data into the nested session object regardless of who asked. /api/compare redacts its top-level reasoning_objects per the caller's real scope (verified by smoke test) but does not fix the nested copy, because that is shared code (RunSession.to_dict()). This route is exactly as leaky as /api/chat — no worse, not fixed. "
                  "UPDATE 2026-09-25 (BG): reads sent with an investor token now strip the internal tier from the nested "
                  "session too (validation/gate.py redact_for_scope, on /api/runs, /api/runs/{id}, /api/sessions). "
                  "Storage is unchanged (still full), and a read with no token is served at the scope the run was "
                  "stored under, so this stays open.",
        "status": "OPEN",
        "source": "logs/RUN_LOG.md 2026-08-28 HTTP-route entry; status doc §1.3",
    },
    {
        "id": "audit-criticals",
        "severity": "critical",
        "area": "Security",
        "title": "Four original CRITICAL audit findings still open",
        "detail": "Investor redaction bypassed at storage time; 14 of 16 routes unauthenticated; unauthenticated DELETE /api/runs drops the audit tables; anyone can mint an auditor token. Localhost only — this is not deployable.",
        "status": "OPEN",
        "source": "accountability-layer-audit.md §2 (audit of commit fe45eb4)",
    },
    {
        "id": "input-provenance-heuristic",
        "severity": "medium",
        "area": "UI",
        "title": "The input-provenance marker has a real false-positive mode",
        "detail": "The compare UI marks each cited number as matching, or not matching, a value the "
                  "producer was actually handed. It is a normalised numeric comparison against that "
                  "agent's context, with a rounding tolerance — NOT claim verification. A "
                  "legitimately derived figure (a ratio computed from two input values) does not "
                  "appear in the input and is therefore marked 'no input value matches' while being "
                  "perfectly sound. Treat the marker as a pointer for a human, which is how the "
                  "AAPL 0.34 fabrication was actually found. It is untested against any corpus.",
        "status": "OPEN",
        "source": "Introduced 2026-09-04 with the compare UI v2; see logs/RUN_LOG.md",
    },
    {
        "id": "no-route-tests",
        "severity": "medium",
        "area": "Testing",
        "title": "/api/compare has no automated test",
        "detail": "No route in web/server.py had one; verification was a single manual smoke test (AAPL auditor scope, MSFT "
                  "investor scope, mock provider). RESOLVED 2026-09-27 for /api/compare: tests/test_compare_route.py drives it "
                  "with scripted agents, and route tests now also cover /api/compare/stream, /api/chat/stream, /api/runs reads, "
                  "decisions, source-snippet, facts/excerpt, audit, export.md, sessions and \"/\" (test_concurrency_and_stream, "
                  "test_trace_withholding, test_gate, test_audit, test_cutover). Still without a route test: the plain "
                  "/api/chat, /api/config, DELETE /api/runs, replay, contradictions, /api/self-report and /api/directive.",
        "status": "RESOLVED",
        "source": "status doc §3.3; tests/test_compare_route.py; logs/RUN_LOG.md 2026-09-27 ledger refresh entry",
    },
    {
        "id": "retry-halt-unproven",
        "severity": "medium",
        "area": "Testing",
        "title": "ADR-07 retry/halt never observed firing on a real model",
        "detail": "24 real agent-runs produced zero retries and zero halts. Good reliability news, but the retry/halt path's real-world correctness is unproven — it is only exercised by mock_adapter.py's scripted failures. "
                  "RESOLVED 2026-09-27, observed: counted from the stored runs (web/data/accountability.db, LangChain provider, "
                  "real models only), 48 agent-runs from 2026-09-22 to 2026-09-24 include 13 retries (llama3.2 9, "
                  "gemini-2.5-flash 4). 4 recovered on attempt 2 (PARSE_FAILURE then SUCCESS) and 9 halted (PARSE_FAILURE "
                  "then HALT), each stored with its reasoning objects, e.g. MSFT 55df46d2 (recovered) and da03160a (halted). "
                  "Counted from reasoning objects, not the step trace (see consistency-probe-shown-as-retry). Observed "
                  "firing is not the same as judged correct in every case: nobody has reviewed the 9 halts one by one.",
        "status": "RESOLVED",
        "source": "Live test 4; web/data/accountability.db; logs/RUN_LOG.md 2026-09-27 ledger refresh entry",
    },
    {
        "id": "gemini-key-unconfirmed",
        "severity": "low",
        "area": "Config",
        "title": "GEMINI_API_KEY is configured but never confirmed working",
        "detail": "A key was written to .env. The first live attempt returned a suspended-key 403 from Google, and no successful Gemini call has been observed since. 'Configured' and 'working' are two different facts.",
        "status": "OPEN",
        "source": "logs/RUN_LOG.md 2026-08-29 live-run entries",
    },
    {
        "id": "http-no-model-override",
        "severity": "low",
        "area": "API",
        "title": "Per-producer model override is CLI-only",
        "detail": "scripts/run_cross_agent_live.py accepts --agent-a-model / --agent-b-model so the two producers can run on genuinely different models. /api/compare uses one shared adapter for both sides, so a comparison run from this UI is same-model-twice.",
        "status": "OPEN",
        "source": "status doc §1.3, §3.3",
    },
    {
        "id": "escalation-undefined",
        "severity": "info",
        "area": "Scope",
        "title": "What happens when a contradiction fires is undefined",
        "detail": "Until 2026-09-25 the system recorded the flag and stopped: no escalation workflow, no approval gate, no named reviewer (a deliberate v1 boundary). "
                  "RESOLVED for mismatches by BG: a compare run with a MISMATCH figure is AWAITING_DECISION until a named human records a decision for every "
                  "mismatched figure (validation/gate.py; append-only gate_decisions table). NOT covered: figures cited by one agent only, halted runs, "
                  "and the accounting-check / no-consensus triggers the roadmap assigns to B3 and B5.",
        "status": "RESOLVED",
        "source": "proposal §8 item 4; sdd.md §14 and its 2026-09-25 addendum; logs/RUN_LOG.md 2026-09-25",
    },
    {
        "id": "checks-lexical-coverage",
        "severity": "medium",
        "area": "Verification",
        "title": "Accounting checks only see figures the tagger recognises",
        "detail": "validation/constraints.py runs on validation/facts.py's extracted figures, so its coverage is the tagger's: an unrecognised "
                  "phrasing is never checked, EPS stated without 'basic' or 'diluted' is not checked against the filing, and a construction like "
                  "'EPS diluted and basic are $2.02 and $2.03, respectively' yields only the first figure (seen live on AAPL, 2026-09-25). A check "
                  "that doesn't run is not shown, so absence of a failure is not evidence of a correct figure. Source-sanity checks use the latest "
                  "period all a rule's figures share, which can differ from the period the agents were given (MSFT, 2026-09-25: agents given Q3, "
                  "filing checks on the fiscal year).",
        "status": "OPEN",
        "source": "logs/RUN_LOG.md 2026-09-25 B2 + B3 entry",
    },
    {
        "id": "ollama-hangs-under-compare",
        "severity": "high",
        "area": "Runtime",
        "title": "The local model server stopped responding during compare runs (four times)",
        "detail": "Observed 2026-09-25, twice: during two-agent compare runs, Ollama stopped answering even a bare 5-token "
                  "/api/generate from outside the app, and the runs' model calls never returned (no timeout exists, so they "
                  "waited indefinitely). Both times Ollama answered immediately after this server was restarted, which dropped "
                  "its open connections. Hypothesis, not confirmed: two concurrent tool-calling requests to one local model "
                  "can wedge it. CROSS_AGENT_MAX_CONCURRENCY=1 (one agent at a time) is the obvious mitigation and has NOT "
                  "been tried. The live view shows such a run honestly (the timer keeps counting on a step that never ends). "
                  "UPDATE 2026-09-26: two more times, both during ticker compares that now make an extra extraction call per "
                  "agent; each time a 5-token request from outside hung too, and each time Ollama answered right after the "
                  "server restarted. Five observations, same pattern; still not a confirmed cause. "
                  "CORRECTION 2026-09-27: four, not five. The RUN_LOG records two on 2026-09-25 and two on 2026-09-26. "
                  "UPDATE 2026-09-27: model calls now have a timeout (MODEL_TIMEOUT_S, default 120 s with nothing received), "
                  "so a hung call ends and its run is recorded as halted with the error instead of waiting indefinitely. That "
                  "bounds the damage; it doesn't fix the hang, whose cause is still unconfirmed. Ollama may stay wedged after a "
                  "timeout until its connections drop, which hasn't been tested. CROSS_AGENT_MAX_CONCURRENCY=1 is still untried.",
        "status": "OPEN",
        "source": "logs/RUN_LOG.md 2026-09-25 B2 + B3 and BP + U4 entries; 2026-09-27 ledger refresh entry; tests/test_model_timeout.py",
    },
    {
        "id": "filing-excerpt-coverage",
        "severity": "low",
        "area": "Provenance",
        "title": "Filing excerpts cover recent inline-XBRL primary documents only",
        "detail": "datasources/filings.py finds a figure by its us-gaap tag and a consolidated (no-dimension) context with the "
                  "same period, in the filing's primary document. Measured live 2026-09-25: 24 of 24 figures the agents were "
                  "given (AAPL, MSFT, NVDA, GOOGL) found, every filed value equal to companyfacts'. Not covered: filings older "
                  "than the company's ~1000 most recent (reported as not_in_index), figures only in exhibits, pre-2019 "
                  "non-inline filings (no_inline_xbrl). Row labels and column headers come from table-layout heuristics that "
                  "have been checked on those four filers only. There is no UI for it yet (U6). "
                  "UPDATE 2026-09-26: U6 shipped the UI (Source buttons on every given figure and matrix cell), verified live on "
                  "AAPL's net income against the real 10-Q; the coverage limits above are unchanged.",
        "status": "OPEN",
        "source": "logs/RUN_LOG.md 2026-09-25 BP + U4 entry; tests/test_filings.py",
    },
    {
        "id": "trace-leaks-disputed-values",
        "severity": "high",
        "area": "Security",
        "title": "The run trace let a disputed figure through the decision gate to investors",
        "detail": "Found 2026-09-26: the investor-scope read of gated run ec1a3b44 (AWAITING_DECISION, agents disputing 1998 vs 1996) "
                  "withheld both conclusions and both values, but still carried \"1998\" once, inside a Nintendo search result in the "
                  "run trace (step 5's detail). The BG + U3 log entry had said the read contained neither year, and that search previews "
                  "'None did in ec1a3b44'; both were wrong. The same text was reachable through the live stream's step events, "
                  "/api/runs/{id}/source-snippet (no scope check) and, for failed checks, GET /api/runs/{id}/decisions. FIXED IN CODE the "
                  "same day (validation/gate.py strip_search_content, applied by redact_for_scope, the investor stream and both routes; "
                  "tests/test_trace_withholding.py asserts the real gated run's investor read contains neither value). Kept OPEN until "
                  "observed on a restarted server: the dev server running when this was written predates the fix. Not covered: text a "
                  "user supplied as a generic run's context, which investors still see as the input. "
                  "UPDATE 2026-09-26: observed on a restarted server — the investor read of ec1a3b44 (still AWAITING_DECISION) now "
                  "contains 0 x '1998' and 0 x '1996', tool steps 4 and 5 are marked withheld, and the run list, session, decisions "
                  "and source-snippet routes carry neither value at investor scope; the auditor read still has the full trace. The "
                  "generic-context limit above is unchanged.",
        "status": "RESOLVED",
        "source": "logs/RUN_LOG.md 2026-09-26 correction entry and its verification entry; tests/test_trace_withholding.py",
    },
    {
        "id": "assessment-not-produced",
        "severity": "medium",
        "area": "Model",
        "title": "Structured assessments are built but not being produced",
        "detail": "B4 added an optional <assessment> block (grade, direction, assumptions) in directive v1.6.0, with strict "
                  "validation, recording and UI. Made active 2026-09-26 and reverted the same day: live, 2 of 10 first attempts "
                  "passed the format check under v1.6.0 (llama3.2 mostly left </thought_log> unclosed and nested the other blocks "
                  "inside it), against 7 of 8 under v1.5.2 the day before. Both successes gave an assessment, but with ungrounded "
                  "key points, and one failed attempt's key points misquoted its context 10x (key points are not checked by B3). "
                  "v1.5.2 is active again, so no new run asks for an assessment. How to obtain them — a separate extraction call "
                  "labelled as a model judgment, reworded directive, or a larger model — is a human decision. "
                  "UPDATE 2026-09-26: the human chose the separate extraction call. Ticker compares now get one per agent "
                  "(core/assessment.py extract_assessment; prompt assess-extract-v2), after the unchanged two-block check. Live: "
                  "5 of 5 successful answers got a usable assessment (all partial: the extraction's own additions were dropped, "
                  "e.g. an unstated horizon, or a past growth rate reported as an assumption). Few runs, one model.",
        "status": "RESOLVED",
        "source": "logs/RUN_LOG.md 2026-09-26 B4 + U7 entry",
    },
    {
        "id": "bull-bear-unmeasured",
        "severity": "low",
        "area": "Model",
        "title": "The bull/bear pairing has four live agent runs behind it",
        "detail": "Under the active v1.5.2 (2026-09-26, AAPL and NVDA): bear passed the format check 2 of 2, bull 0 of 2 (both "
                  "halted, ordinary structure failures). AAPL's bear said the figures don't support a bearish view but added an "
                  "unsupported 'despite the losses'; NVDA's bear argued from search results rather than the filing figures. "
                  "Too few runs to say whether the briefs themselves hurt compliance or grounding.",
        "status": "OPEN",
        "source": "logs/RUN_LOG.md 2026-09-26 B4 + U7 entry",
    },
    {
        "id": "synthesis-thin-and-lexical",
        "severity": "medium",
        "area": "Comparator",
        "title": "Grade synthesis rests on a few live runs and a lexical check",
        "detail": "B5 (validation/divergence.py) classifies a disagreement as data / assumption / weighting from recorded rows, "
                  "checks and extracted assessments. Observed live 2026-09-26 on two AAPL/NVDA runs, both classed 'assumption' — "
                  "but with extraction v1 those 'assumptions' were past growth rates (AAPL's 16% year over year, NVDA's 106%), "
                  "so the class was wrong. v2 keeps a growth assumption only if the agent's own sentence with that number looks "
                  "forward (expect, guidance, outlook...) — a word list, which a sentence mixing past and guided growth can fool. "
                  "A run where the agents agree gets a proposed consensus, but there is no way yet to confirm it as the "
                  "published grade: only a disagreement opens a grade decision.",
        "status": "OPEN",
        "source": "logs/RUN_LOG.md 2026-09-26 option 1 + B5 + U8 entry",
    },
    {
        "id": "clear-all-runs-not-in-ui",
        "severity": "info",
        "area": "Scope",
        "title": "\"Clear all runs\" is deliberately not in the new UI",
        "detail": "The classic UI had a button for DELETE /api/runs, which drops every table — runs, the append-only decisions "
                  "and flags. That contradicts the repository's never-delete rule, so the React app that replaced it on "
                  "2026-09-27 has no such button. The route itself is unchanged (admin/test use) and still unauthenticated "
                  "(see audit-criticals).",
        "status": "BY_DESIGN",
        "source": "archive/web-static-legacy/README.md; logs/RUN_LOG.md 2026-09-27 B6 + U9 entry",
    },
    {
        "id": "cached-classic-ui",
        "severity": "low",
        "area": "UI",
        "title": "A browser can keep showing the archived classic UI for a while",
        "detail": "Before the cutover, \"/\" was a plain file response that browsers cached without revalidating. Seen "
                  "2026-09-27: a tab that had loaded the classic UI kept showing it after \"/\" started redirecting to /app/, "
                  "with its /static/ assets now 404 on the server. It clears once the browser revalidates, or on a hard "
                  "refresh. \"/\" now sends Cache-Control: no-store, so this can't recur for whatever \"/\" becomes next.",
        "status": "OPEN",
        "source": "logs/RUN_LOG.md 2026-09-27 B6 + U9 entry; tests/test_cutover.py",
    },
    {
        "id": "consistency-probe-shown-as-retry",
        "severity": "medium",
        "area": "Trace",
        "title": "A chat run's consistency probe is traced and shown as a retry",
        "detail": "The chat route's consistency probe (ADR-06, on by default for non-Gemini models) asks the same question "
                  "again through the same traced adapter, so its call is recorded as \"LLM attempt 2\" and the live view "
                  "says \"Retrying (attempt 2)\". Found 2026-09-27 on chat run 3f1b0f89: the trace has LLM attempts 1 and 2, "
                  "while its reasoning objects hold one attempt (SUCCESS) and its consistency block holds the probe's answer. "
                  "The RUN_LOG's 2026-09-27 B6 + U9 entry reported that as a retry; it was not. A reviewer reading the trace "
                  "sees a retry that never happened (P6: the trace and the record disagree). Not fixed yet.",
        "status": "OPEN",
        "source": "web/server.py chat route (run_consistency_probe with the wrapped adapter); web/step_trace.py wrap_adapter; "
                  "logs/RUN_LOG.md 2026-09-27 ledger refresh entry",
    },
    {
        "id": "gate-identity-self-declared",
        "severity": "medium",
        "area": "Security",
        "title": "The decision gate records a typed name, not an authenticated person",
        "detail": "The JWT carries a scope, not an identity, so decided_by is whatever the reviewer typed; every gate payload says so. "
                  "Any auditor-scoped token can record a decision, and anyone can mint one (see audit-criticals). The investor withholding "
                  "is also only as strong as read auth: a read with no token is served at the run's stored scope. A real identity is a separate auth project.",
        "status": "OPEN",
        "source": "validation/gate.py IDENTITY_NOTE; logs/RUN_LOG.md 2026-09-25",
    },
    {
        "id": "recipe-adoption",
        "severity": "info",
        "area": "Scope",
        "title": "Whether to adopt the existing contradiction-detection-agent recipe is undecided",
        "detail": "The repo already carries a 16-node scaffolded recipe for this capability. Structurally compatible with this implementation either way, but no decision has been made.",
        "status": "BY_DESIGN",
        "source": "proposal §8 item 3; sdd.md §12",
    },
]


# ── Automated suite ────────────────────────────────────────────────────────────

def _discover_test_counts() -> dict[str, Any]:
    """
    Count the automated suite by discovery, not by a hard-coded number that goes
    stale. Discovery imports the test modules but does not run them.

    Returns counts per module plus a total. On failure, returns an explicit error
    rather than a plausible-looking zero.
    """
    try:
        loader = unittest.TestLoader()
        suite = loader.discover(str(_TESTS_DIR), top_level_dir=str(_TESTS_DIR.parent))
    except Exception as exc:  # noqa: BLE001 - report the failure, never fake a count
        return {"error": f"{type(exc).__name__}: {exc}", "modules": [], "total": None}

    per_module: dict[str, int] = {}

    def walk(item) -> None:
        if isinstance(item, unittest.TestSuite):
            for child in item:
                walk(child)
            return
        module = type(item).__module__.split(".")[-1]
        per_module[module] = per_module.get(module, 0) + 1

    walk(suite)

    modules = [{"module": name, "tests": n} for name, n in sorted(per_module.items())]
    return {
        "error": None,
        "modules": modules,
        "total": sum(per_module.values()),
        "load_errors": [m["module"] for m in modules if m["module"].startswith("_Failed")],
    }


# ── Public API ─────────────────────────────────────────────────────────────────

def build_self_report() -> dict[str, Any]:
    """
    Everything the UI needs to show what has been tested and what is broken.

    Test counts are computed live. Live-model results and known issues are the
    recorded findings from this subsystem's own logs, each with its source.
    """
    issues = KNOWN_ISSUES
    open_count = sum(1 for i in issues if i["status"] in ("OPEN", "UNVERIFIED"))

    return {
        "automated_tests": _discover_test_counts(),
        "live_model_tests": {
            "run_on": "2026-08-29 to 2026-09-11",
            "model": "qwen2.5:7b (Ollama, local); test 6 (2026-09-11) also used mistral-7b -- see each test's own record for which model(s) it used",
            "tests": LIVE_MODEL_TESTS,
            "caveats": LIVE_MODEL_TESTS_CAVEATS,
        },
        "known_issues": issues,
        "counts": {
            "issues_total": len(issues),
            "issues_open": open_count,
            "issues_critical": sum(1 for i in issues if i["severity"] == "critical"),
            "live_tests_gaps_found": sum(1 for t in LIVE_MODEL_TESTS if t["outcome"] == "gap_found"),
        },
        "deployment_status": {
            "state": "PROTOTYPE",
            "detail": "Localhost only. Not deployable: four CRITICAL audit findings are open, "
                      "and the branch carrying this work is not merged.",
        },
    }
