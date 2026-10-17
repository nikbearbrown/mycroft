"""Seed the canonical `companies` table from the frozen universe.

Data, not schema, so it lives here rather than in schema.sql. Idempotent: the
upsert is on canonical_name, and re-running after a universe v2 boundary
updates `status` and `universe_version` in place rather than inserting a second
row for the same company.

The full/thin members come from universe_v1.json, which is the Week 1 human
gate and the only place membership is decided. The watchlist names come from
src/resolve/adjudicate.py CANONICAL -- the closed list the resolver is allowed
to return -- because a resolver that can name a company the database has never
heard of would break the foreign key at exactly the moment a human is trying to
record a decision about it.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.ingest.universe import status_of  # noqa: E402
from src.resolve.adjudicate import CANONICAL  # noqa: E402
from src.resolve.match import ISSUER_LEIS  # noqa: E402

UNIVERSE = ROOT / "universe_v1.json"

UPSERT = """
INSERT INTO companies (canonical_name, status, lei, universe_version, notes)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT (canonical_name) DO UPDATE
   SET status = EXCLUDED.status,
       lei = COALESCE(EXCLUDED.lei, companies.lei),
       universe_version = EXCLUDED.universe_version,
       notes = COALESCE(EXCLUDED.notes, companies.notes)
RETURNING company_id
"""


def _leis() -> dict:
    """canonical name -> one verified LEI, where the project has one."""
    out: dict = {}
    for lei, company in ISSUER_LEIS.items():
        out.setdefault(company, lei)
    return out


def seed_companies(conn) -> dict:
    """Insert or refresh every company the resolver may name. Returns
    canonical_name -> company_id."""
    frozen = json.loads(UNIVERSE.read_text(encoding="utf-8"))
    version = frozen["universe_version"]
    leis = _leis()

    rows = []
    for member in frozen["members"]:
        name = member["canonical_name"]
        rows.append((name, status_of(name), leis.get(name), version,
                     f"universe v{version} member; {member['status']} coverage"))
    for name in frozen.get("carried_thin", []):
        canonical = name if isinstance(name, str) else name.get("canonical_name")
        if canonical:
            rows.append((canonical, status_of(canonical), leis.get(canonical), version,
                         f"universe v{version}, thin coverage"))
    for name in CANONICAL:
        if not any(r[0] == name for r in rows):
            rows.append((name, status_of(name), leis.get(name), version,
                         "watchlist: resolvable, not published at v1"))

    ids: dict = {}
    with conn.cursor() as cur:
        for row in rows:
            cur.execute(UPSERT, row)
            ids[row[0]] = cur.fetchone()[0]
    conn.commit()
    return ids


def company_ids(conn) -> dict:
    with conn.cursor() as cur:
        cur.execute("SELECT canonical_name, company_id FROM companies")
        return dict(cur.fetchall())


def main() -> None:
    from src.db.connect import apply_schema, connect

    conn = connect()
    apply_schema(conn)
    ids = seed_companies(conn)
    with conn.cursor() as cur:
        cur.execute("SELECT status, count(*) FROM companies GROUP BY 1 ORDER BY 1")
        breakdown = ", ".join(f"{n} {s}" for s, n in cur.fetchall())
    print(f"companies: {len(ids)} rows ({breakdown})")
    conn.close()


if __name__ == "__main__":
    main()
