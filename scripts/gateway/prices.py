"""Compute per-attempt cost from a versioned, human-maintained price table."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_PRICE_TABLE = Path(__file__).with_name("prices.json")


class UnknownModelPrice(KeyError):
    """Raised when a (provider, model) pair has no entry in the price table."""


class PriceTableError(ValueError):
    """Raised when the price table itself is malformed."""


class PriceTable:
    def __init__(self, data: dict[str, Any]) -> None:
        version = data.get("version")
        if not isinstance(version, str) or not version.strip():
            raise PriceTableError("price table has no non-empty 'version'")
        models = data.get("models")
        if not isinstance(models, dict):
            raise PriceTableError("price table 'models' must be an object")

        self.version = version
        self.unit = data.get("unit", "per_1k_tokens")
        if self.unit != "per_1k_tokens":
            raise PriceTableError(f"unsupported price unit {self.unit!r}")
        self._models = models

    @classmethod
    def load(cls, path: str | Path = DEFAULT_PRICE_TABLE) -> "PriceTable":
        return cls(json.loads(Path(path).read_text(encoding="utf-8")))

    @staticmethod
    def _key(provider: str, model: str) -> str:
        return f"{provider}:{model}"

    def rates(self, provider: str, model: str) -> tuple[float, float]:
        key = self._key(provider, model)
        entry = self._models.get(key)
        if entry is None:
            raise UnknownModelPrice(
                f"no price for {key!r} in price table version {self.version!r}. "
                f"Add it to prices.json with a source URL and the date read, then "
                f"bump the table version. Cost is never defaulted to zero."
            )
        try:
            return float(entry["input_per_1k"]), float(entry["output_per_1k"])
        except (KeyError, TypeError, ValueError) as exc:
            raise PriceTableError(
                f"price entry {key!r} needs numeric 'input_per_1k' and 'output_per_1k'"
            ) from exc

    def cost_usd(self, provider: str, model: str, tokens_in: int, tokens_out: int) -> float:
        if tokens_in < 0 or tokens_out < 0:
            raise PriceTableError("token counts must be non-negative")
        input_rate, output_rate = self.rates(provider, model)
        return (tokens_in / 1000.0) * input_rate + (tokens_out / 1000.0) * output_rate