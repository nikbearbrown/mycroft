# rag grader

## Purpose

The rag grader evaluates whether a RAG answer is relevant to the question, grounded in retrieved facts, and free of obvious factual or internal conflicts before the answer is trusted in a Mycroft report.

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Question | String | Calling workflow log or chat run | Yes |
| Student answer / RAG output | String | Calling workflow log | Yes |
| Retrieved facts | Array/string | `intermediateSteps`, sources, or observations from calling workflow | Yes for groundedness |
| Model credential | Environment variable | `OPENROUTER_API_KEY` for future live grading adapter | No for local dialogic mode |

## Phase Gates

1. Input gate: question and answer must be present. Verification: run `python3 scripts/tools/rag_relevance_grader.py` and confirm the output contains `relevant`. Human capacity: [PA].
2. Grounding gate: retrieved facts or observations must be available before groundedness is trusted. Verification: run `python3 scripts/tools/rag_groundedness_grader.py` and confirm `grounded` is false when facts are absent. Human capacity: [PA], [IJ].
3. Parser gate: each grader output must conform to its boolean schema. Verification: run `python3 scripts/gigo/parse_relevance_grade.py`, `python3 scripts/gigo/parse_groundedness_grade.py`, and `python3 scripts/gigo/parse_correctness_grade.py`. Human capacity: [PA].
4. Merge gate: final grade must expose all three dimensions and an overall pass/fail. Verification: run `python3 scripts/tools/merge_rag_grades.py`. Human capacity: [EI].

## Steps

1. Receive grading request. Labor: AI. Script called: none; conductor trigger. Input: passthrough payload from calling workflow. Output: grading run record. Where output goes: `logs/`.
2. Grade relevance. Labor: AI. Script called: `scripts/tools/rag_relevance_grader.py`. Input: question and answer. Output: relevance grade. Where output goes: `logs/`.
3. Grade groundedness. Labor: AI. Script called: `scripts/tools/rag_groundedness_grader.py`. Input: answer and retrieved facts. Output: groundedness grade. Where output goes: `logs/`.
4. Grade correctness. Labor: AI. Script called: `scripts/tools/rag_correctness_grader.py`. Input: question and answer. Output: correctness grade. Where output goes: `logs/`.
5. Validate grader schemas. Labor: AI. Script called: `scripts/gigo/parse_relevance_grade.py`, `scripts/gigo/parse_groundedness_grade.py`, and `scripts/gigo/parse_correctness_grade.py`. Input: raw grade records. Output: normalized grade records. Where output goes: `logs/`.
6. Merge grades. Labor: AI. Script called: `scripts/tools/merge_rag_grades.py`. Input: normalized grade records. Output: combined grade summary. Where output goes: `logs/`.
7. Review failure modes. Labor: Human. Human action required: decide whether a failed grade reflects bad retrieval, bad answer generation, missing facts, or a too-strict grader. Output: remediation decision. Where output goes: `reports/generated/`.

## Output Contract

### Agent output

Agent output goes to `logs/rag-grader/<run-id>.json`. It must include `question`, `answer_preview`, `fact_count`, `correctness`, `relevance`, `groundedness`, `passed`, `scripts_used`, `validation_results`, and any missing-input flags.

### Human report

The human report goes to `reports/generated/rag-grader-<date>.md`. It surfaces which answers passed, which dimension failed, and what decision the human should make about rerunning retrieval, revising prompts, or rejecting the answer.

## Stop Conditions

- Stop if the question or answer is missing.
- Stop if groundedness is requested but no facts, sources, or intermediate observations are present.
- Stop if any parser output lacks the required boolean field.
- Stop if the merged grade omits correctness, relevance, or groundedness.
- Stop before treating a local lexical grade as a definitive semantic evaluation without human review.

## Provenance

Original n8n JSON: `data/mycroft-main/n8n-workflows/originals/Core_Components/news_monitoring_agent/workflows/rag grader.json`
