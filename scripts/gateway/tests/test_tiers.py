import pytest

from gateway.tiers import (
    ContextLimitUnset,
    TierConfig,
    TierConfigError,
    UnknownTierName,
)


def valid_config() -> dict:
    return {
        "version": "0.1.0",
        "tiers": {
            "cheap": {"provider": "groq", "model": "small", "status": "evidenced",
                      "evidence": "seen in the repo", "context_limit": 8192,
                      "capabilities": ["text"]},
            "strong": {"provider": "ollama", "model": "llama3.1",
                       "status": "provisional", "evidence": "no paid account found",
                       "replace_when": "a paid key is confirmed",
                       "context_limit": None, "capabilities": ["text"]},
        },
        "pins": {"_note": "ignored", "embedding": {"model": "UNSET"}},
    }


def test_the_shipped_config_loads():
    config = TierConfig.load()
    assert config.names == ["cheap", "mid", "strong"]
    assert config.providers() == {"groq", "ollama"}


def test_as_client_map_is_the_shape_the_client_wants():
    config = TierConfig(valid_config())
    assert config.as_client_map() == {
        "cheap": {"provider": "groq", "model": "small"},
        "strong": {"provider": "ollama", "model": "llama3.1"},
    }


def test_provisional_tiers_are_surfaced():
    assert TierConfig(valid_config()).provisional() == ["strong"]


def test_provisional_without_replace_when_is_rejected():
    data = valid_config()
    del data["tiers"]["strong"]["replace_when"]
    with pytest.raises(TierConfigError, match="replace_when"):
        TierConfig(data)


def test_unknown_status_is_rejected():
    data = valid_config()
    data["tiers"]["cheap"]["status"] = "probably_fine"
    with pytest.raises(TierConfigError, match="status"):
        TierConfig(data)


def test_missing_version_is_rejected():
    data = valid_config()
    del data["version"]
    with pytest.raises(TierConfigError, match="version"):
        TierConfig(data)


def test_unknown_tier_raises():
    with pytest.raises(UnknownTierName):
        TierConfig(valid_config()).spec("nonexistent")


def test_unset_context_limit_raises_rather_than_guessing():
    config = TierConfig(valid_config())
    assert config.context_limit("cheap") == 8192
    with pytest.raises(ContextLimitUnset):
        config.context_limit("strong")


def test_pins_skip_underscore_keys():
    assert list(TierConfig(valid_config()).pins()) == ["embedding"]