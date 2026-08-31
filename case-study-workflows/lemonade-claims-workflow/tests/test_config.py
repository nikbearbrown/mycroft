import unittest
from unittest.mock import patch

import config as config_module
from exceptions import UnknownProviderError, MissingAPIKeyError


class ConfigurationTests(unittest.TestCase):
    def test_default_configuration_resolves_to_fake_no_key_required(self):
        with patch.dict("os.environ", {}, clear=True):
            cfg = config_module.Configuration()

            self.assertEqual(cfg.llm_provider, "fake")
            self.assertIsNone(cfg.llm_api_key)

    def test_real_provider_without_key_raises_missing_api_key_error(self):
        with patch.dict("os.environ", {"LLM_PROVIDER": "claude"}, clear=True):
            with self.assertRaises(MissingAPIKeyError):
                config_module.Configuration()

    def test_unrecognized_provider_raises_unknown_provider_error(self):
        with patch.dict("os.environ", {"LLM_PROVIDER": "not_a_real_provider"}, clear=True):
            with self.assertRaises(UnknownProviderError):
                config_module.Configuration()

    def test_confidence_threshold_and_matching_tolerance_independently_overridable(self):
        env = {"CONFIDENCE_THRESHOLD": "0.6", "MATCHING_TOLERANCE": "0.10"}
        with patch.dict("os.environ", env, clear=True):
            cfg = config_module.Configuration()

            self.assertEqual(cfg.confidence_threshold, 0.6)
            self.assertEqual(cfg.matching_tolerance, 0.10)
            self.assertEqual(cfg.llm_provider, "fake")  # unaffected by tunable overrides


if __name__ == "__main__":
    unittest.main()
