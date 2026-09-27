"""LLM reader with advanced techniques: few-shot, temporal context, CoT,
self-consistency decoding, and multi-turn verification via Ollama."""

from __future__ import annotations

import base64
import gzip
import json
import logging
import time
from collections import Counter
from typing import Any

import ollama

from ecis.config.settings import settings
from ecis.embedding.embedder import query_similar
from ecis.embedding.exemplar_store import retrieve_exemplars
from ecis.schemas.signal import GuidanceDirection, VerificationStatus

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are a financial analyst specialising in earnings call transcript analysis.
Your task is to determine whether a company has RAISED, LOWERED, or MAINTAINED its financial guidance.

You MUST respond with valid JSON only. No other text before or after the JSON.

Output format:
{
  "direction": "raised" | "lowered" | "maintained" | "none",
  "confidence": <float 0.0 to 1.0>,
  "supporting_quote": "<exact quote from the passage>",
  "reasoning": "<step-by-step reasoning>"
}

Rules:
1. First determine if the statement is forward-looking (guidance) or backward-looking (reporting).
2. Only forward-looking statements about future expectations count as guidance.
3. Determine if this is a CHANGE from prior guidance or a reaffirmation.
4. "maintained" is ONLY for an explicit reaffirmation of prior guidance (e.g. "we are reaffirming", "we maintain our outlook", "no change to our guidance").
5. "none" if there is no forward-looking guidance, or the company simply does not mention a change. Silence or a historical result is not "maintained".
6. Be conservative: if unsure between maintained and none, prefer "none"."""

_MISTRAL_JSON_REMINDER = """
Always emit a complete JSON object. Close every opening brace and bracket.
Do not truncate. Do not wrap the JSON in markdown. End with a final closing brace.
"""

_JSON_REPAIR_USER = (
    "Your previous reply was incomplete or invalid JSON. "
    "Output the complete JSON object only, with all closing braces."
)

_COT_USER_TEMPLATE = """Analyse the following earnings call passage for guidance signals.

{few_shot_section}
{temporal_context_section}

Passage to analyse:
{chunk_text}
END PASSAGE

Think step by step:
1. Is this statement forward-looking or backward-looking?
2. Is it an explicit change, an explicit reaffirmation of prior guidance, or neither?
3. If neither (no guidance, or historical results only), direction is "none" — not "maintained".
4. What specific words or numbers indicate the direction?
5. What is the direction (raised/lowered/maintained/none)?
6. What is your confidence level and why?

Respond with JSON only."""

_VERIFICATION_TEMPLATE = """You previously analysed an earnings call passage and extracted:
- Direction: {direction}
- Confidence: {confidence}
- Supporting quote: "{supporting_quote}"
- Reasoning: {reasoning}

Re-read the original passage below and critically evaluate your extraction.

Original passage:
{chunk_text}
END PASSAGE

