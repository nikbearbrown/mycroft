"""Week 6: the resolution graph and the review queue.

Two kinds of test here.

The pure ones need nothing but the module. The rest need a live Postgres,
because a review queue whose durability is mocked has not been tested at all --
the whole claim is that the state is in a database and not in a process. They
build a small synthetic corpus in their own database, engineered so that one
holding hits each trigger, and they skip (never silently pass) when no server
is reachable.

Point them at a server with REVIEW_TEST_DB_URL, or let them find a local
cluster on the default port. They never touch DATABASE_URL: the project's own
database is not a test fixture.

The load-bearing test is test_a_paused_review_survives_a_new_process, which
runs the resume in a genuine second interpreter. plan.md week 6 asks for "a
paused run [that] survives restart and resumes days later"; asserting that
inside one process would only prove the object was still in memory.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

import psycopg2
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.db.seed import seed_companies  # noqa: E402
from src.graphs.resolve_graph import (  # noqa: E402
    SPLIT_MAX_RATIO,
    SPLIT_TOLERANCE,
    is_split_ratio,
    build_graph,
    checkpointer_from,
    company_key,
    decision_key,
    pending_ambiguities,
    resolve_one,
    split_signals,
    thread_id,
)

FIXTURE = ROOT / "tests" / "fixtures" / "review_decisions_v1.json"
SCHEMA = ROOT / "src" / "db" / "schema.sql"

# Decisions made in these tests are attributed to "test-reviewer", never to a
# real person. A human's name on a decision they did not make would be a
# fabricated attestation, and the fixture these tests read is the same file the
# real queue exports into.
REVIEWER = "test-reviewer"

CANDIDATE_URLS = [
    os.getenv("REVIEW_TEST_DB_URL"),
    "postgresql://postgres:postgres@127.0.0.1:55432/postgres",
    "postgresql://postgres:postgres@127.0.0.1:5432/postgres",
]


# --------------------------------------------------------------------------
# Pure tests -- no database
# --------------------------------------------------------------------------


def test_decision_key_collapses_case_and_whitespace():
    """The two MWAM SpaceX vehicles differ only by a trailing space in the
    filed name. That is one question, not two."""
    a = decision_key("MWAM VC SpaceX-II, LLC ", "MWAM VC SPACEX-II")
    b = decision_key("mwam  vc spacex-ii, llc", "MWAM VC  SPACEX-II ")
    assert a == b
    assert a == "MWAM VC SPACEX-II, LLC || MWAM VC SPACEX-II"


def test_decision_key_keeps_different_titles_apart():
    """Collapsing whitespace must not collapse actual securities. Anduril
    Series F and Series H are different rows and different questions."""
    f = decision_key("ANDURIL ENGINEERING LLC", "ANDURIL ENGINEERING LLC, SERIES F")
    h = decision_key("ANDURIL ENGINEERING LLC", "ANDURIL ENGINEERING LLC, SERIES H")
    assert f != h


def test_thread_id_is_deterministic_so_a_rerun_resumes():
    """If the thread id moved between runs, every re-run would open a second
    thread and the paused review would be orphaned rather than resumed."""
    key = decision_key("X.AI HOLDINGS CORP", "X.AI HOLDINGS CORP")
    assert thread_id(key) == thread_id(key)
    assert thread_id(key) != thread_id(key + " ")  # different key, different thread
    assert thread_id(key).startswith("resolve:")


def test_company_key_is_distinct_from_any_spelling_key():
    """A decision about the company must not collide with a decision about a
    string that happens to be the company's name."""
    assert company_key("X.AI Corp") != decision_key("X.AI Corp", "X.AI Corp")


