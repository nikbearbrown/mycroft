"""The JSON signal, frozen at `schema_version` 1.0.

`plan.md`: "The JSON signal and the note are deliberately distinct artifacts.
The signal is a contract (`schema_version`) the coordination layer parses and
that must change slowly; the note is human presentation that can be restyled
freely."

So this module is the contract, and the schema lives here as data rather than
as prose. Two things follow from "a contract that must change slowly":

1. **The schema is explicit and closed.** `additionalProperties: false` on
   every object. A field that appears without a version bump is a silent
   change to something another system parses, which is the failure a
   `schema_version` exists to prevent.
2. **Commentary is quarantined inside the contract.** The LLM note is a
   string in a `commentary` object that carries `is_model_output: true` and
   the model's name. Everything else in the signal is deterministic and
   reproducible from stored rows. A consumer that wants only verified figures
   can drop one key and keep the rest.

--------------------------------------------------------------------------
What the signal deliberately does not contain
--------------------------------------------------------------------------
No company valuation, no implied market cap, no return. `plan.md`'s "Not
supported" section is structural: N-PORT gives a fund's share count, never the
company's shares outstanding. A field for it would invite a consumer to fill
it from somewhere else and inherit that source's error. There is no such
field, `validate` rejects one, and a test asserts both.
"""

from __future__ import annotations

import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

SCHEMA_VERSION = "1.0"

# Fields no version of this contract may carry. Checked by name on the way
# out, because the cost of publishing one is a consumer building on a number
# this project cannot stand behind.
FORBIDDEN_FIELDS = (
    "valuation", "company_valuation", "implied_valuation", "market_cap",
    "post_money", "pre_money", "shares_outstanding", "return", "irr", "moic",
)

SCHEMA: dict = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://mycroft.local/private-ai-valuations/signal-1.0.json",
    "title": "Private AI valuation signal",
    "type": "object",
    "additionalProperties": False,
    "required": ["schema_version", "generated_at", "period", "coverage",
                 "companies", "guards", "provenance"],
    "properties": {
        "schema_version": {"const": SCHEMA_VERSION},
        "generated_at": {"type": "string", "format": "date-time"},
        "period": {
            "type": "object", "additionalProperties": False,
            "required": ["latest_period_end", "first_period_end", "periods"],
            "properties": {
                "latest_period_end": {"type": "string", "format": "date"},
                "first_period_end": {"type": "string", "format": "date"},
                "periods": {"type": "integer", "minimum": 0},
            },
        },
        "coverage": {
            "type": "object", "additionalProperties": False,
            "required": ["companies", "managers", "marks", "marks_published"],
            "properties": {
                "companies": {"type": "integer", "minimum": 0},
                "managers": {"type": "integer", "minimum": 0},
                "marks": {"type": "integer", "minimum": 0},
                "marks_published": {"type": "integer", "minimum": 0},
                "opaque_spv_positions": {"type": "integer", "minimum": 0},
            },
        },
        "companies": {
            "type": "array",
            "items": {
                "type": "object", "additionalProperties": False,
                "required": ["company", "status", "marks", "managers",
                             "latest_period_end"],
                "properties": {
                    "company": {"type": "string", "minLength": 1},
                    "status": {"enum": ["full", "thin", "watchlist"]},
                    "marks": {"type": "integer", "minimum": 0},
                    "managers": {"type": "integer", "minimum": 0},
                    "latest_period_end": {
                        "type": ["string", "null"], "format": "date"},
                    "latest_price_min": {"type": ["number", "null"]},
                    "latest_price_max": {"type": ["number", "null"]},
                    "remark_rate": {
                        "type": ["number", "null"], "minimum": 0, "maximum": 1},
                    "dispersion": {
                        "type": ["object", "null"], "additionalProperties": False,
                        "required": ["groups", "median_spread"],
                        "properties": {
                            "groups": {"type": "integer", "minimum": 0},
                            "median_spread": {"type": ["number", "null"]},
                            "max_spread": {"type": ["number", "null"]},
                            "suppressed_reason": {"type": ["string", "null"]},
                        },
                    },
                    "propagation": {
                        "type": ["object", "null"], "additionalProperties": False,
                        "required": ["events", "median_days_to_half"],
                        "properties": {
                            "events": {"type": "integer", "minimum": 0},
                            "median_days_to_half": {"type": ["integer", "null"]},
                            "max_days_to_half": {"type": ["integer", "null"]},
                            "suppressed_reason": {"type": ["string", "null"]},
                        },
                    },
                },
            },
        },
        "guards": {
            "type": "object", "additionalProperties": False,
            "required": ["change_blocked", "unadjudicated_splits",
                         "incomplete_runs", "unresolved_reviews"],
            "properties": {
                "change_blocked": {"type": "integer", "minimum": 0},
                "unadjudicated_splits": {"type": "integer", "minimum": 0},
                "confirmed_splits": {"type": "integer", "minimum": 0},
                "incomplete_runs": {"type": "integer", "minimum": 0},
                "unresolved_reviews": {"type": "integer", "minimum": 0},
                "unpriced_marks": {"type": "integer", "minimum": 0},
            },
        },
        "commentary": {
            "type": ["object", "null"], "additionalProperties": False,
            "required": ["text", "is_model_output", "model", "generated_at"],
            "properties": {
                "text": {"type": "string"},
                "is_model_output": {"const": True},
                "model": {"type": ["string", "null"]},
                "generated_at": {"type": ["string", "null"],
                                 "format": "date-time"},
                "grounded_in": {"type": "array", "items": {"type": "string"}},
                "refused": {"type": "boolean"},
                "refusal_reason": {"type": ["string", "null"]},
            },
        },
        "not_supported": {"type": "array", "items": {"type": "string"}},
        "provenance": {
            "type": "object", "additionalProperties": False,
            "required": ["source", "recipe", "generated_by"],
            "properties": {
                "source": {"type": "string"},
                "recipe": {"type": "string"},
                "generated_by": {"type": "string"},
                "universe_version": {"type": ["integer", "null"]},
                "lag_note": {"type": "string"},
            },
        },
    },
}

