"""Domain-specific LM on earnings-call text."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from ecis.config.settings import settings
from ecis.guidance_models.qa_parser import parse_qa_corpus

_LOAD = os.getenv("GRAPH_LOAD_LM", "").lower() in {"1", "true", "yes"}
ADAPTER_DIR = Path(os.getenv("DOMAIN_LM_ADAPTER", str(settings.data_dir / "models" / "domain-lm")))


def collect_corpus(ticker: str | None = None) -> list[str]:
    texts: list[str] = []
    for pair in parse_qa_corpus(ticker):
        blob = f"{pair.get('question') or ''} {pair.get('answer') or ''}".strip()
        if blob:
            texts.append(blob)
    try:
        from ecis.db.init_db import get_connection

        conn = get_connection("signals")
        query = "SELECT supporting_quote FROM signals"
        params: list[str] = []
        if ticker:
            query += " WHERE ticker = ?"
            params.append(ticker.upper())
        for row in conn.execute(query, params).fetchall():
            if row["supporting_quote"]:
                texts.append(row["supporting_quote"])
        conn.close()
    except Exception:
        pass
    return texts


def finetune_status() -> dict[str, Any]:
    present = ADAPTER_DIR.exists() and any(ADAPTER_DIR.iterdir()) if ADAPTER_DIR.exists() else False
    return {
        "skipped": not _LOAD,
        "adapter_dir": str(ADAPTER_DIR),
        "adapter_present": present,
        "n_passages": len(collect_corpus()),
        "note": "Masked-LM continue-pretrain is not run here. Drop an adapter at DOMAIN_LM_ADAPTER to use it.",
    }