def test_the_split_rule_is_capped_and_relative():
    """Regression, twice over. The rule has been wrong in two directions.

    First it used 2% *of the ratio* with no cap: at 348 -- what OpenAI's $1.00
    placeholder rows produce against a real ~$348 mark -- a 2% window is plus
    or minus 7, so almost any number counted as near-integer, and three OpenAI
    keys were flagged as suspected splits.

    The fix was an absolute 0.02 window plus a cap of 20, and **the cap was the
    part that mattered**. The absolute window then quietly failed plan.md's own
    verification case: Perplexity's 695 -> 58 is a ratio of 11.93, and 0.02
    around 12 misses it by a factor of three. Corrected in Week 7 to a relative
    1% window under the same cap, in src/marks/splits.py, which both this queue
    trigger and the marks detector now import.
    """
    assert is_split_ratio(10.0)        # the SpaceX unit artifact
    assert is_split_ratio(11.93)       # plan.md's Perplexity case, missed by 0.02 absolute
    assert is_split_ratio(11.983)
    assert is_split_ratio(4.0181)      # quarantined, and a human says it is a repricing
    assert not is_split_ratio(348.5255)  # excluded by the cap, not by the tolerance
    assert not is_split_ratio(306.0239)
    assert not is_split_ratio(2.064)   # X.AI, an ordinary repricing 44 times over
    assert not is_split_ratio(8.299)   # Figure AI, a large move but not near-integer
    assert not is_split_ratio(1.87)

    # The cap is what keeps a placeholder artifact out, so pin it explicitly.
    assert SPLIT_MAX_RATIO == 20
    assert SPLIT_TOLERANCE == 0.01


# --------------------------------------------------------------------------
# Database fixtures
# --------------------------------------------------------------------------


def _reachable(url):
    try:
        conn = psycopg2.connect(url, connect_timeout=3)
    except Exception:
        return False
    conn.close()
    return True


@pytest.fixture(scope="module")
def db_url():
    for url in CANDIDATE_URLS:
        if url and _reachable(url):
            break
    else:
        pytest.skip("no Postgres reachable; set REVIEW_TEST_DB_URL to run the queue tests")

    name = f"review_test_{uuid.uuid4().hex[:8]}"
    admin = psycopg2.connect(url)
    admin.autocommit = True
    with admin.cursor() as cur:
        cur.execute(f'CREATE DATABASE "{name}"')
    admin.close()

    test_url = url.rsplit("/", 1)[0] + "/" + name
    yield test_url

    admin = psycopg2.connect(url)
    admin.autocommit = True
    with admin.cursor() as cur:
        cur.execute(f"""
            SELECT pg_terminate_backend(pid) FROM pg_stat_activity
             WHERE datname = '{name}' AND pid <> pg_backend_pid()
        """)
        cur.execute(f'DROP DATABASE IF EXISTS "{name}"')
    admin.close()


# One synthetic holding per trigger, plus two spellings of one company so the
# reuse path has something to reuse. Prices are chosen to make the split test
# deterministic: 10.00 -> 100.00 is a ratio of exactly 10.
CORPUS = [
    # (issuer_name, title, lei, price, period, holdings, expect)
    ("Databricks, Inc.", "DATABRICKS, INC. SERIES H", None, 100.0, "2026-03-31", "auto"),
    ("DATABRICKS INC", "DATABRICKS INC SERIES H", None, 100.0, "2026-03-31", "auto"),
    ("COHERE TECHNOLOGIES, INC. PREFERRED SERIES D-1", "COHERE TECHNOLOGIES",
     None, 7.0, "2026-03-31", "unresolved"),
    # 0.90 exactly: the top of the review band is exclusive, so this one is
    # accepted. Week 4 measured these SPV strings, and the band edge is a real
    # boundary rather than a made-up one.
    ("DXYZ SpaceX I LLC (economic exposure to Space Exploration Technologies Corp.)",
     "DXYZ SPACEX I LLC", None, 200.0, "2026-03-31", "auto"),
    # 0.80: the blended-class SPV string from Week 4, which is the bottom of
    # the band and the only thing in this corpus that lands inside it.
    ("MWAM VC SPACEX-II, LLC (ECONOMIC EXPOSURE TO SPACE EXPLORATION TECHNOLOGIES "
     "CORP., 55% CLASS A COMMON STOCK AND 45% CLASS C COMMON STOCK)",
     "MWAM VC SPACEX-II LLC", None, 200.0, "2026-03-31", "band"),
    ("X.AI HOLDINGS CORP", "X.AI HOLDINGS CORP CLASS A", None, 50.0, "2026-03-31",
     "new_company"),
    ("X.AI, CORP.", "X.AI CORP SERIES C", None, 50.0, "2026-03-31", "new_company"),
]

SPLIT_ROWS = [
    ("Anthropic PBC", "ANTHROPIC PBC CLASS A", 10.0, "2025-12-31"),
    ("Anthropic PBC", "ANTHROPIC PBC CLASS A", 100.0, "2026-03-31"),
]


