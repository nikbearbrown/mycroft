"""Which EDGAR CIK *is* a universe company, and who says so.

Week 9 needs a join key that a name cannot provide. `plan.md`: "Form D join on
resolved issuer identity, not name string". This module is that identity, and
`company_identity` is where a named human's answer lives.

--------------------------------------------------------------------------
Why the machine cannot finish this one
--------------------------------------------------------------------------
The candidate pool is a name scan, and the three ways it is wrong are all ways
a machine reads as a match:

  * **A vehicle named after the company.** "Anduril Investors LLC",
    "Gaingels Databricks 2024 LLC", "Eagle VP Fund 2 LLC-Series SpaceX". Real
    Form D filers, real dollars raised, and none of it the company's round.
  * **A different company with a colliding name.** "iDox.ai Corp.",
    "Siscale AI, Inc.", "Stax.ai, Inc.", "Apex.AI, Inc." all contain `X.AI` or
    `SCALE AI`. And `x.ai, inc.` (CIK 1609052) is not xAI at all -- it is the
    older scheduling-assistant startup that held the domain first, which is
    the trap this table exists to catch.
  * **A substring that is not a name at all.** `%ANTHROPIC%` matches
    "Community Philanthropic Ventures, LLC", because *phil-anthropic* contains
    it. Nothing about the filing is wrong; the pattern is.

`form_d.candidates` narrows the pool using the filer's own declaration
(`ISPOOLEDINVESTMENTFUNDTYPE`), which is a filed fact rather than an inference.
It does not close it -- two 2026 vehicles declare `INDUSTRYGROUPTYPE =
'Pooled Investment Fund'` while leaving the boolean blank, so they arrive in
the human's queue rather than being filtered out. That is the correct failure
direction: over-refer, never over-accept (P1).

--------------------------------------------------------------------------
What `propose` is and is not
--------------------------------------------------------------------------
`propose` returns a *suggested* verdict with the evidence behind it. It is a
model judgment and is labelled one (P8). Nothing it returns reaches
`company_identity` without `affirm` being called with a real reviewer name.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

VERDICTS = ("operating_company", "vehicle", "not_in_universe", "unresolved")

# Words that look like a reviewer and are not one. Checked by name because the
# docstring promising "'auto' is not a reviewer" was, until a test asked,
# only a docstring: the guard tested for an empty string and let 'auto'
# through.
_NON_NAMES = {"auto", "automatic", "system", "machine", "n/a", "na", "none",
              "unknown", "-", "tbd", "ai", "claude", "bot"}

# Tokens that mark a collective investment vehicle rather than an operating
# company. Checked against the entity name only as *supporting* evidence for a
# proposal -- the binding machine signal is the filer's own pooled-fund
# declaration, and the binding decision is a human's.
VEHICLE_TOKENS = (
    " A SERIES OF ", " SERIES OF ", "SPV", " FUND", "FUNDS ", " PARTNERS",
    " CO-INVEST", " VENTURES", " INVESTORS", " HOLDINGS SPV", " SYNDICATE",
    " OPPORTUNITIES", " CAPITAL FUND", " ALTERNATE", " SECONDARY",
)

# Legal-form suffixes stripped before comparing a filed entity name to a
# canonical one. "Databricks, Inc." and "DATABRICKS INC" are the same filer.
_SUFFIX = re.compile(
    r"[,.]?\s*\b(INC|INCORPORATED|CORP|CORPORATION|PBC|LLC|L\.L\.C|LP|L\.P|"
    r"LTD|LIMITED|CO|COMPANY|HOLDINGS)\b\.?", re.I)


def normalize_entity(name: str) -> str:
    """A filed entity name reduced to the part that identifies the company."""
    text = (name or "").upper()
    text = text.replace("&", " AND ")
    text = re.sub(r"[^A-Z0-9 .]", " ", text)
    previous = None
    while previous != text:
        previous = text
        text = _SUFFIX.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip(" .")


def looks_like_vehicle(entity_name: str) -> bool:
    """Name-shape evidence only. Never the sole basis for a verdict."""
    padded = f" {(entity_name or '').upper()} "
    return any(token in padded for token in VEHICLE_TOKENS)


def propose(candidate: dict, canonical_name: str) -> dict:
    """A suggested verdict for one candidate CIK, with its reasons.

    A judgment, labelled as one. `candidate` is a row from
    `form_d.candidates`; `canonical_name` is the company its name pattern hit.
    """
    entity = candidate.get("entity_name") or ""
    filed = normalize_entity(entity)
    canonical = normalize_entity(canonical_name)
    reasons = []

    name_matches = filed == canonical
    if name_matches:
        reasons.append(f"filed name normalises to the canonical name ({filed!r})")
    else:
        reasons.append(f"filed name {filed!r} != canonical {canonical!r}")

    vehicle_shape = looks_like_vehicle(entity)
    if vehicle_shape:
        reasons.append("entity name carries a pooling token "
                       "(a series, fund, SPV, co-invest or investors vehicle)")

    industries = (candidate.get("industry_groups") or "")
    if "Pooled Investment Fund" in industries or "Investing" in industries:
        reasons.append(f"industry group is {industries!r}, which is an investing "
                       "activity rather than an operating one")
        vehicle_shape = True

    types = candidate.get("entity_types") or ""
    if "Corporation" not in types:
        reasons.append(f"entity type is {types!r}; an operating company in this "
                       "universe files as a Corporation")

    if name_matches and not vehicle_shape:
        verdict, confidence = "operating_company", 0.9
    elif vehicle_shape:
        verdict, confidence = "vehicle", 0.8
    elif not name_matches:
        verdict, confidence = "not_in_universe", 0.6
    else:
        verdict, confidence = "unresolved", 0.0

    return {
        "cik": candidate.get("cik"),
        "entity_name": entity,
        "company_provisional": canonical_name,
        "proposed_verdict": verdict,
        "confidence": confidence,
        "reasons": reasons,
        "is_judgment": True,
        "filings": candidate.get("filings"),
        "first_filing": candidate.get("first_filing"),
        "last_filing": candidate.get("last_filing"),
    }


def edgar_facts(cik: str, session=None) -> dict:
    """State of incorporation, city, former names and form history for a CIK.

    The network half of the evidence, and the half that settles the cases the
    name cannot. `x.ai, inc.` (CIK 1609052) normalises to exactly the same
    string as `X.AI CORP.` (CIK 2002695), so no amount of string work
    separates them -- but one is a Delaware company in New York that filed
    four Form Ds between 2014 and 2017, and the other is a Nevada company in
    Palo Alto that started filing in 2023. That is a decision a reviewer can
    make in one read, and it is not one the matcher should make alone.

    Read-only, one request, rate-limited by the shared throttle.
    """
    import requests

    from src.ingest.download_bulk import throttle, user_agent

    throttle()
    get = (session or requests).get
    response = get(f"https://data.sec.gov/submissions/CIK{cik}.json",
                   headers={"User-Agent": user_agent()}, timeout=60)
    if response.status_code != 200:
        return {"cik": cik, "error": f"HTTP {response.status_code}"}
    payload = response.json()

    recent = payload.get("filings", {}).get("recent", {})
    forms: dict[str, list[str]] = {}
    for form, filed in zip(recent.get("form", []), recent.get("filingDate", [])):
        forms.setdefault(form, []).append(filed)

    business = (payload.get("addresses") or {}).get("business") or {}
    return {
        "cik": cik,
        "name": payload.get("name"),
        "sic_description": payload.get("sicDescription") or None,
        "state_of_incorporation": payload.get("stateOfIncorporation"),
        "city": business.get("city"),
        "former_names": [f.get("name") for f in payload.get("formerNames", [])],
        "form_d_count": len(forms.get("D", [])) + len(forms.get("D/A", [])),
        "form_d_first": min(forms.get("D", ["-"])),
        "form_d_last": max(forms.get("D", ["-"])),
        "all_form_types": sorted(forms),
    }


AFFIRM = """
INSERT INTO company_identity (cik, entity_name, company_id, verdict, source,
                              evidence, reviewer)
