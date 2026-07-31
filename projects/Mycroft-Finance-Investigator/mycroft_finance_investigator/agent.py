"""Single-agent observe-plan-act investigation loop."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Callable

from .finance import FinanceEngine


Tool = Callable[..., dict[str, Any]]


@dataclass(frozen=True)
class Action:
    tool: str
    arguments: dict[str, str]
    reason: str


@dataclass
class InvestigationState:
    question: str
    threshold: Decimal
    pending: list[Action] = field(default_factory=list)
    trace: list[dict[str, Any]] = field(default_factory=list)
    findings: list[dict[str, Any]] = field(default_factory=list)
    evidence: set[str] = field(default_factory=set)
    categories_scheduled: set[str] = field(default_factory=set)


class InvestigationAgent:
    """Plans tool calls from observations while calculations remain deterministic."""

    def __init__(self, engine: FinanceEngine, max_steps: int = 20):
        self.engine = engine
        self.max_steps = max_steps
        self.tools: dict[str, Tool] = {
            "scan_material_variances": self._scan_material_variances,
            "analyze_category": self._analyze_category,
            "inspect_driver_records": self._inspect_driver_records,
        }

    def _scan_material_variances(self, threshold: str) -> dict[str, Any]:
        amount = Decimal(threshold)
        ebitda = self.engine.ebitda_variance()
        category_bridge = self.engine.category_variances()
        categories = self.engine.material_categories(amount)
        return {
            "ebitda": ebitda.to_dict(),
            "category_bridge": [line.to_dict() for line in category_bridge],
            "material_categories": [line.to_dict() for line in categories],
        }

    def _analyze_category(self, category: str, threshold: str) -> dict[str, Any]:
        lines = self.engine.accounts_for_category(category, Decimal(threshold))
        return {
            "category": category,
            "material_accounts": [line.to_dict() for line in lines],
        }

    def _inspect_driver_records(self, category: str) -> dict[str, Any]:
        return {
            "category": category,
            "driver_records": self.engine.driver_rows(category),
            "boundary": "Records are correlated inputs, not approved causal explanations.",
        }

    def _observe_and_plan(
        self, state: InvestigationState, action: Action, observation: dict[str, Any]
    ) -> None:
        if action.tool == "scan_material_variances":
            ebitda = observation["ebitda"]
            state.findings.append(
                {
                    "kind": "VERIFIED_CALCULATION",
                    "statement": (
                        f"Actual EBITDA was {ebitda['actual']} versus budget "
                        f"{ebitda['budget']}, a variance of {ebitda['variance']}."
                    ),
                    "performance_impact": ebitda["performance_impact"],
                    "evidence": ebitda["evidence"],
                }
            )
            state.evidence.update(ebitda["evidence"])
            for line in observation["category_bridge"]:
                state.findings.append(
                    {
                        "kind": "VERIFIED_CALCULATION",
                        "statement": (
                            f"{line['label']} contributed EBITDA performance impact "
                            f"{line['performance_impact']} from actual {line['actual']} "
                            f"versus budget {line['budget']}."
                        ),
                        "performance_impact": line["performance_impact"],
                        "evidence": line["evidence"],
                    }
                )
                state.evidence.update(line["evidence"])
            for line in observation["material_categories"]:
                category = str(line["category"])
                if category in state.categories_scheduled:
                    continue
                state.categories_scheduled.add(category)
                state.pending.append(
                    Action(
                        tool="analyze_category",
                        arguments={
                            "category": category,
                            "threshold": str(state.threshold),
                        },
                        reason=(
                            f"{category} has performance impact "
                            f"{line['performance_impact']}, above the configured threshold"
                        ),
                    )
                )
        elif action.tool == "analyze_category":
            category = observation["category"]
            accounts = observation["material_accounts"]
            for line in accounts:
                state.findings.append(
                    {
                        "kind": "VERIFIED_CALCULATION",
                        "statement": (
                            f"{line['label']} had actual {line['actual']} versus "
                            f"budget {line['budget']}; EBITDA performance impact "
                            f"{line['performance_impact']}."
                        ),
                        "performance_impact": line["performance_impact"],
                        "evidence": line["evidence"],
                    }
                )
                state.evidence.update(line["evidence"])
            if category in {"revenue", "payroll"}:
                state.pending.append(
                    Action(
                        tool="inspect_driver_records",
                        arguments={"category": category},
                        reason=f"{category} has a verified operational driver dataset",
                    )
                )
        elif action.tool == "inspect_driver_records":
            rows = observation["driver_records"]
            evidence = [row["evidence"] for row in rows]
            state.evidence.update(evidence)
            state.findings.append(
                {
                    "kind": "INVESTIGATION_PROMPT",
                    "statement": (
                        f"{len(rows)} {observation['category']} driver records were "
                        "attached for owner review; no causal conclusion was generated."
                    ),
                    "performance_impact": None,
                    "evidence": evidence,
                }
            )

    def run(self, question: str, threshold: Decimal) -> dict[str, Any]:
        state = InvestigationState(question=question, threshold=threshold)
        state.pending.append(
            Action(
                tool="scan_material_variances",
                arguments={"threshold": str(threshold)},
                reason="Begin with a reconciled EBITDA bridge and materiality scan",
            )
        )
        steps = 0
        while state.pending:
            if steps >= self.max_steps:
                raise RuntimeError(
                    f"investigation exceeded the configured {self.max_steps} step limit"
                )
            action = state.pending.pop(0)
            tool = self.tools[action.tool]
            observation = tool(**action.arguments)
            state.trace.append(
                {
                    "step": steps + 1,
                    "tool": action.tool,
                    "arguments": action.arguments,
                    "reason": action.reason,
                    "observation": observation,
                }
            )
            self._observe_and_plan(state, action, observation)
            steps += 1

        return {
            "question": question,
            "status": "COMPLETED_PENDING_HUMAN_REVIEW",
            "agent": {
                "name": "monthly-performance-investigator",
                "policy": "local-evidence-driven-v0.1",
                "steps": steps,
            },
            "findings": state.findings,
            "evidence": sorted(state.evidence),
            "trace": state.trace,
            "current_explanation": None,
            "human_gate": {
                "status": "OPEN",
                "required": [
                    "Approve or replace the demo materiality threshold",
                    "Supply and evidence current-period causal explanations",
                    "Approve or block distribution",
                ],
            },
        }
