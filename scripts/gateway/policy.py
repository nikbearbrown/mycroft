"""Load and validate the routing policy: the locked task-type vocabulary and,
for each type, its starting tier, escalation target, and validator.

Refusals, following the price-table and tier-config precedent:
- an unknown task type raises; it is never routed to a default tier
- a label or verdict task without its label set is rejected
- every tier the policy names must exist in tiers.json
- escalation must go UP the tier order; sideways or down is rejected
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from gateway.tiers import TierConfig

DEFAULT_POLICY = Path(__file__).with_name("policy.json")

OUTPUT_KINDS = frozenset({"label", "json", "verdict", "prose"})
LABELLED_OUTPUTS = frozenset({"label", "verdict"})
VALIDATORS = frozenset({
    "label_in_set", "required_keys", "verdict_with_quote",
    "numbers_grounded", "cites_context",
})
QUALITY_CHECKS = frozenset({"deterministic", "offline_judge"})
_REQUIRED = ("description", "output", "validator", "quality_check",
             "start_tier", "escalate_to")


class PolicyError(ValueError):
    """Raised when the policy file is malformed or inconsistent with tiers."""


class UnknownTaskType(KeyError):
    """Raised when a request names a task type the policy does not define."""


def _positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


class Policy:
    def __init__(self, data: dict[str, Any], tiers: TierConfig) -> None:
        version = data.get("version")
        if not isinstance(version, str) or not version.strip():
            raise PolicyError("policy has no non-empty 'version'")

        order = data.get("tier_order")
        if not isinstance(order, list) or len(order) != len(set(order)):
            raise PolicyError("'tier_order' must be a list of distinct tier names")
        if set(order) != set(tiers.names):
            raise PolicyError(
                f"'tier_order' {order} must list every configured tier exactly "
                f"once; tiers.json has {tiers.names}"
            )

        budgets = {k: v for k, v in (data.get("max_tokens_by_tier") or {}).items()
                   if not k.startswith("_")}
        for tier in order:
            if not _positive_int(budgets.get(tier)):
                raise PolicyError(f"max_tokens_by_tier needs a positive int for {tier!r}")

        task_types = data.get("task_types")
        if not isinstance(task_types, dict) or not task_types:
            raise PolicyError("'task_types' must be a non-empty object")

        for name, rule in task_types.items():
            for key in _REQUIRED:
                if not isinstance(rule.get(key), str) or not rule[key].strip():
                    raise PolicyError(f"task type {name!r} needs a non-empty {key!r}")

            if rule["output"] not in OUTPUT_KINDS:
                raise PolicyError(f"task type {name!r} output {rule['output']!r} "
                                  f"is not one of {sorted(OUTPUT_KINDS)}")
            if rule["validator"] not in VALIDATORS:
                raise PolicyError(f"task type {name!r} validator {rule['validator']!r} "
                                  f"is not one of {sorted(VALIDATORS)}")
            if rule["quality_check"] not in QUALITY_CHECKS:
                raise PolicyError(f"task type {name!r} quality_check "
                                  f"{rule['quality_check']!r} is invalid")

            if rule["output"] in LABELLED_OUTPUTS:
                labels = rule.get("labels")
                if (not isinstance(labels, list) or not labels
                        or len(labels) != len(set(labels))
                        or not all(isinstance(x, str) and x.strip() for x in labels)):
                    raise PolicyError(f"task type {name!r} produces a {rule['output']} "
                                      f"and needs a non-empty list of distinct labels")

            start, up = rule["start_tier"], rule["escalate_to"]
            for tier in (start, up):
                if tier not in order:
                    raise PolicyError(f"task type {name!r} names tier {tier!r}, "
                                      f"which is not in tier_order {order}")
            if order.index(up) <= order.index(start):
                raise PolicyError(f"task type {name!r} escalates from {start!r} to "
                                  f"{up!r}; escalation must go up the tier order")

            promote = rule.get("promote_above_chars")
            if promote is not None and not _positive_int(promote):
                raise PolicyError(f"task type {name!r} promote_above_chars must be "
                                  f"a positive int or absent")

            evidence = rule.get("evidence")
            if not isinstance(evidence, list) or not evidence:
                raise PolicyError(f"task type {name!r} needs at least one evidence path")

        self.version = version
        self._order = list(order)
        self._budgets = budgets
        self._task_types = task_types

    @classmethod
    def load(cls, tiers: TierConfig, path: str | Path = DEFAULT_POLICY) -> "Policy":
        return cls(json.loads(Path(path).read_text(encoding="utf-8")), tiers)

    @property
    def task_types(self) -> list[str]:
        return sorted(self._task_types)

    @property
    def tier_order(self) -> list[str]:
        return list(self._order)

    def rule_for(self, task_type: str) -> dict[str, Any]:
        """Refuse rather than guess: an unknown type is a missing human decision."""
        if task_type not in self._task_types:
            raise UnknownTaskType(
                f"task type {task_type!r} has no policy; known types: "
                f"{self.task_types}. Add a rule to policy.json and bump its version."
            )
        return dict(self._task_types[task_type])

    def max_tokens(self, tier: str) -> int:
        return self._budgets[tier]

    def next_tier_up(self, tier: str) -> str | None:
        i = self._order.index(tier)
        return self._order[i + 1] if i + 1 < len(self._order) else None