VALUES (%(cik)s, %(entity_name)s, %(company_id)s, %(verdict)s, %(source)s,
        %(evidence)s, %(reviewer)s)
ON CONFLICT (cik) DO UPDATE SET
    verdict    = EXCLUDED.verdict,
    company_id = EXCLUDED.company_id,
    evidence   = EXCLUDED.evidence,
    reviewer   = EXCLUDED.reviewer,
    decided_at = now()
"""


def affirm(conn, *, cik: str, verdict: str, reviewer: str, evidence: str,
           company: str | None = None, source: str = "form_d") -> dict:
    """Record a human identity decision. The only way a row reaches the join.

    Deliberately strict, for the reason Week 7's split adjudicator was made
    strict: the version of this that accepted an empty reviewer would have let
    the pipeline clear its own gate, and a gate that clears itself is P4's
    definition of a violation.

    `company` is required for `operating_company` and forbidden otherwise --
    a vehicle resolved *to* a company is precisely the mistake this table
    exists to stop, because it would put the vehicle's raise on the company's
    timeline.
    """
    if verdict not in VERDICTS:
        raise ValueError(f"verdict must be one of {VERDICTS}, got {verdict!r}")
    if not (reviewer or "").strip() or reviewer.strip().lower() in _NON_NAMES:
        raise ValueError("an identity decision needs a named reviewer -- "
                         f"{reviewer!r} is not a name (P4)")
    if not (evidence or "").strip():
        raise ValueError("an identity decision needs written evidence (P3)")
    if verdict == "operating_company" and not company:
        raise ValueError("an operating_company verdict must name the company "
                         "it resolves to")
    if verdict != "operating_company" and company:
        raise ValueError(
            f"a {verdict!r} verdict must not carry a company. Linking a vehicle "
            "to a company is the error this table exists to prevent: it would "
            "put the vehicle's raise onto the company's round timeline."
        )

    with conn.cursor() as cur:
        company_id = None
        if company:
            cur.execute("SELECT company_id FROM companies WHERE canonical_name = %s",
                        (company,))
            row = cur.fetchone()
            if not row:
                raise ValueError(f"no company named {company!r} in companies")
            company_id = row[0]

        cur.execute("SELECT entity_name FROM form_d_filings WHERE cik = %s LIMIT 1",
                    (cik,))
        row = cur.fetchone()
        entity_name = row[0] if row else cik

        cur.execute(AFFIRM, {
            "cik": cik, "entity_name": entity_name, "company_id": company_id,
            "verdict": verdict, "source": source,
            "evidence": f"{reviewer.strip()}: {evidence.strip()}",
            "reviewer": reviewer.strip(),
        })
    conn.commit()
    return {"cik": cik, "entity_name": entity_name, "verdict": verdict,
            "company": company, "reviewer": reviewer.strip()}


def outstanding(conn) -> list[dict]:
    """Candidate CIKs with no recorded human decision."""
    from src.ingest.form_d import candidates

    return [c for c in candidates(conn) if not c["already_decided"]]


def summary(conn) -> dict:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT verdict, count(*) AS ciks FROM company_identity
             GROUP BY 1 ORDER BY 1
        """)
        by_verdict = [dict(zip([c[0] for c in cur.description], r))
                      for r in cur.fetchall()]
        cur.execute("""
            SELECT c.canonical_name AS company, i.cik, i.entity_name
              FROM company_identity i
              JOIN companies c ON c.company_id = i.company_id
             WHERE i.verdict = 'operating_company'
             ORDER BY 1
        """)
        operating = [dict(zip([c[0] for c in cur.description], r))
                     for r in cur.fetchall()]
    return {"by_verdict": by_verdict, "operating_companies": operating,
            "outstanding": len(outstanding(conn))}
