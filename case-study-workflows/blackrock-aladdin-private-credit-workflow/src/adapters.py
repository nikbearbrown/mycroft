"""
Data Retrieval Adapters.

Input: scoped tool list, structured query parameters.
Output: raw structured data from each source.

§3.3's own [DEV] marker says "map it to what you actually have" without
showing any schema at all — read literally, that's not actionable for a
learner with no internal BlackRock systems to map to. This repo replaces
that empty instruction with illustrative stub data (see data/stub_*.json).
THESE ARE NOT REAL BLACKROCK OR PREQIN RECORDS — invented figures, clearly
labeled, for demonstrating the pipeline end-to-end.

Documented limitation (found via a dry-run trace during design, not
discovered after the fact): the private credit adapter can filter by
borrower_name; the portfolio holdings adapter cannot, because portfolio
records are keyed only by fund_id, not borrower name. For a borrower-scoped
query, portfolio holdings can only be correctly scoped via a post-retrieval
join on fund_id (done in pipeline.py), not independently in this adapter.
This means the two adapters are only truly independent for fund-ID-scoped
queries — not for borrower-name-scoped ones. A production system fielding
borrowers with positions across multiple funds would need a dedicated
borrower-to-fund resolution step performed BEFORE scoping, not after.

Extension note: a real internal API client is very likely synchronous.
Swapping this stub for a real one means either wrapping your sync call with
asyncio.to_thread(), or converting the retrieval step to concurrent.futures
instead of asyncio.gather.
"""
import asyncio
import json
from abc import ABC, abstractmethod


class Adapter(ABC):
    @abstractmethod
    async def fetch(self, params: dict) -> list[dict]:
        """Returns raw structured records. Async because retrieval happens in
        parallel across adapters."""
        raise NotImplementedError


class PrivateCreditAdapter(Adapter):
    """Illustrative stub — reads from a local JSON file standing in for a
    Preqin-equivalent private credit data source. NOT real BlackRock or
    Preqin data. Replace fetch() with a real API/warehouse call; keep the
    return shape (list of dicts with these field names) or update
    BenchmarkCalculator to match."""

    def __init__(self, stub_path: str = "data/stub_private_credit.json"):
        self.stub_path = stub_path

    async def fetch(self, params: dict) -> list[dict]:
        with open(self.stub_path) as f:
            records = json.load(f)

        if params.get("fund_scope"):
            records = [r for r in records if r["fund_id"] in params["fund_scope"]]

        borrower = params.get("borrower_or_entity")
        if borrower:
            needle = borrower.strip().lower()
            records = [r for r in records if needle in r["borrower_name"].lower()]

        return records


class PortfolioHoldingsAdapter(Adapter):
    """Illustrative stub — same pattern, standing in for a portfolio system.
    Cannot filter by borrower name (see module docstring) — only by fund_id.
    A borrower-scoped query gets an unfiltered result here; pipeline.py joins
    it against the private credit adapter's fund_id after both return."""

    def __init__(self, stub_path: str = "data/stub_portfolio.json"):
        self.stub_path = stub_path

    async def fetch(self, params: dict) -> list[dict]:
        with open(self.stub_path) as f:
            records = json.load(f)

        if params.get("fund_scope"):
            records = [r for r in records if r["fund_id"] in params["fund_scope"]]

        return records


async def retrieve_parallel(scoped_tools: dict, params: dict) -> dict:
    """Runs every scoped adapter concurrently.
    Genuinely independent for fund-ID-scoped queries; see the documented
    limitation above for borrower-scoped ones."""
    names = list(scoped_tools.keys())
    results = await asyncio.gather(*(adapter.fetch(params) for adapter in scoped_tools.values()))
    return dict(zip(names, results))
