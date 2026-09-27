import json
import unittest
from unittest.mock import patch, Mock

from llm_provider.fake_adapter import FakeAdapter
from llm_provider.claude_adapter import ClaudeAdapter
from llm_provider.gpt_adapter import GPTAdapter
from llm_provider.gemini_adapter import GeminiAdapter
from llm_provider.factory import build_llm_client
from fixtures import SOFIA_VALID_CLAIM_TEXT


class FakeConfig:
    def __init__(self, provider, api_key=None):
        self.llm_provider = provider
        self.llm_api_key = api_key


class FakeAdapterTests(unittest.TestCase):
    def test_returns_correct_canned_response_for_known_scenario(self):
        adapter = FakeAdapter()

        response = adapter.call("instruction", SOFIA_VALID_CLAIM_TEXT)
        parsed = json.loads(response)

        self.assertEqual(parsed["diagnosis"], "kennel cough")
        self.assertEqual(parsed["amount"], 120.0)

    def test_returns_generic_low_confidence_for_unrecognized_input(self):
        adapter = FakeAdapter()

        response = adapter.call("instruction", "some text not in the fixture table")
        parsed = json.loads(response)

        self.assertEqual(parsed["claim_type"], "unclassified")
        self.assertEqual(parsed["confidence"], 0.0)


class RealAdapterTests(unittest.TestCase):
    # No test in this class calls a real external API - all three mock the
    # HTTP layer, per the /v3 card's testing contract.

    def test_claude_adapter_builds_request_and_normalizes_response(self):
        adapter = ClaudeAdapter(api_key="fake-key")
        mock_response = Mock()
        mock_response.json.return_value = {"content": [{"type": "text", "text": "hello from claude"}]}
        mock_response.raise_for_status.return_value = None

        with patch("requests.post", return_value=mock_response) as mock_post:
            result = adapter.call("instruction", "input text")

        self.assertEqual(result, "hello from claude")
        called_headers = mock_post.call_args.kwargs["headers"]
        self.assertEqual(called_headers["x-api-key"], "fake-key")

    def test_gpt_adapter_builds_request_and_normalizes_response(self):
        adapter = GPTAdapter(api_key="fake-key")
        mock_response = Mock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "hello from gpt"}}]}
        mock_response.raise_for_status.return_value = None

        with patch("requests.post", return_value=mock_response) as mock_post:
            result = adapter.call("instruction", "input text")

        self.assertEqual(result, "hello from gpt")
        called_headers = mock_post.call_args.kwargs["headers"]
        self.assertEqual(called_headers["Authorization"], "Bearer fake-key")

    def test_gemini_adapter_builds_request_and_normalizes_response(self):
        adapter = GeminiAdapter(api_key="fake-key")
        mock_response = Mock()
        mock_response.json.return_value = {
            "candidates": [{"content": {"parts": [{"text": "hello from gemini"}]}}]
        }
        mock_response.raise_for_status.return_value = None

        with patch("requests.post", return_value=mock_response) as mock_post:
            result = adapter.call("instruction", "input text")

        self.assertEqual(result, "hello from gemini")
        self.assertIn("fake-key", mock_post.call_args.args[0])


class FactoryTests(unittest.TestCase):
    def test_returns_fake_adapter_for_fake_provider(self):
        self.assertIsInstance(build_llm_client(FakeConfig("fake")), FakeAdapter)

    def test_returns_claude_adapter_for_claude_provider(self):
        self.assertIsInstance(build_llm_client(FakeConfig("claude", api_key="k")), ClaudeAdapter)

    def test_returns_gpt_adapter_for_gpt_provider(self):
        self.assertIsInstance(build_llm_client(FakeConfig("gpt", api_key="k")), GPTAdapter)

    def test_returns_gemini_adapter_for_gemini_provider(self):
        self.assertIsInstance(build_llm_client(FakeConfig("gemini", api_key="k")), GeminiAdapter)

    # NOTE (per this component's /v3 card): factory.py does not test for an
    # unrecognized provider name. Per /review Finding 2, Configuration is
    # the sole owner of that validation - see tests/test_config.py.


if __name__ == "__main__":
    unittest.main()
