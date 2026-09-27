"""
Orchestrator / Query Parser.

Input: raw natural-language query from a portfolio manager or analyst.
Output: structured intent — entity/borrower named, requested metrics, fund
scope — used to scope the tool registry and later the data adapters.

§3.1's own [DEV] marker says this is the one place where LLM choice matters
most, since it's open-ended intent parsing rather than constrained
calculation — and that it should be written against the provider interface,
not a vendor SDK. That's LLMProvider (see llm_providers.py); this module
never imports a vendor SDK directly.
"""
import json
from .models import ParsedIntent
from .llm_providers import LLMProvider

INTENT_SYSTEM_PROMPT = """You are a query parser for a private credit analytics system.
Given a natural-language question from a portfolio manager or analyst, extract:
- borrower_or_entity: the fund, borrower, or asset name mentioned (your best identification)
- requested_metrics: a list drawn ONLY from this exact set: ["money_multiple",
  "leverage_ratio", "valuation_trend", "equity_cushion", "debt_service_coverage",
  "position_size"] — include every metric the question is actually asking about
- fund_scope: a list of fund IDs if explicitly named in the query, otherwise null

Respond with ONLY a JSON object containing exactly these three keys — no
preamble, no markdown code fences, no explanation before or after the JSON."""


class QueryOrchestrator:
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def parse(self, query: str) -> ParsedIntent:
        raw = self.llm.complete(prompt=query, system=INTENT_SYSTEM_PROMPT)
        try:
            return self._to_intent(raw, query)
        except (json.JSONDecodeError, KeyError) as first_error:
            # LLMs asked for JSON don't always return clean JSON on the first
            # try. One retry, with the actual parse error shown back to the
            # model, rather than failing silently on the first bad response.
            correction_prompt = (
                f"{query}\n\n[Your previous response could not be parsed as JSON "
                f"({first_error}). Return ONLY valid JSON with the three required keys.]"
            )
            raw_retry = self.llm.complete(prompt=correction_prompt, system=INTENT_SYSTEM_PROMPT)
            return self._to_intent(raw_retry, query)

    def _to_intent(self, raw: str, original_query: str) -> ParsedIntent:
        cleaned = (
            raw.strip()
            .removeprefix("```json").removeprefix("```")
            .removesuffix("```").strip()
        )
        data = json.loads(cleaned)
        return ParsedIntent(
            borrower_or_entity=data["borrower_or_entity"],
            requested_metrics=data["requested_metrics"],
            fund_scope=data.get("fund_scope"),
            raw_query=original_query,
        )