def _build_corpus(conn):
    with conn.cursor() as cur:
        cur.execute(SCHEMA.read_text(encoding="utf-8"))
        cur.execute("INSERT INTO funds (cik, series_id, fund_name, family) "
                    "VALUES ('0000000001', 'S1', 'Test Fund', 'TestCo') RETURNING fund_id")
        fund_id = cur.fetchone()[0]

        def filing(period, accession):
            cur.execute("INSERT INTO filings (fund_id, accession, form_type, period_end) "
                        "VALUES (%s, %s, 'NPORT-P', %s) "
                        "ON CONFLICT (accession) DO UPDATE SET period_end = EXCLUDED.period_end "
                        "RETURNING filing_id", (fund_id, accession, period))
            return cur.fetchone()[0]

        holding_no = 0
        for name, title, lei, price, period, _expect in CORPUS:
            holding_no += 1
            fid = filing(period, f"acc-{period}")
            cur.execute("""
                INSERT INTO raw_holdings
                    (filing_id, holding_id, issuer_name, title_of_issue, lei, balance,
                     value_usd, price_per_share, company_provisional, is_spv, source_quarter)
                VALUES (%s, %s, %s, %s, %s, 10, %s, %s, NULL, false, '2026q1')
            """, (fid, f"h{holding_no}", name, title, lei, price * 10, price))

        for name, title, price, period in SPLIT_ROWS:
            holding_no += 1
            fid = filing(period, f"acc-{period}")
            cur.execute("""
                INSERT INTO raw_holdings
                    (filing_id, holding_id, issuer_name, title_of_issue, balance,
                     value_usd, price_per_share, company_provisional, is_spv, source_quarter)
                VALUES (%s, %s, %s, %s, 10, %s, %s, 'Anthropic PBC', false, '2026q1')
            """, (fid, f"h{holding_no}", name, title, price * 10, price))
    conn.commit()
    seed_companies(conn)


@pytest.fixture(scope="module")
def db(db_url):
    conn = psycopg2.connect(db_url)
    _build_corpus(conn)
    yield conn
    conn.close()


@pytest.fixture
def graph_for(db, db_url):
    """A compiled graph plus the work list, sharing one checkpointer."""
    from contextlib import ExitStack

    stack = ExitStack()
    cp = stack.enter_context(checkpointer_from(db_url))
    cp.setup()
    yield build_graph(db, cp), pending_ambiguities(db, only_undecided=False), split_signals(db)
    stack.close()


def _find(items, needle):
    for item in items:
        if needle.upper() in item["decision_key"]:
            return item
    raise AssertionError(f"no ambiguity matching {needle!r}")


def _is_paused(graph, key):
    config = {"configurable": {"thread_id": thread_id(key)}}
    snapshot = graph.get_state(config)
    return any(getattr(task, "interrupts", ()) for task in snapshot.tasks)


# --------------------------------------------------------------------------
# Database tests
# --------------------------------------------------------------------------


def test_the_corpus_produces_one_ambiguity_per_distinct_pair(graph_for):
    _, items, _ = graph_for
    assert len(items) == len(CORPUS) + 1  # the two split rows share one pair


def test_the_top_of_the_review_band_is_exclusive(graph_for):
    """0.90 accepts; 0.80 asks. Week 4 found the threshold is a band, not a
    number, and four real SPV strings sit on its floor -- so which side of the
    boundary each edge falls on has to be pinned rather than assumed."""
    graph, items, splits = graph_for
    at_ceiling = _find(items, "DXYZ")
    result = resolve_one(graph, at_ceiling, splits.get(at_ceiling["decision_key"]))
    assert result["score"] == 0.90
    assert result["route"] == "accept"


def test_a_confident_match_is_never_sent_to_a_human(graph_for, db):
    graph, items, splits = graph_for
    item = _find(items, "DATABRICKS, INC.")
    result = resolve_one(graph, item, splits.get(item["decision_key"]))
    assert result["route"] == "accept"
    assert result["company"] == "Databricks, Inc."
    assert not _is_paused(graph, item["decision_key"])
    with db.cursor() as cur:
        cur.execute("SELECT method FROM match_decisions WHERE decision_key = %s",
                    (item["decision_key"],))
        assert cur.fetchone()[0] in ("lei", "alias", "fuzzy", "spv")


