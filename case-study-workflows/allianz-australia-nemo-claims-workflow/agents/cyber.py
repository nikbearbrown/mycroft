"""
agents/cyber.py

Cyber — a cross-cutting guardrail layer, NOT a numbered pipeline step and
NOT an LLM-calling agent. Every other agent in this pipeline (Planner,
Coverage, Weather, Fraud, Payout, Audit) makes an LLM call and has a system
prompt. Cyber does not — its job is to intercept and monitor every other
agent's call, enforcing that each agent stays within its declared
data-access scope, and halting execution if one doesn't.

This is an illustrative implementation, not a disclosure of any real
insurer's actual system. See README.md for why Cyber is modeled this way
rather than as a sixth agent in the sequence.

[DEV] EXTENSION POINT: this implementation checks access scope only
(read-only allowlist per agent). A production version would likely add:
rate limiting, PII redaction before logging, and anomaly detection across
calls (e.g. the same claim_id being reprocessed unusually often). None of
that is built here — this wrapper demonstrates the pattern, not a complete
security layer.
"""

from dataclasses import dataclass
from functools import wraps
from typing import Callable, TypeVar

T = TypeVar("T")

# [DEV] Declared read-access scope per agent, used to check that an agent
# call only touches the data sources it's supposed to. This is a simple
# allowlist for illustration — see the extension-point note above for what
# a production guardrail layer would add on top of this.
AGENT_ACCESS_SCOPE = {
    "planner": {"claim_intake"},
    "coverage": {"policy_database"},
    "weather": {"meteorological_data"},
    "fraud": {"accumulated_context", "claim_history"},
    "payout": {"accumulated_context"},
    "audit": {"accumulated_context"},
}


class CyberPolicyViolation(Exception):
    """Raised when an agent call touches a data source outside its
    declared scope. This halts the workflow immediately."""
    def __init__(self, agent_name: str, requested_source: str):
        self.agent_name = agent_name
        self.requested_source = requested_source
        allowed = AGENT_ACCESS_SCOPE.get(agent_name, set())
        super().__init__(
            f"Cyber halted execution: '{agent_name}' requested access to "
            f"'{requested_source}', which is outside its declared scope {allowed}."
        )


@dataclass
class CyberLogEntry:
    agent_name: str
    data_sources_accessed: set
    violation: bool


class CyberWrapper:
    """
    Wraps a single agent call. Used by the orchestrator around every agent
    invocation — see workflow/orchestrator.py for how this is applied
    consistently across all six agents rather than each agent guarding
    itself.
    """

    def __init__(self):
        self.log: list[CyberLogEntry] = []

    def guard(self, agent_name: str, data_sources_accessed: set, call: Callable[[], T]) -> T:
        """
        Checks data_sources_accessed against AGENT_ACCESS_SCOPE before
        running `call`. Raises CyberPolicyViolation and does NOT run
        `call` at all if any accessed source is outside the agent's
        declared scope — this is a pre-check, not a post-hoc audit.
        """
        allowed = AGENT_ACCESS_SCOPE.get(agent_name, set())
        out_of_scope = data_sources_accessed - allowed

        if out_of_scope:
            self.log.append(CyberLogEntry(agent_name, data_sources_accessed, violation=True))
            raise CyberPolicyViolation(agent_name, next(iter(out_of_scope)))

        self.log.append(CyberLogEntry(agent_name, data_sources_accessed, violation=False))
        return call()
