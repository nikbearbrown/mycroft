"""
data/stub_scenarios.py

Fixture data for this reference workflow. Three scenarios, chosen
specifically to demonstrate the two design decisions that matter most in
this pipeline (see README.md for the full reasoning):

1. HAPPY_PATH — Coverage passes, Weather matches, Fraud clears, Payout
   recommends. Everything works.
2. UNCOVERED_CLAIM — Coverage fails. Weather and Fraud never run. This is
   the fail-fast behavior in action, not just described in a comment.
3. NO_WEATHER_MATCH — Coverage passes, but Weather finds no matching
   event. This is what actually exercises Fraud's hard dependency on
   Weather's conclusion.

None of this is real Allianz Australia data. This is illustrative fixture
data only.
"""

from dataclasses import dataclass
from datetime import datetime

from models.claim import PolicyRecord


@dataclass
class Scenario:
    name: str
    raw_claim_event: str
    policy_record: PolicyRecord
    meteorological_data: str
    claim_history_summary: str
    expected_outcome: str   # human-readable note for anyone running the demo


HAPPY_PATH = Scenario(
    name="happy_path",
    raw_claim_event=(
        "Claim filed by Laura, policy AUS-POL-88213. A storm caused a "
        "20-hour power outage at her home in Adelaide, SA on 2026-03-14 "
        "starting around 14:00. Approximately AUD $250 of refrigerated "
        "food spoiled as a result."
    ),
    policy_record=PolicyRecord(
        policy_id="AUS-POL-88213",
        active=True,
        covers_food_spoilage=True,
        covers_severe_weather_outage=True,
        policy_limit_aud=2000.0,
    ),
    meteorological_data=(
        "Bureau of Meteorology severe weather warning confirmed for "
        "Adelaide metro area, 2026-03-14, 12:00-18:00: destructive winds "
        "and heavy rainfall causing widespread power outages."
    ),
    claim_history_summary="No prior claims on file for this policyholder.",
    expected_outcome="Covered, weather matched, fraud clear, payout recommended ~$250.",
)

UNCOVERED_CLAIM = Scenario(
    name="uncovered_claim",
    raw_claim_event=(
        "Claim filed by Marcus, policy AUS-POL-40217. A storm caused a "
        "power outage at his home in Perth, WA on 2026-02-02 starting "
        "around 09:00. Approximately AUD $180 of refrigerated food "
        "spoiled as a result."
    ),
    policy_record=PolicyRecord(
        policy_id="AUS-POL-40217",
        active=True,
        covers_food_spoilage=True,
        covers_severe_weather_outage=False,   # <- this is why the claim exits at Coverage
        policy_limit_aud=1500.0,
    ),
    meteorological_data=(
        "Bureau of Meteorology confirms a severe storm cell over Perth "
        "metro, 2026-02-02, 06:00-12:00, with widespread outages reported."
    ),
    claim_history_summary="No prior claims on file for this policyholder.",
    expected_outcome=(
        "Not covered — policy excludes severe-weather-outage spoilage. "
        "Workflow exits at Coverage; Weather and Fraud never run."
    ),
)

NO_WEATHER_MATCH = Scenario(
    name="no_weather_match",
    raw_claim_event=(
        "Claim filed by Priya, policy AUS-POL-77105. A power outage at "
        "her home in Brisbane, QLD on 2026-04-01 starting around 20:00, "
        "described as storm-related. Approximately AUD $220 of "
        "refrigerated food spoiled as a result."
    ),
    policy_record=PolicyRecord(
        policy_id="AUS-POL-77105",
        active=True,
        covers_food_spoilage=True,
        covers_severe_weather_outage=True,
        policy_limit_aud=1800.0,
    ),
    meteorological_data=(
        "Bureau of Meteorology has no severe weather warnings or reports "
        "for the Brisbane metro area on 2026-04-01. Conditions recorded "
        "as fine, light winds, no rainfall of note."
    ),
    claim_history_summary="Two prior food-spoilage claims from this policyholder in the last 8 months.",
    expected_outcome=(
        "Covered by policy, but Weather finds no matching event — this, "
        "combined with prior claim pattern, is the input Fraud weighs. "
        "Outcome depends on the model's judgment (clear or flagged) — "
        "this scenario exists to exercise that dependency, not to force "
        "a specific result."
    ),
)

ALL_SCENARIOS = {
    "happy_path": HAPPY_PATH,
    "uncovered_claim": UNCOVERED_CLAIM,
    "no_weather_match": NO_WEATHER_MATCH,
}
