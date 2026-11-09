"""
extract/extract_signals_local.py  —  Sprint 4: local LLM extraction (Ollama).

Same extraction as Sprint 3, but the model runs ENTIRELY ON YOUR MACHINE via Ollama
-- no API, no key, no internet, no cost. The point of Sprint 4 is the COMPARISON:
does a local model extract as well as the Groq API model did (Sprint 3)?

Prerequisite (do this first):
  1. Install Ollama:  https://ollama.com  (Windows installer)
  2. Pull a model:    ollama pull llama3.2
  3. Ollama runs as a background service after install.

Setup:
    pip install langchain-ollama pydantic

Run (NO API key needed):
    python -m extract.extract_signals_local data/raw/news_signals.json --limit 2
    python -m extract.extract_signals_local data/raw/news_signals.json --out data/extracted/local_signals.json

Boundary unchanged: the model EXTRACTS; it does not decide or validate.
Every signal stays validated_by = None (P2). A human validates before it counts.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pydantic import BaseModel, Field  # noqa: E402


class ExtractedSignal(BaseModel):
    signal_type: str = Field(
        description="one of: funding_round, funding_stage, layoff, executive_change, "
                    "security_issue, product_launch, news_mention"
    )
    amount_usd: Optional[str] = Field(default=None, description="funding amount if mentioned; else null")
    occurred_date: Optional[str] = Field(default=None, description="ISO date if clearly present; else null")
    confidence: int = Field(description="0-100 confidence. Low if vague. Never invent details.")
    reasoning: str = Field(description="one short sentence: why this type/these values")


_MODEL = ["llama3.2"]  # set from CLI; used for the log label


def build_extractor(model_name: str):
    from langchain_ollama import ChatOllama
    llm = ChatOllama(model=model_name, temperature=0)
    return llm.with_structured_output(ExtractedSignal)


SYSTEM = (
    "You extract structured financial/company signals from a news headline. "
    "Return only what the text supports. If the headline is a vague mention with no "
    "funding/layoff/exec/security/launch content, use signal_type 'news_mention' and "
    "low confidence. Never invent an amount or a date that isn't in the text."
)


def extract_one(extractor, raw: dict) -> dict:
    headline = raw.get("signal_title", "")
    company = raw.get("company_id", "")
    prompt = f"{SYSTEM}\n\nCompany: {company}\nHeadline: {headline}\n\nExtract the signal."
    result: ExtractedSignal = extractor.invoke(prompt)

    enriched = dict(raw)
    enriched["signal_type"] = result.signal_type
    if result.amount_usd:
        enriched["signal_value"] = result.amount_usd
    if result.occurred_date:
        enriched["occurred_date"] = result.occurred_date
    enriched["score"] = result.confidence
    enriched["extraction_reasoning"] = result.reasoning
    enriched["extraction_model"] = f"ollama:{_MODEL[0]}"
    enriched["validated_by"] = None  # P2: still needs a human
    return enriched


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("raw_path")
    ap.add_argument("--model", default="llama3.2", help="local Ollama model (default llama3.2)")
    ap.add_argument("--out", default=None)
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    _MODEL[0] = args.model

    raw_signals = json.load(open(args.raw_path))
    if args.limit:
        raw_signals = raw_signals[: args.limit]
    if not raw_signals:
        print("No raw signals to extract. Run the agent/fetch first.")
        return 0

    try:
        extractor = build_extractor(args.model)
    except Exception as e:
        raise SystemExit(
            f"Could not start the local model '{args.model}'. Checklist:\n"
            "  1. Ollama installed?  https://ollama.com\n"
            f"  2. Model pulled?      ollama pull {args.model}\n"
            "  3. Ollama running?    (background service)\n"
            f"\nUnderlying error: {e}"
        )

    print(f"LOCAL LLM EXTRACTION (Ollama: {args.model}) -- free, offline")
    print("=" * 52)
    out = []
    for raw in raw_signals:
        enriched = extract_one(extractor, raw)
        out.append(enriched)
        print(f"\n  {enriched['company_id']}: {raw.get('signal_title','')[:60]}")
        print(f"    -> type={enriched['signal_type']}  value={enriched.get('signal_value')}  "
              f"date={enriched.get('occurred_date')}  conf={enriched['score']}")
        print(f"    reasoning: {enriched['extraction_reasoning']}")
        print(f"    validated_by: None  (still UNVALIDATED -- a human must confirm, P2)")

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        json.dump(out, open(args.out, "w"), indent=2)
        print(f"\n[saved] {len(out)} extracted signals -> {args.out}")
        print("Compare to your Groq (Sprint 3) output: same types? similar confidence?")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