def test_an_unresolved_holding_stops_and_writes_nothing(graph_for, db):
    """P2/P3: a paused review must not leave a half-decided row behind."""
    graph, items, splits = graph_for
    item = _find(items, "COHERE")
    resolve_one(graph, item, splits.get(item["decision_key"]))
    assert _is_paused(graph, item["decision_key"])
    with db.cursor() as cur:
        cur.execute("SELECT count(*) FROM match_decisions WHERE decision_key = %s",
                    (item["decision_key"],))
        assert cur.fetchone()[0] == 0


def test_a_near_integer_price_step_reaches_a_human(graph_for):
    """plan.md: a suspected split is routed to a human, never auto-adjusted --
    even when the matcher is completely sure of the company."""
    graph, items, splits = graph_for
    item = _find(items, "ANTHROPIC")
    assert splits.get(item["decision_key"]), "the 10x step should have been detected"
    result = resolve_one(graph, item, splits.get(item["decision_key"]))
    assert result["trigger"] == "split"
    assert result["route"] == "review"
    assert result["company"] == "Anthropic PBC"  # confident, and still asked


def test_a_watchlist_company_is_a_universe_decision_not_a_matcher_one(graph_for):
    graph, items, splits = graph_for
    item = _find(items, "X.AI HOLDINGS CORP")
    result = resolve_one(graph, item, splits.get(item["decision_key"]))
    assert result["trigger"] == "new_company"
    assert result["route"] == "review"


def test_a_decision_needs_a_named_reviewer_and_a_reason(graph_for):
    """P4: 'looks good' is not a handoff condition, and 'auto' is not a name."""
    from langgraph.types import Command

    graph, items, splits = graph_for
    item = _find(items, "MWAM")
    result = resolve_one(graph, item, splits.get(item["decision_key"]))
    assert result["trigger"] == "band", f"expected the band, got {result['trigger']}"
    config = {"configurable": {"thread_id": thread_id(item["decision_key"])}}

    for bad in (
        {"verdict": "company", "company": "Space Exploration Technologies Corp.",
         "reviewer": "", "rationale": "sure"},
        {"verdict": "company", "company": "Space Exploration Technologies Corp.",
         "reviewer": "test-reviewer", "rationale": "   "},
        {"verdict": "yes", "reviewer": "test-reviewer", "rationale": "sure"},
        {"verdict": "company", "company": "Acme Inc.", "reviewer": "test-reviewer",
         "rationale": "a company the universe has never heard of"},
    ):
        with pytest.raises((ValueError, TypeError)):
            graph.invoke(Command(resume=bad), config=config)
    assert _is_paused(graph, item["decision_key"]), "a rejected answer must not clear the review"


def test_a_decision_is_reused_and_the_question_is_never_asked_twice(graph_for, db):
    """The deliverable, in one test: answer X.AI once, and the second spelling
    resolves without ever reaching a human."""
    from langgraph.types import Command

    graph, items, splits = graph_for
    first = _find(items, "X.AI HOLDINGS CORP")
    second = _find(items, "X.AI, CORP.")

    resolve_one(graph, first, splits.get(first["decision_key"]))
    config = {"configurable": {"thread_id": thread_id(first["decision_key"])}}
    graph.invoke(Command(resume={
        "verdict": "company", "company": "X.AI Corp", "reviewer": "test-reviewer",
        "rationale": "x.AI is the issuer; admitted for resolution, still watchlist for publication",
    }), config=config)

    result = resolve_one(graph, second, splits.get(second["decision_key"]))
    assert result["reused"] is True
    assert result["method"] == "reused"
    assert result["company"] == "X.AI Corp"
    assert not _is_paused(graph, second["decision_key"])
    with db.cursor() as cur:
        cur.execute("SELECT reviewer, rationale FROM match_decisions WHERE decision_key = %s",
                    (second["decision_key"],))
        reviewer, rationale = cur.fetchone()
    assert reviewer == "test-reviewer", "a reused decision must still name the human who made it"
    assert rationale


def test_match_decisions_holds_exactly_one_row_per_holding(db):
    with db.cursor() as cur:
        cur.execute("""
            SELECT count(*), count(DISTINCT raw_id) FROM match_decisions
        """)
        total, distinct = cur.fetchone()
    assert total == distinct, "plan.md declares unique (raw_id); a holding is decided once"


