import json
import unittest

from intake import Intake, ExtractedFields, IntakeEscalation


class StubLLMClient:
    def __init__(self, response_text):
        self._response_text = response_text
        self.calls = []

    def call(self, instruction, input_text):
        self.calls.append((instruction, input_text))
        return self._response_text


class IntakeTests(unittest.TestCase):
    def test_high_confidence_classification_extracts_fields(self):
        response = json.dumps({
            "claim_type": "pet_illness_reimbursement", "diagnosis": "kennel cough",
            "amount": 120.0, "date": "2026-05-01", "confidence": 0.95,
        })
        intake = Intake(llm_client=StubLLMClient(response), confidence_threshold=0.75)

        result = intake.process("some claim text")

        self.assertIsInstance(result, ExtractedFields)
        self.assertEqual(result.diagnosis, "kennel cough")
        self.assertEqual(result.amount, 120.0)
        self.assertEqual(result.date, "2026-05-01")

    def test_unclassified_response_escalates(self):
        response = json.dumps({"claim_type": "unclassified", "confidence": 0.0})
        intake = Intake(llm_client=StubLLMClient(response), confidence_threshold=0.75)

        result = intake.process("gibberish")

        self.assertIsInstance(result, IntakeEscalation)
        self.assertEqual(result.reason, "unclassified")

    def test_low_confidence_escalates(self):
        response = json.dumps({
            "claim_type": "pet_illness_reimbursement", "diagnosis": "unknown",
            "amount": None, "date": None, "confidence": 0.2,
        })
        intake = Intake(llm_client=StubLLMClient(response), confidence_threshold=0.75)

        result = intake.process("vague claim")

        self.assertIsInstance(result, IntakeEscalation)
        self.assertEqual(result.reason, "low_confidence")

    def test_malformed_model_output_treated_as_unclassified_not_a_crash(self):
        # This is the exact class of bug that broke Verification during
        # CommBank's code review pass - a component receiving output it
        # can't parse and crashing instead of escalating. Tested explicitly.
        intake = Intake(llm_client=StubLLMClient("not valid json {{{"), confidence_threshold=0.75)

        result = intake.process("some claim text")

        self.assertIsInstance(result, IntakeEscalation)
        self.assertEqual(result.reason, "unclassified")

    def test_confidence_threshold_is_read_from_configuration_not_hardcoded(self):
        # Same response, two different thresholds -> two different outcomes.
        # Proves the /v2 Configuration-edge fix actually holds in code.
        response = json.dumps({
            "claim_type": "pet_illness_reimbursement", "diagnosis": "kennel cough",
            "amount": 120.0, "date": "2026-05-01", "confidence": 0.80,
        })

        lenient_intake = Intake(llm_client=StubLLMClient(response), confidence_threshold=0.5)
        strict_intake = Intake(llm_client=StubLLMClient(response), confidence_threshold=0.9)

        lenient_result = lenient_intake.process("some claim text")
        strict_result = strict_intake.process("some claim text")

        self.assertIsInstance(lenient_result, ExtractedFields)
        self.assertIsInstance(strict_result, IntakeEscalation)
        self.assertEqual(strict_result.reason, "low_confidence")


if __name__ == "__main__":
    unittest.main()
