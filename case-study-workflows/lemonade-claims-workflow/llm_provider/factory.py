"""
WHAT THIS FILE DOES: Reads an already-validated provider name from
Configuration and returns the corresponding adapter instance. Does not
re-validate the provider name - that is Configuration's job, per /review
Finding 2. This removes the duplicated validation that previously existed
between Configuration and this factory.
"""
from llm_provider.fake_adapter import FakeAdapter
from llm_provider.claude_adapter import ClaudeAdapter
from llm_provider.gpt_adapter import GPTAdapter
from llm_provider.gemini_adapter import GeminiAdapter


def build_llm_client(config):
    """
    config is an already-constructed, already-validated Configuration
    instance - by the time it reaches here, config.llm_provider is guaranteed
    to be one of "fake", "claude", "gpt", "gemini", and config.llm_api_key is
    guaranteed present for any real provider.
    """
    if config.llm_provider == "fake":
        return FakeAdapter()
    if config.llm_provider == "claude":
        return ClaudeAdapter(api_key=config.llm_api_key)
    if config.llm_provider == "gpt":
        return GPTAdapter(api_key=config.llm_api_key)
    if config.llm_provider == "gemini":
        return GeminiAdapter(api_key=config.llm_api_key)

    # Unreachable if Configuration validated correctly - factory.py trusts
    # Configuration and does not re-check the provider name itself.
    raise AssertionError(
        f"Unexpected provider {config.llm_provider!r} reached factory.py "
        f"without validation. This indicates Configuration's own validation "
        f"was bypassed."
    )