def test_a_paused_review_survives_a_new_process(db_url, db):
    """The claim of the week, tested the only way it can honestly be tested.

    Process one runs the graph until it interrupts, then exits. Process two --
    a genuinely separate interpreter, sharing nothing but Postgres -- resumes
    the same thread by id and answers it. If the checkpoint were in memory the
    second process would find no thread to resume.
    """
    key = decision_key("COHERE TECHNOLOGIES, INC. PREFERRED SERIES D-1",
                       "COHERE TECHNOLOGIES")
    pause = f"""
import sys
sys.path.insert(0, r"{ROOT}")
import psycopg2
from src.graphs.resolve_graph import (build_graph, checkpointer_from,
                                      pending_ambiguities, split_signals, resolve_one)
conn = psycopg2.connect({db_url!r})
items = pending_ambiguities(conn, only_undecided=False)
item = [i for i in items if "COHERE" in i["decision_key"]][0]
with checkpointer_from({db_url!r}) as cp:
    graph = build_graph(conn, cp)
    resolve_one(graph, item, split_signals(conn).get(item["decision_key"]))
print("PAUSED")
"""
    resume = f"""
import sys
sys.path.insert(0, r"{ROOT}")
import psycopg2
from langgraph.types import Command
from src.graphs.resolve_graph import build_graph, checkpointer_from, thread_id
conn = psycopg2.connect({db_url!r})
config = {{"configurable": {{"thread_id": thread_id({key!r})}}}}
with checkpointer_from({db_url!r}) as cp:
    graph = build_graph(conn, cp)
    snapshot = graph.get_state(config)
    assert any(getattr(t, "interrupts", ()) for t in snapshot.tasks), "no paused thread found"
    result = graph.invoke(Command(resume={{
        "verdict": "not_in_universe",
        "reviewer": "test-reviewer",
        "rationale": "Cohere Technologies is a different company; the name pattern was a canary",
    }}), config=config)
print("RESUMED", result["verdict"], result["persisted"])
"""
    first = subprocess.run([sys.executable, "-c", pause], capture_output=True, text=True)
    assert "PAUSED" in first.stdout, first.stderr[-2000:]

    second = subprocess.run([sys.executable, "-c", resume], capture_output=True, text=True)
    assert "RESUMED not_in_universe" in second.stdout, second.stderr[-2000:]

    with db.cursor() as cur:
        cur.execute("SELECT verdict, reviewer FROM review_decisions WHERE decision_key = %s",
                    (key,))
        row = cur.fetchone()
    assert row == ("not_in_universe", "test-reviewer")


def test_the_queue_reports_unresolved_rather_than_dropping_them(graph_for, db):
    """plan.md error handling: 'An unresolved holding is never dropped.'"""
    graph, items, splits = graph_for
    with db.cursor() as cur:
        cur.execute("SELECT count(*) FROM raw_holdings")
        holdings = cur.fetchone()[0]
        cur.execute("SELECT count(DISTINCT raw_id) FROM match_decisions")
        decided = cur.fetchone()[0]
    pending = pending_ambiguities(db)
    covered = decided + sum(i["holdings"] for i in pending)
    assert covered == holdings, "every holding is either decided or still in the queue"


# --------------------------------------------------------------------------
# The regression fixture -- every human decision becomes a test case
# --------------------------------------------------------------------------


def test_every_exported_human_decision_is_still_honoured():
    """plan.md week 6: each decision "becomes a regression test case".

    A matcher change that would overturn a human decision is not a matcher
    improvement, it is a silent override. This reads the exported decisions and
    asserts the deterministic matcher does not now contradict one of them.
    """
    if not FIXTURE.exists():
        pytest.skip("no decisions exported yet -- run review_queue.py --export-fixture")
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    decisions = payload["decisions"]
    if not decisions:
        pytest.skip("the fixture is empty; nothing has been decided by a human yet")

    from src.resolve.match import resolve

    contradictions = []
    for row in decisions:
        if row["decision_key"].startswith("COMPANY ||"):
            continue  # a company-level ruling, not a claim about one string
        match = resolve(row["issuer_name"], row["title_of_issue"])
        if row["verdict"] == "not_in_universe" and match.company:
            contradictions.append((row["issuer_name"], "human said no, matcher says "
                                                       f"{match.company}"))
        if row["verdict"] == "company" and match.company and match.company != row["canonical_name"]:
            contradictions.append((row["issuer_name"],
                                   f"human said {row['canonical_name']}, "
                                   f"matcher says {match.company}"))
    assert not contradictions, "the matcher now contradicts a human decision:\n" + "\n".join(
        f"  {name}: {why}" for name, why in contradictions
    )
