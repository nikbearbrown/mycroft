import pytest

from gateway.prices import PriceTable, PriceTableError, UnknownModelPrice


def test_cost_is_computed_from_tokens(prices_v1):
    # 1000 in * 0.10/1k + 1000 out * 0.20/1k = 0.30
    assert prices_v1.cost_usd("groq", "small", 1000, 1000) == pytest.approx(0.30)
    # 1000 in * 3.00/1k + 1000 out * 6.00/1k = 9.00
    assert prices_v1.cost_usd("anthropic", "strong", 1000, 1000) == pytest.approx(9.00)


def test_unknown_model_raises_instead_of_costing_zero(prices_v1):
    with pytest.raises(UnknownModelPrice):
        prices_v1.cost_usd("mystery", "unpriced", 1000, 1000)


def test_missing_version_is_rejected():
    with pytest.raises(PriceTableError, match="version"):
        PriceTable({"models": {}})


def test_negative_tokens_are_rejected(prices_v1):
    with pytest.raises(PriceTableError):
        prices_v1.cost_usd("groq", "small", -1, 0)


# -- a model that cannot be priced, as opposed to one nobody has recorded ---

UNPRICEABLE = {
    "version": "test-unpriced", "currency": "USD", "unit": "per_1k_tokens",
    "models": {
        "groq:enterprise-only": {
            "unpriced": "sold on an Enterprise tier with 'Contact Sales' in place "
                        "of a published rate",
            "source": "https://example.invalid/models", "read_on": "2026-11-17",
        },
        "groq:small": {"input_per_1k": 0.10, "output_per_1k": 0.20},
    },
}


def test_a_model_recorded_as_unpriced_refuses_and_says_why():
    """The refusal must not send someone after a rate that does not exist."""
    table = PriceTable(UNPRICEABLE)

    with pytest.raises(UnknownModelPrice, match="Contact Sales"):
        table.rates("groq", "enterprise-only")


def test_an_unpriced_model_still_cannot_be_costed():
    table = PriceTable(UNPRICEABLE)
    with pytest.raises(UnknownModelPrice):
        table.cost_usd("groq", "enterprise-only", 100, 100)


def test_the_note_is_readable_without_asking_for_a_price():
    """A caller deciding what to do about it needs the reason, not an exception."""
    entry = PriceTable(UNPRICEABLE).entry("groq", "enterprise-only")

    assert "Contact Sales" in entry["unpriced"]
    assert entry["read_on"] == "2026-11-17"
    assert PriceTable(UNPRICEABLE).entry("groq", "nothing-here") is None


def test_an_entry_with_neither_rates_nor_a_reason_is_rejected():
    """A half-finished price entry is how a rate later gets read as zero."""
    with pytest.raises(PriceTableError, match="unpriced"):
        PriceTable({"version": "t", "unit": "per_1k_tokens",
                    "models": {"groq:half-done": {"source": "somewhere"}}})


# -- the shipped table ------------------------------------------------------

def test_the_shipped_table_prices_every_configured_tier():
    """Sprint 2 shipped this empty on purpose; since 2026-09-02 it has rates."""
    table = PriceTable.load()

    for model in ("openai/gpt-oss-20b", "openai/gpt-oss-120b", "qwen/qwen3.8-27b"):
        input_rate, output_rate = table.rates("groq", model)
        assert input_rate > 0 and output_rate > 0


def test_the_shipped_table_refuses_the_model_mycroft_recipes_name():
    """contradiction-detection-agent names llama-3.3-70b-versatile, which is
    Enterprise-only. The gateway must refuse it, and explain itself."""
    table = PriceTable.load()

    with pytest.raises(UnknownModelPrice, match="Enterprise"):
        table.rates("groq", "llama-3.3-70b-versatile")