Does your extraction hold? Could it be interpreted differently?
Respond with JSON:
{{
  "verdict": "CONFIRM" | "REVISE" | "REJECT",
  "direction": "raised" | "lowered" | "maintained" | "none",
  "confidence": <float>,
  "reasoning": "<why you confirm/revise/reject>"
}}"""


def _build_few_shot_section(chunk_text: str) -> str:
    try:
        exemplars = retrieve_exemplars(chunk_text, n_results=3)
    except Exception:
        logger.debug("Exemplar retrieval failed, proceeding without few-shot")
        return ""

    if not exemplars:
        return ""

    lines = ["Few-shot examples:"]
    for i, ex in enumerate(exemplars, 1):
        meta = ex["metadata"]
        lines.append(f"\nExample {i}:")
        lines.append(f"Passage: {ex['text'][:300]}...")
        lines.append(f"Direction: {meta.get('direction', 'N/A')}")
        lines.append(f"Reasoning: {meta.get('reasoning_trace', 'N/A')[:200]}")
    lines.append("END EXAMPLES\n")
    return "\n".join(lines)


def _build_temporal_context(
    chunk_text: str,
    ticker: str,
    transcript_date: str | None = None,
) -> str:
    date_range = None
    if transcript_date:
        try:
            from datetime import date, timedelta

            end = date.fromisoformat(transcript_date[:10]) - timedelta(days=1)
            start = end - timedelta(days=140)
            date_range = (str(start), str(end))
        except ValueError:
            date_range = None
    try:
        prior = query_similar(
            chunk_text,
            n_results=3,
            ticker=ticker,
            date_range=date_range,
        )
    except Exception:
        logger.debug("Temporal retrieval failed, proceeding without context")
        return ""

    if not prior:
        return ""

    lines = ["Prior quarter context:"]
    for i, p in enumerate(prior, 1):
        meta = p["metadata"]
        lines.append(f"\nPrior {i} (date: {meta.get('transcript_date', 'N/A')}):")
        lines.append(p["text"][:300])
    lines.append("END PRIOR CONTEXT\n")
    return "\n".join(lines)


def _needs_json_reminder(model: str) -> bool:
    name = (model or "").lower()
    return "mistral" in name or "qwen" in name


def _system_prompt(model: str) -> str:
    if _needs_json_reminder(model):
        return _SYSTEM_PROMPT + _MISTRAL_JSON_REMINDER
    return _SYSTEM_PROMPT


def _looks_truncated(raw: str) -> bool:
    if not raw:
        return True
    return raw.count("{") != raw.count("}")


def _ollama_client() -> ollama.Client:
    """Ollama client pointed at OLLAMA_BASE_URL (local or Colab tunnel)."""
    host = (settings.ollama_base_url or "http://localhost:11434").rstrip("/")
    return ollama.Client(host=host)


def encode_provenance(payload: dict[str, Any]) -> str:
    blob = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    return base64.b64encode(gzip.compress(blob)).decode("ascii")


def _chat_once(client: ollama.Client, model_name: str, messages: list[dict], temperature: float) -> str:
    response = client.chat(
        model=model_name,
        messages=messages,
        options={"temperature": temperature},
    )
    return response["message"]["content"]


def _call_ollama(
    messages: list[dict],
    temperature: float = 0.0,
    model: str | None = None,
) -> tuple[str, int]:
    """Return (content, retry_count). Retries malformed JSON up to llm_json_max_retries."""
    model_name = model or settings.llm_model
    client = _ollama_client()
    last = ""
    retries = 0
    max_retries = settings.llm_json_max_retries
    delay = settings.llm_json_retry_base_delay

    for attempt in range(max_retries + 1):
        temp = temperature if attempt == 0 else 0.0
        try:
            last = _chat_once(client, model_name, messages, temp)
        except Exception as exc:
            logger.warning("Ollama call failed (attempt %d): %s", attempt, exc)
            last = ""
        parsed = _parse_llm_json(last) if last else {}
        truncated = _looks_truncated(last)
        parse_failed = parsed.get("reasoning") == "Parse error" or not last
        if last and not truncated and not parse_failed:
            return last, retries
        if attempt < max_retries:
            retries += 1
            if truncated and last:
                messages = messages + [
                    {"role": "assistant", "content": last},
                    {"role": "user", "content": _JSON_REPAIR_USER},
                ]
            time.sleep(delay * (2 ** attempt))
    return last, retries


def _parse_llm_json(raw: str) -> dict[str, Any]:
    raw = raw.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    import re
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start >= 0 and end > start:
        try:
            return json.loads(raw[start:end])
        except json.JSONDecodeError:
            pass

    logger.warning("Could not parse LLM JSON output: %s", raw[:200])
    return {"direction": "none", "confidence": 0.0, "supporting_quote": "", "reasoning": "Parse error"}


def _single_extraction(
    chunk_text: str,
    ticker: str,
    temperature: float,
    model: str | None = None,
    transcript_date: str | None = None,
) -> dict[str, Any]:
    model_name = model or settings.llm_model
    few_shot = _build_few_shot_section(chunk_text)
    temporal = _build_temporal_context(chunk_text, ticker, transcript_date=transcript_date)
    system = _system_prompt(model_name)

    user_msg = _COT_USER_TEMPLATE.format(
        few_shot_section=few_shot,
        temporal_context_section=temporal,
        chunk_text=chunk_text,
    )

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_msg},
    ]

    raw_output, retries = _call_ollama(messages, temperature=temperature, model=model_name)
    result = _parse_llm_json(raw_output)
    result["llm_model"] = model_name
    result["retry_count"] = retries
    result["raw_llm_output"] = raw_output
    result["provenance"] = encode_provenance({
        "system_prompt": system,
        "user_template": user_msg,
        "few_shot": few_shot,
        "temporal_context": temporal,
        "chunk_text": chunk_text,
        "model": model_name,
        "temperature": temperature,
    })
    return result


def _self_consistency_decode(
    chunk_text: str,
    ticker: str,
    model: str | None = None,
    transcript_date: str | None = None,
) -> dict[str, Any]:
    model_name = model or settings.llm_model
    temps = settings.self_consistency_temps
    results = []

    for temp in temps:
        try:
            result = _single_extraction(
                chunk_text, ticker, temp, model=model_name, transcript_date=transcript_date,
            )
            results.append(result)
        except Exception as exc:
            logger.error("Extraction pass at temp %.1f failed: %s", temp, exc)
            results.append({"direction": "none", "confidence": 0.0, "llm_model": model_name})

    directions = [r.get("direction", "none") for r in results]
    counter = Counter(directions)
    most_common, count = counter.most_common(1)[0]

    if count >= 2:
        winning_results = [r for r in results if r.get("direction") == most_common]
        best = max(winning_results, key=lambda r: r.get("confidence", 0.0))

        if count < len(temps):
            best["confidence"] = max(0.0, best.get("confidence", 0.0) - settings.confidence_agreement_threshold)

        out = dict(best)
        out["self_consistency_votes"] = [dict(r) for r in results]
        out["llm_model"] = model_name
        out["retry_count"] = sum(int(r.get("retry_count") or 0) for r in results)
        out["provenance"] = best.get("provenance")
        out["raw_llm_output"] = best.get("raw_llm_output")
        return out

    return {
        "direction": "none",
        "confidence": 0.0,
        "supporting_quote": "",
        "reasoning": "Self-consistency: all passes disagreed, abstaining",
        "self_consistency_votes": results,
        "llm_model": model_name,
    }


def _verify_extraction(
    chunk_text: str,
    extraction: dict[str, Any],
    model: str | None = None,
) -> dict[str, Any]:
    model_name = model or extraction.get("llm_model") or settings.llm_model
    if extraction.get("direction") == "none":
        extraction["verification_status"] = VerificationStatus.REJECTED.value
        extraction["llm_model"] = model_name
        return extraction

    prompt = _VERIFICATION_TEMPLATE.format(
        direction=extraction.get("direction", ""),
        confidence=extraction.get("confidence", 0.0),
        supporting_quote=extraction.get("supporting_quote", ""),
        reasoning=extraction.get("reasoning", ""),
        chunk_text=chunk_text,
    )

    messages = [
        {"role": "system", "content": _system_prompt(model_name)},
        {"role": "user", "content": prompt},
    ]

    try:
        raw, retries = _call_ollama(messages, temperature=0.0, model=model_name)
        verdict = _parse_llm_json(raw)
        extraction["retry_count"] = extraction.get("retry_count", 0) + retries
    except Exception as exc:
        logger.error("Verification call failed: %s", exc)
        extraction["verification_status"] = VerificationStatus.CONFIRMED.value
        extraction["llm_model"] = model_name
        return extraction

    action = verdict.get("verdict", "CONFIRM").upper()

    if action == "CONFIRM":
        extraction["verification_status"] = VerificationStatus.CONFIRMED.value
    elif action == "REVISE":
        extraction["direction"] = verdict.get("direction", extraction["direction"])
        extraction["confidence"] = verdict.get("confidence", extraction["confidence"])
        extraction["reasoning"] = (
            extraction.get("reasoning", "")
            + f"\n[REVISED] {verdict.get('reasoning', '')}"
        )
        extraction["verification_status"] = VerificationStatus.REVISED.value
    elif action == "REJECT":
        extraction["direction"] = "none"
        extraction["confidence"] = 0.0
        extraction["reasoning"] = (
            extraction.get("reasoning", "")
            + f"\n[REJECTED] {verdict.get('reasoning', '')}"
        )
        extraction["verification_status"] = VerificationStatus.REJECTED.value

    extraction["llm_model"] = model_name
    return extraction


def read_chunk(
    chunk_text: str,
    ticker: str,
    *,
    use_self_consistency: bool = True,
    use_verification: bool = True,
    model: str | None = None,
    transcript_date: str | None = None,
) -> dict[str, Any]:
    model_name = model or settings.llm_model

    if use_self_consistency:
        extraction = _self_consistency_decode(
            chunk_text, ticker, model=model_name, transcript_date=transcript_date,
        )
    else:
        extraction = _single_extraction(
            chunk_text, ticker, temperature=0.0, model=model_name, transcript_date=transcript_date,
        )

    if use_verification and extraction.get("direction") != "none":
        extraction = _verify_extraction(chunk_text, extraction, model=model_name)

    extraction["llm_model"] = model_name
    return extraction


def read_chunks(
    chunks: list[dict[str, Any]],
    ticker: str,
    *,
    use_self_consistency: bool = True,
    use_verification: bool = True,
    model: str | None = None,
) -> list[dict[str, Any]]:
    model_name = model or settings.llm_model
    results = []
    for chunk in chunks:
        try:
            result = read_chunk(
                chunk["text"],
                ticker,
                use_self_consistency=use_self_consistency,
                use_verification=use_verification,
                model=model_name,
                transcript_date=chunk.get("transcript_date"),
            )
            result["chunk_index"] = chunk.get("chunk_index", 0)
            result["llm_model"] = model_name
            results.append(result)
        except Exception as exc:
            logger.error("LLM extraction failed for chunk %s: %s", chunk.get("chunk_index"), exc)
            results.append({
                "chunk_index": chunk.get("chunk_index", 0),
                "direction": "none",
                "confidence": 0.0,
                "reasoning": f"Error: {exc}",
                "verification_status": "rejected",
                "llm_model": model_name,
            })
    return results
