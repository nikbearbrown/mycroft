"""Content hashing used to make the oracle tamper-evident.

When an oracle is frozen we hash the exact content the human committed to
(the rule text plus every test case). Any later edit to that content would
change the hash, so a stored `oracle_hash` is proof of what was frozen.
"""
import hashlib
import json


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compute_oracle_hash(rule_text, test_cases) -> str:
    """Deterministic hash over the frozen oracle content.

    `test_cases` is an iterable of objects exposing applicant_id, applicant_data,
    expected_outcome and author_rationale. Cases are sorted by applicant_id and
    the JSON is key-sorted so the hash is stable regardless of insertion order.
    """
    payload = {
        "rule_text": rule_text,
        "test_cases": sorted(
            [
                {
                    "applicant_id": tc.applicant_id,
                    "applicant_data": tc.applicant_data,
                    "expected_outcome": tc.expected_outcome,
                    "author_rationale": tc.author_rationale,
                }
                for tc in test_cases
            ],
            key=lambda x: x["applicant_id"],
        ),
    }
    return sha256_text(json.dumps(payload, sort_keys=True, separators=(",", ":")))


def compute_binding_proof(code_hash, validation_results, simulation_results) -> str:
    """Bind the generated code to the exact results it produced.

    A single hash over (code + both checkers' results). The human approves this
    bundle, so an approval can't later be re-attached to different code or results.
    """
    payload = {
        "code_hash": code_hash,
        "validation": validation_results,
        "simulation": simulation_results,
    }
    return sha256_text(json.dumps(payload, sort_keys=True, separators=(",", ":")))
