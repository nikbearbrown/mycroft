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


def test_shipped_price_table_is_empty_by_default():
    """prices.json ships unfilled on purpose: no invented rates."""
    table = PriceTable.load()
    with pytest.raises(UnknownModelPrice):
        table.rates("groq", "small")