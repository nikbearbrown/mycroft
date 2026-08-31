"""
Linear, single-tool pipeline: Intake -> Assistant -> HumanReviewGate ->
Apply & Test. Fail-fast: each stage's failure or rejection halts the
pipeline before the next stage runs. Consistent with this series' practice
(CommBank, Klarna, Lemonade) of modeling a small number of confirmed
functions as one linear pipeline, not a multi-agent system — per the case
study's Section 3.1 finding that HSBC describes a single coding-assistant
capability, not a documented multi-agent architecture.
"""

from .models import PipelineResult
from .intake import validate_vulnerability_report
from .assistant import draft_patch
from .review_gate import HumanReviewGate
from .apply_test import apply_patch_and_test


class VulnerabilityPatchPipeline:
    def __init__(self, decision_fn):
        # Constructing the pipeline without a valid decision function fails
        # immediately, at construction — not partway through processing a
        # report, after Intake and the Assistant have already done real work.
        self.gate = HumanReviewGate(decision_fn)

    def run(self, report):
        try:
            validated = validate_vulnerability_report(report)
        except ValueError as e:
            return PipelineResult(status="escalated", reason=str(e))

        patch = draft_patch(validated)

        decision = self.gate.review(patch, validated)
        if not decision.approved:
            return PipelineResult(status="rejected", reason=decision.reason, patch=patch)

        apply_patch_and_test(patch)
        return PipelineResult(status="applied", patch=patch)
