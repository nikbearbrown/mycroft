"""Load and validate the tier configuration.

Tiers are named (cheap / mid / strong); policy refers to those names, never
to concrete models. Swapping a model is then one edit here plus a version
bump, rather than a hunt through every routing rule.

Two refusals are deliberate, and both follow the price-table precedent:
an unknown tier raises rather than falling back, and an unset context limit
raises when asked for rather than being treated as zero or infinity.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_TIER_CONFIG = Path(__file__).with_name("tiers.json")

VALID_STATUSES = frozenset({"evidenced", "provisional"})
_REQUIRED_TIER_FIELDS = ("provider", "model", "status", "evidence")


class TierConfigError(ValueError):
    """Raised when the tier config is malformed."""


class UnknownTierName(KeyError):
    """Raised when a tier is requested that is not configured."""


class ContextLimitUnset(ValueError):
    """Raised when a tier's context limit is needed but has never been recorded."""


class TierConfig:
    def __init__(self, data: dict[str, Any]) -> None:
        version = data.get("version")
        if not isinstance(version, str) or not version.strip():
            raise TierConfigError("tier config has no non-empty 'version'")

        tiers = data.get("tiers")
        if not isinstance(tiers, dict) or not tiers:
            raise TierConfigError("tier config 'tiers' must be a non-empty object")

        for name, spec in tiers.items():
            if not isinstance(spec, dict):
                raise TierConfigError(f"tier {name!r} must be an object")

            for key in _REQUIRED_TIER_FIELDS:
                value = spec.get(key)
                if not isinstance(value, str) or not value.strip():
                    raise TierConfigError(
                        f"tier {name!r} needs a non-empty {key!r}"
                    )

            if spec["status"] not in VALID_STATUSES:
                raise TierConfigError(
                    f"tier {name!r} status {spec['status']!r} is not one of "
                    f"{sorted(VALID_STATUSES)}"
                )

            # A provisional choice must say what would replace it, so a
            # temporary decision cannot quietly harden into a permanent one.
            if spec["status"] == "provisional" and not spec.get("replace_when"):
                raise TierConfigError(
                    f"tier {name!r} is provisional and must record 'replace_when'"
                )

            limit = spec.get("context_limit")
            if limit is not None and (not isinstance(limit, int)
                                      or isinstance(limit, bool) or limit <= 0):
                raise TierConfigError(
                    f"tier {name!r} context_limit must be a positive int or null, "
                    f"got {limit!r}"
                )

            if not isinstance(spec.get("capabilities", []), list):
                raise TierConfigError(f"tier {name!r} capabilities must be a list")

        self.version = version
        self._tiers = tiers
        self._pins = {k: v for k, v in (data.get("pins") or {}).items()
                      if not k.startswith("_")}

    @classmethod
    def load(cls, path: str | Path = DEFAULT_TIER_CONFIG) -> "TierConfig":
        return cls(json.loads(Path(path).read_text(encoding="utf-8")))

    @property
    def names(self) -> list[str]:
        return sorted(self._tiers)

    def spec(self, name: str) -> dict[str, Any]:
        if name not in self._tiers:
            raise UnknownTierName(
                f"tier {name!r} is not configured; known tiers: {self.names}"
            )
        return dict(self._tiers[name])

    def providers(self) -> set[str]:
        """Every provider a tier names -- i.e. the adapters you must register."""
        return {spec["provider"] for spec in self._tiers.values()}

    def context_limit(self, name: str) -> int:
        """Raise rather than guess. An unset limit is not zero and not infinity."""
        limit = self.spec(name).get("context_limit")
        if limit is None:
            raise ContextLimitUnset(
                f"tier {name!r} has no recorded context_limit. Read it from the "
                f"provider's docs, record the source URL and date in tiers.json, "
                f"and bump the config version."
            )
        return limit

    def as_client_map(self) -> dict[str, dict[str, str]]:
        """The shape GatewayClient expects: tier -> {provider, model}."""
        return {
            name: {"provider": spec["provider"], "model": spec["model"]}
            for name, spec in self._tiers.items()
        }

    def pins(self) -> dict[str, Any]:
        return dict(self._pins)

    def provisional(self) -> list[str]:
        """Tiers not backed by evidence -- surfaced in reports, not hidden."""
        return sorted(n for n, s in self._tiers.items()
                      if s["status"] == "provisional")