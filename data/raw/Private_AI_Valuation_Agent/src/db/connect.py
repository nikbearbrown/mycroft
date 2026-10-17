"""One place that knows how to reach Postgres, and how to say so when it can't.

Supabase shows several connection strings on the same settings page and only
one of them works with psycopg2. The checks here exist because the project has
already lost time to the wrong one being pasted into .env.
"""

import os
import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = Path(__file__).resolve().parent / "schema.sql"

HELP = """
DATABASE_URL must be a Postgres URI, not the Supabase project URL.

  In Supabase: Project Settings -> Database -> Connection string -> URI
  It looks like:
      postgresql://postgres.<ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres
  It does NOT look like:
      https://<ref>.supabase.co          <- that is the REST API URL

Put the URI in .env as DATABASE_URL and re-run. See DATABASE_SETUP.md.
"""


def database_url() -> str:
    load_dotenv(ROOT / ".env")
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        sys.exit("DATABASE_URL is not set in .env.\n" + HELP)
    if not url.startswith(("postgresql://", "postgres://")):
        sys.exit(f"DATABASE_URL is {url.split('://')[0]}://... which psycopg2 cannot use.\n" + HELP)
    return url


def connect(**kwargs):
    """Open a connection, or exit with something a human can act on."""
    url = database_url()
    try:
        return psycopg2.connect(url, connect_timeout=kwargs.pop("connect_timeout", 30), **kwargs)
    except psycopg2.OperationalError as exc:
        sys.exit(f"could not connect to Postgres:\n  {exc}\n{HELP}")


def apply_schema(conn) -> None:
    """Create the tables if they are not already there. Idempotent."""
    with conn.cursor() as cur:
        cur.execute(SCHEMA.read_text(encoding="utf-8"))
    conn.commit()


def main() -> None:
    """python -m src.db.connect -- verify the URL, create the schema, report."""
    conn = connect()
    apply_schema(conn)
    with conn.cursor() as cur:
        cur.execute("SELECT version()")
        print("connected:", cur.fetchone()[0].split(",")[0])
        cur.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' ORDER BY table_name
        """)
        print("tables:", ", ".join(r[0] for r in cur.fetchall()) or "(none)")
    conn.close()


if __name__ == "__main__":
    main()
