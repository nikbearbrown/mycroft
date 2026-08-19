"""
Pipeline Orchestration .

Composition: explicit, not hidden — every
component is a constructor argument, visible in the type signature, testable
and swappable independently of the others.

Run order: Orchestrator → Registry filter → Retrieval (parallel) →
Fund-ID join → Benchmark calc → Synthesis → Guardrail → Human review
(outside this class — see README).

The fund-ID join step didn't exist in any single component's spec on its
own — it was found while tracing a borrower-scoped query by hand before any
code was written. Portfolio holdings can't be filtered by borrower name
directly (see adapters.py's documented limitation), so for a borrower-scoped
query, this step narrows portfolio results to the fund(s) the private-credit
adapter already resolved for that borrower.
"""
import uuid
from .llm_providers import LLMProvider
from .orchestrator import QueryOrchestrator
from .registry_filter import ToolRegistryFilter
from .adapters import PrivateCreditAdapter, PortfolioHoldingsAdapter, retrieve_parallel
from .benchmark_calculator import BenchmarkCalculator
from .synthesizer import ResponseSynthesizer
from .guardrail import GuardrailChecker
from .audit_log import AuditLog
from .models import GuardrailResult


class PrivateCreditQueryPipeline:
    def __init__(
        self,
        llm: LLMProvider,
        orchestrator: QueryOrchestrator,
        registry_filter: ToolRegistryFilter,
        adapters: dict,
        calc: BenchmarkCalculator,
        synthesizer: ResponseSynthesizer,
        guardrail: GuardrailChecker,
        audit_log: AuditLog = None,
    ):
        self.llm = llm
        self.orchestrator = orchestrator
        self.registry_filter = registry_filter
        self.adapters = adapters
        self.calc = calc
        self.synthesizer = synthesizer
        self.guardrail = guardrail
        self.audit_log = audit_log

    async def run(self, query: str) -> GuardrailResult:
        query_id = str(uuid.uuid4())

        intent = self.orchestrator.parse(query)
        self._log(query_id, "orchestrator", str(intent))

        scoped_tools = self.registry_filter.filter(intent, self.adapters)
        self._log(query_id, "registry_filter", str(list(scoped_tools)))

        raw_data = await retrieve_parallel(
            scoped_tools,
            {"fund_scope": intent.fund_scope, "borrower_or_entity": intent.borrower_or_entity},
        )
        self._log(query_id, "retrieval", str(raw_data)[:500])

        private_credit_records = raw_data.get("private_credit", [])
        portfolio_records = raw_data.get("portfolio_holdings", [])

        # Fund-ID join — found via dry-run trace, not part of any single
        # component's original spec. See module docstring.
        if private_credit_records and portfolio_records:
            matched_fund_ids = {r["fund_id"] for r in private_credit_records}
            portfolio_records = [p for p in portfolio_records if p["fund_id"] in matched_fund_ids]

        benchmark_results = self.calc.run(private_credit_records)
        self._log(query_id, "benchmark_calc", str(benchmark_results))

        draft = self.synthesizer.draft(intent, benchmark_results, portfolio_records, self.llm)
        self._log(query_id, "synthesizer", draft)

        result = self.guardrail.screen(
            draft, benchmark_results, portfolio_records, self.synthesizer, self.llm, intent,
            thresholds=self.calc.THRESHOLDS,
        )
        self._log(query_id, "guardrail", result.verified_draft)

        return result

    def _log(self, query_id: str, module: str, output: str) -> None:
        if self.audit_log:
            self.audit_log.append(query_id=query_id, module=module, output=output)


def build_default_pipeline(llm: LLMProvider) -> PrivateCreditQueryPipeline:
    """Quickstart wiring — swap any argument to customize a single component."""
    return PrivateCreditQueryPipeline(
        llm=llm,
        orchestrator=QueryOrchestrator(llm),
        registry_filter=ToolRegistryFilter(),
        adapters={
            "private_credit": PrivateCreditAdapter(),
            "portfolio_holdings": PortfolioHoldingsAdapter(),
        },
        calc=BenchmarkCalculator(),
        synthesizer=ResponseSynthesizer(),
        guardrail=GuardrailChecker(),
        audit_log=AuditLog(),
    )
