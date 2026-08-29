import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[2]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import pytest

from gateway.prices import PriceTable

# Test scaffolding chosen so the arithmetic is checkable by hand.
# These are NOT real provider prices -- never copy them into prices.json.
FIXTURE_PRICES_V1 = {
    "version": "test-v1", "currency": "USD", "unit": "per_1k_tokens",
    "models": {
        "groq:small":       {"input_per_1k": 0.10, "output_per_1k": 0.20},
        "groq:large":       {"input_per_1k": 1.00, "output_per_1k": 2.00},
        "anthropic:strong": {"input_per_1k": 3.00, "output_per_1k": 6.00},
    },
}

FIXTURE_PRICES_V2 = {
    "version": "test-v2", "currency": "USD", "unit": "per_1k_tokens",
    "models": {  # same models, doubled -- proves history is not re-priced
        "groq:small":       {"input_per_1k": 0.20, "output_per_1k": 0.40},
        "groq:large":       {"input_per_1k": 2.00, "output_per_1k": 4.00},
        "anthropic:strong": {"input_per_1k": 6.00, "output_per_1k": 12.00},
    },
}


@pytest.fixture
def prices_v1() -> PriceTable:
    return PriceTable(FIXTURE_PRICES_V1)


@pytest.fixture
def prices_v2() -> PriceTable:
    return PriceTable(FIXTURE_PRICES_V2)


@pytest.fixture
def log_path(tmp_path):
    return tmp_path / "logs" / "gateway-test.jsonl"