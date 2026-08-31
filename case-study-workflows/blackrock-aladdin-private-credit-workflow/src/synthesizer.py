"""
Synthesis Module.

Input: full accumulated context (parsed intent, benchmark results, and
portfolio holdings data).
Output: the final text answer returned to the human. Text-only in this
reference implementation — chart/visual output is a labeled extension
point, not built here (see README's Extension Points section).

§3.6 is explicit and non-negotiable: "This module does not recommend an
action, flag a decision, or take any position on what the human should do
next. It reports what was found." That's architecture principle 1 (no
execution authority) enforced at the prompt level, not just assumed.
"""
from .llm_providers import LLMProvider

SYNTHESIS_SYSTEM_PROMPT = """You are a report-writing assistant for a private credit \
analytics system. You will be given a parsed question, computed benchmark ratios, and \
portfolio holdings data. Write a plain-language summary for a portfolio manager.

Strict rules:
1. Only cite figures that appear in the data provided below. Never estimate, invent, or \
state a figure not present in the data.
2. Report findings neutrally. Never write "you should," "we recommend," or imply what \
the reader should do next — that decision belongs entirely to the human reading this.
3. If a metric has a flag noted, mention it plainly as an observation, not as an \
instruction to act.
4. Write for a person who will decide what happens next — not someone who will act \
directly on this text."""


class ResponseSynthesizer:
    """Stateless — all context is passed into draft() per call."""

    def draft(self, intent, benchmark_results: list, portfolio_data: list,
              llm: LLMProvider, avoid_unverified: list = None) -> str:
        context = self._format_context(intent, benchmark_results, portfolio_data)
        system_prompt = SYNTHESIS_SYSTEM_PROMPT
        if avoid_unverified:
            system_prompt += (
                f"\n\nA prior draft cited these figures without support in the data: "
                f"{avoid_unverified}. Do not restate them unless you can derive them "
                f"directly from the data below."
            )
        return llm.complete(prompt=context, system=system_prompt)

    def _format_context(self, intent, benchmark_results: list, portfolio_data: list) -> str:
        lines = [f"Question: {intent.raw_query}", f"Entity: {intent.borrower_or_entity}", ""]
        if benchmark_results:
            lines.append("Computed benchmarks:")
            for r in benchmark_results:
                flag_note = f" [FLAG: {r.flag}]" if r.flag else ""
                lines.append(f"  - {r.metric}: {r.value:.4f} (source: {r.source_record_id}){flag_note}")
        if portfolio_data:
            lines.append("\nPortfolio holdings:")
            for p in portfolio_data:
                lines.append(
                    f"  - fund {p['fund_id']}: position ${p['position_size']:,.0f}, "
                    f"market value ${p['market_value']:,.0f}, "
                    f"allocation {p['allocation_pct'] * 100:.1f}%"
                )
        return "\n".join(lines)