# Travels inside every signal. A consumer parsing this contract gets the
# limits in the payload rather than in a README it will not read.
NOT_SUPPORTED = [
    "Company valuation or implied market cap. N-PORT reports a fund's share "
    "count, never the company's shares outstanding, so no company-level value "
    "is derivable from this data.",
    "Any timely signal. Filings lag their period end by roughly 55-60 days "
    "and the bulk data sets lag those again by up to ~90 days.",
    "Complete coverage. Some exposure sits in opaque SPVs that disclose no "
    "underlying, and the size of that gap cannot be quantified.",
    "A return. A split-adjusted change series requires adjudicated split "
    "factors; blocked marks are excluded and counted in guards.",
]


class SignalInvalid(ValueError):
    """A signal that does not satisfy the frozen contract."""


def _scan_forbidden(node, path="$") -> list[str]:
    found = []
    if isinstance(node, dict):
        for key, value in node.items():
            lowered = key.lower()
            if any(bad in lowered for bad in FORBIDDEN_FIELDS):
                found.append(f"{path}.{key}")
            found.extend(_scan_forbidden(value, f"{path}.{key}"))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            found.extend(_scan_forbidden(value, f"{path}[{index}]"))
    return found


def validate(signal: dict) -> dict:
    """Validate against schema 1.0. Raises `SignalInvalid`, returns the signal.

    Two passes, because the second catches what the first cannot. JSON Schema
    with `additionalProperties: false` rejects an unknown field wherever the
    schema reaches -- but `commentary.text` is a free string, and a field
    named `implied_valuation` nested inside a future object would be a schema
    change somebody made deliberately. The name scan is the standing
    prohibition, independent of what the schema happens to allow today.
    """
    import jsonschema

    try:
        jsonschema.validate(signal, SCHEMA,
                            format_checker=jsonschema.FormatChecker())
    except jsonschema.ValidationError as exc:
        location = "$" + "".join(f"[{p!r}]" for p in exc.absolute_path)
        raise SignalInvalid(f"{location}: {exc.message}") from exc

    forbidden = _scan_forbidden(signal)
    if forbidden:
        raise SignalInvalid(
            "the signal carries a field this project does not stand behind: "
            + ", ".join(forbidden)
            + ". N-PORT gives a fund's share count, never the company's "
              "shares outstanding, so no valuation or return is derivable "
              "from it.")
    return signal


def envelope(*, period: dict, coverage: dict, companies: list[dict],
             guards: dict, commentary: dict | None = None,
             universe_version: int | None = 1) -> dict:
    """Assemble a signal and validate it before returning it.

    Validating on the way out rather than at the call site means an invalid
    signal is never written to disk at all -- there is no path from this
    module to a file that skips the contract.
    """
    signal = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(
            timespec="seconds").replace("+00:00", "Z"),
        "period": period,
        "coverage": coverage,
        "companies": companies,
        "guards": guards,
        "commentary": commentary,
        "not_supported": list(NOT_SUPPORTED),
        "provenance": {
            "source": "SEC Form N-PORT bulk data sets (DERA), Form D data "
                      "sets, and N-CSR/N-CSRS restricted-securities footnotes",
            "recipe": "data/raw/Private_AI_Valuation_Agent/plan.md",
            "generated_by": "src/graphs/quarterly_graph.py",
            "universe_version": universe_version,
            "lag_note": "Every figure is as of a filed period end, not as of "
                        "today. See not_supported.",
        },
    }
    return validate(signal)


def write(signal: dict, path: Path) -> Path:
    validate(signal)
    path.write_text(json.dumps(signal, indent=2, default=_json_default),
                    encoding="utf-8", newline="\n")
    return path


def _json_default(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    raise TypeError(f"{type(value).__name__} is not JSON serialisable")
