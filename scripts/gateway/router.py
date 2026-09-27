"""The traffic cop: decide which tier serves a request, and say why.

A pure function of the request, the policy, and the tier config. No network,
no clock, no randomness, no model call -- the same request always routes the
same way, which is what lets routing accuracy be tested against hand-labeled
fixtures without spending anything.

This is the simple rules-based router that Sprint 7's baseline measures.
Deliberately absent: the break-even rule (start cheap only when
c_cheap < q_cheap * c_strong). That needs measured pass rates, and it is the
Sprint 8 "clever version" -- putting it here would leave the baseline nothing
to be compared against.

Every signal used is one a human can see in the request -- the task type and
the length of the input -- so a fixture's expected tier can be labeled by hand.
"""

from __future__ import annotations

from dataclasses import dataclass

from gateway.policy import Policy
from gateway.tiers import TierConfig

# Without a tokenizer, bound input tokens by characters: one token per
# character. Loose for English, but never an underestimate, and it does not
# depend on any model's tokenizer -- input counts differ by model (78 vs 17
# tokens for the same prompt; FINDINGS.md section 5).
#
# Margin for per-model prompt-format overhead: observed at 61 tokens
# (gpt-oss 78 vs qwen 17 on one prompt). 256 leaves headroom.
TEMPLATE_MARGIN_TOKENS = 256


class PinnedTask(ValueError):
    """Raised when a pinned task type reaches the router. Pins are never routed."""


class InputTooLarge(ValueError):
    """Raised when the input fits no tier's context window."""


@dataclass(frozen=True)
class RoutingDecision:
    task_type: str
    tier: str
    escalate_to: str | None
    max_tokens: int
    routing_reason: str
    explanation: str
    policy_version: str


def _fits(text: str, tier: str, policy: Policy, tiers: TierConfig) -> bool:
    # context_limit() raises ContextLimitUnset rather than guessing.
    needed = len(text) + TEMPLATE_MARGIN_TOKENS + policy.max_tokens(tier)
    return needed <= tiers.context_limit(tier)


def route(*, task_type: str, text: str, policy: Policy,
          tiers: TierConfig) -> RoutingDecision:
    # 1. Pinned task types never get a routing choice.
    if task_type in tiers.pins():
        raise PinnedTask(
            f"task type {task_type!r} is pinned in tiers.json and must never be "
            f"routed. Serving it needs its pinned model and adapter, not a tier."
        )

    # 2. No policy for this task type -> refuse. Raises UnknownTaskType.
    rule = policy.rule_for(task_type)
    order = policy.tier_order
    start = tier = rule["start_tier"]
    why = [f"{task_type} starts on {tier} by policy"]

    # 3. A long input is a harder task: start one tier up.
    limit = rule.get("promote_above_chars")
    if limit is not None and len(text) > limit:
        up = policy.next_tier_up(tier)
        if up is not None:
            why.append(f"input is {len(text):,} chars, over {limit:,}: promoted to {up}")
            tier = up

    # 4. The input must fit the tier's context window. Move up until it does.
    while not _fits(text, tier, policy, tiers):
        up = policy.next_tier_up(tier)
        if up is None:
            raise InputTooLarge(
                f"input of {len(text):,} chars fits no tier from {start} up; "
                f"the largest window is {tiers.context_limit(tier):,} tokens"
            )
        why.append(f"input does not fit {tier}'s context window: moved to {up}")
        tier = up

    # Escalation must go up from wherever the request actually starts.
    escalate_to = rule["escalate_to"]
    if order.index(escalate_to) <= order.index(tier):
        escalate_to = policy.next_tier_up(tier)

    return RoutingDecision(
        task_type=task_type,
        tier=tier,
        escalate_to=escalate_to,
        max_tokens=policy.max_tokens(tier),
        routing_reason="policy",
        explanation="; ".join(why) + ".",
        policy_version=policy.version,
    )