import unittest
from unittest.mock import Mock

from orchestrator import Orchestrator, ClaimResult
from intake import IntakeEscalation, ExtractedFields
from verification import VerificationEscalation, VerifiedClaim
from authorization_gate import GateOutcome
from exceptions import MissingPolicyError


def make_components(intake_result, verification_result=None, gate_outcome=None):
    intake = Mock()
    intake.process.return_value = intake_result

    verification = Mock()
    verification.process.return_value = verification_result

    gate = Mock()
    gate.decide.return_value = gate_outcome

    return intake, verification, gate


class OrchestratorConstructionTests(unittest.TestCase):
    def test_construction_with_valid_policy_fn_succeeds(self):
        intake, verification, gate = make_components(None)
        Orchestrator(intake, verification, gate, policy_fn=lambda claim: True)  # no error

    def test_construction_with_none_policy_fn_raises_missing_policy_error(self):
        intake, verification, gate = make_components(None)
        with self.assertRaises(MissingPolicyError):
            Orchestrator(intake, verification, gate, policy_fn=None)

    def test_construction_with_non_callable_policy_fn_raises_missing_policy_error(self):
        intake, verification, gate = make_components(None)
        with self.assertRaises(MissingPolicyError):
            Orchestrator(intake, verification, gate, policy_fn="not a function")


class OrchestratorPerClaimTests(unittest.TestCase):
    def test_full_happy_path_settles(self):
        extracted = ExtractedFields("pet_illness_reimbursement", "kennel cough", 120.0, "2026-05-01", 0.95)
        verified = VerifiedClaim("kennel cough", 120.0, "2026-05-01")
        intake, verification, gate = make_components(
            intake_result=extracted,
            verification_result=verified,
            gate_outcome=GateOutcome(status="SETTLED"),
        )
        orchestrator = Orchestrator(intake, verification, gate, policy_fn=lambda claim: True)

        result = orchestrator.process_claim("some claim", "cust", "policy")

        self.assertEqual(result, ClaimResult(status="SETTLED", reason=None))
        intake.process.assert_called_once()
        verification.process.assert_called_once()
        gate.decide.assert_called_once()

    def test_intake_escalation_stops_pipeline_before_verification_and_gate(self):
        intake, verification, gate = make_components(
            intake_result=IntakeEscalation(reason="unclassified"),
        )
        orchestrator = Orchestrator(intake, verification, gate, policy_fn=lambda claim: True)

        result = orchestrator.process_claim("gibberish", "cust", "policy")

        self.assertEqual(result, ClaimResult(status="ESCALATED", reason="unclassified"))
        verification.process.assert_not_called()
        gate.decide.assert_not_called()

    def test_intake_low_confidence_stops_pipeline(self):
        intake, verification, gate = make_components(
            intake_result=IntakeEscalation(reason="low_confidence"),
        )
        orchestrator = Orchestrator(intake, verification, gate, policy_fn=lambda claim: True)

        result = orchestrator.process_claim("vague", "cust", "policy")

        self.assertEqual(result, ClaimResult(status="ESCALATED", reason="low_confidence"))
        verification.process.assert_not_called()
        gate.decide.assert_not_called()

    def test_verification_escalation_stops_pipeline_before_gate(self):
        extracted = ExtractedFields("pet_illness_reimbursement", "kennel cough", 120.0, "2026-05-01", 0.95)
        intake, verification, gate = make_components(
            intake_result=extracted,
            verification_result=VerificationEscalation(reason="no_record_found"),
        )
        orchestrator = Orchestrator(intake, verification, gate, policy_fn=lambda claim: True)

        result = orchestrator.process_claim("some claim", "cust", "policy")

        self.assertEqual(result, ClaimResult(status="ESCALATED", reason="no_record_found"))
        gate.decide.assert_not_called()

    def test_each_verification_escalation_reason_stops_pipeline_before_gate(self):
        for reason in ["incomplete_extraction", "no_record_found", "fraud_flag", "mismatch"]:
            with self.subTest(reason=reason):
                extracted = ExtractedFields("pet_illness_reimbursement", "kennel cough", 120.0, "2026-05-01", 0.95)
                intake, verification, gate = make_components(
                    intake_result=extracted,
                    verification_result=VerificationEscalation(reason=reason),
                )
                orchestrator = Orchestrator(intake, verification, gate, policy_fn=lambda claim: True)

                result = orchestrator.process_claim("some claim", "cust", "policy")

                self.assertEqual(result, ClaimResult(status="ESCALATED", reason=reason))
                gate.decide.assert_not_called()

    def test_gate_not_authorized_outcome_passes_through(self):
        extracted = ExtractedFields("pet_illness_reimbursement", "kennel cough", 700.0, "2026-05-01", 0.95)
        verified = VerifiedClaim("kennel cough", 700.0, "2026-05-01")
        intake, verification, gate = make_components(
            intake_result=extracted,
            verification_result=verified,
            gate_outcome=GateOutcome(status="ESCALATED", reason="not_authorized"),
        )
        orchestrator = Orchestrator(intake, verification, gate, policy_fn=lambda claim: False)

        result = orchestrator.process_claim("expensive claim", "cust", "policy")

        self.assertEqual(result, ClaimResult(status="ESCALATED", reason="not_authorized"))


if __name__ == "__main__":
    unittest.main()
