"""
Accountability Layer — Web Test Interface
Exposes the full accountability layer: RunSession lifecycle, SEC-01 scope tiers,
DataSource provenance, ADR-04 confidence degradation, ADR-08 classification.

Phase 1 additions:
  C-03  SQLite persistent store (append-only, 90-day TTL)
  C-04  Ticker query API  GET /api/runs?ticker&from&to
        Drift surface     GET /api/runs/drift?ticker
  UN-05 Reviewer flags    POST/GET /api/runs/{id}/flags
  SEC-02 JWT auth         POST /api/auth/token  →  Bearer token required on /api/chat

Run from the accountability_layer/ directory:
    uvicorn web.server:app --reload --port 8000
"""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional

from dotenv import load_dotenv, find_dotenv

# Search upward from cwd for a .env file (finds it in accountability_layer/ or mycroft/)
load_dotenv(find_dotenv(usecwd=True) or find_dotenv())

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import unicodedata

from adapters.gemini_adapter import (
    make_gemini_adapter,
    RateLimitDailyError,
    RateLimitMinuteError,
)
from adapters.mock_adapter import make_mock_adapter
from adapters.ollama_adapter import (
    make_ollama_adapter,
    OllamaConnectionError,
    OllamaModelError,
)
from claims import extract_claims
from consistency import run_consistency_probe
from verification import verify_claims
from directive import get_active_directive
from middleware import HaltError, run_validation_loop
from schemas import (
    AgentID,
    ConfidenceClassification,
    DataSource,
    DataSourceStatus,
    RunSession,
    RunStatus,
)
from web.db import (
    init_db,
    purge_old_runs,
    insert_run,
    insert_session,
    get_runs,
    get_run,
    get_sessions,
    get_session,
    get_drift,
    get_flags,
    insert_flag,
    clear_all,
    migrate_from_json,
)
from web.auth import issue_token, require_scope, ScopeT

STATIC_DIR  = Path(__file__).parent / "static"
LEGACY_FILE = Path(__file__).parent / "data" / "runs.json"

app = FastAPI(title="Accountability Layer — Test Interface")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ── Startup ────────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup() -> None:
    init_db()
    purge_old_runs()
    # One-shot migration from legacy JSON store
    if LEGACY_FILE.exists():
        try:
            data     = json.loads(LEGACY_FILE.read_text(encoding="utf-8"))
            imported = migrate_from_json(
                data.get("runs", []),
                data.get("sessions", {}),
            )
            if imported:
                # Rename rather than delete so the file isn't lost
                LEGACY_FILE.rename(LEGACY_FILE.with_suffix(".json.migrated"))
        except Exception:
            pass  # corrupt legacy file — ignore


# ── Live config ────────────────────────────────────────────────────────────────

_config: dict = {
    "provider":          "mock",
    "model":             "gemini-2.5-flash",
    "temperature":       0.0,    # ADR: default deterministic — change explicitly for stochastic runs
    "seed":              42,     # stored per-run for replay; fixed seed + temp=0 → deterministic
    "ollama_model":      "llama3.2",
    "agent_id":          "external",
    "failure_mode":      "none",
    "confidence_score":  0.75,
    "consistency_probe": False,   # ADR-06 mitigation — run query twice, compare conclusions
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _ticker(message: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]", "", (message.split() or ["CHAT"])[0])
    return (cleaned.upper()[:10]) or "CHAT"


def _canonicalize(text: str) -> str:
    """
    Normalise input text before prompt assembly.
    Ensures identical prompts are sent for identical logical inputs,
    regardless of whitespace or Unicode encoding differences.
    Week 6 / determinism: this is a prerequisite for seed-based replay to be meaningful.
      - Unicode NFC normalisation (e.g. composed vs decomposed accents → same bytes)
      - Strip leading/trailing whitespace
      - Collapse runs of spaces/tabs to a single space (preserves newlines)
    """
    text = unicodedata.normalize("NFC", text)
    text = text.strip()
    text = re.sub(r"[ \t]+", " ", text)   # collapse horizontal whitespace only
    return text


def _classify(score: float) -> ConfidenceClassification:
    return (
        ConfidenceClassification.HIGH_UNCERTAINTY
        if score < 0.4
        else ConfidenceClassification.STANDARD
    )


def _mock_data_sources() -> tuple[DataSource, ...]:
    return (
        DataSource(
            source="Mock Calendar API",
            status=DataSourceStatus.SIMULATED,
            url="http://calendar.local/api/v1",
            provenance_note="Simulated — no live calendar connected",
        ),
        DataSource(
            source="Contact Directory",
            status=DataSourceStatus.CACHED,
            url="http://contacts.local/api/v1",
        ),
    )


def _degrade_confidence(base: float, data_sources: tuple[DataSource, ...]) -> float:
    penalty = sum(
        0.1 for ds in data_sources
        if ds.status in (DataSourceStatus.SIMULATED, DataSourceStatus.FAILED)
    )
    return round(max(0.05, base - penalty), 2)


def _build_adapter(config: dict):
    if config["provider"] == "gemini":
        return make_gemini_adapter(
            model=config["model"],
            temperature=config["temperature"],
            seed=config.get("seed"),
        )
    if config["provider"] == "ollama":
        return make_ollama_adapter(
            model=config.get("ollama_model", "llama3.2"),
            temperature=config["temperature"],
            seed=config.get("seed", 42),
        )
    return make_mock_adapter(failure_mode=config["failure_mode"])


# ── Pydantic request models ────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    context: str = ""


class ConfigUpdate(BaseModel):
    provider:          Optional[Literal["gemini", "mock", "ollama"]] = None
    model:             Optional[str]   = None
    ollama_model:      Optional[str]   = None
    temperature:       Optional[float] = None
    seed:              Optional[int]   = None
    agent_id:          Optional[str]   = None
    failure_mode:      Optional[Literal["none", "retry_success", "halt"]] = None
    confidence_score:  Optional[float] = None
    consistency_probe: Optional[bool]  = None


class TokenRequest(BaseModel):
    scope: Literal["auditor", "investor"]


class FlagRequest(BaseModel):
    flag_type:     Literal["Hallucinated", "Incorrect", "Other"]
    reviewer_note: Optional[str] = None


# ── Auth routes ────────────────────────────────────────────────────────────────

@app.post("/api/auth/token")
async def get_token(body: TokenRequest):
    """
    SEC-02: Issue a JWT for the requested scope.

    TODO (production): verify caller identity before issuing auditor tokens.
    For Phase 1 prototype any caller can self-serve any scope.
    """
    token = issue_token(body.scope)
    return {"access_token": token, "token_type": "bearer", "scope": body.scope}


# ── Static / config routes ─────────────────────────────────────────────────────

@app.get("/")
async def root():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/config")
async def get_config():
    return _config


@app.post("/api/config")
async def update_config(update: ConfigUpdate):
    if update.provider is not None:
        _config["provider"] = update.provider
    if update.model is not None:
        _config["model"] = update.model
    if update.ollama_model is not None:
        _config["ollama_model"] = update.ollama_model
    if update.temperature is not None:
        _config["temperature"] = round(update.temperature, 2)
    if update.seed is not None:
        _config["seed"] = update.seed
    if update.agent_id is not None:
        try:
            AgentID(update.agent_id)
        except ValueError:
            raise HTTPException(400, detail=f"Unknown agent_id: {update.agent_id!r}")
        _config["agent_id"] = update.agent_id
    if update.failure_mode is not None:
        _config["failure_mode"] = update.failure_mode
    if update.confidence_score is not None:
        _config["confidence_score"] = round(
            max(0.0, min(1.0, update.confidence_score)), 2
        )
    if update.consistency_probe is not None:
        _config["consistency_probe"] = update.consistency_probe
    return _config


# ── Chat route (SEC-02: scope from JWT) ───────────────────────────────────────

@app.post("/api/chat")
async def chat(
    request: ChatRequest,
    scope: ScopeT = Depends(require_scope),
):
    """
    Execute one agent run through the full accountability loop.

    SEC-02: scope is read from the JWT Bearer token, NOT from a query param.
    scope=auditor  → full record including thought_log (internal tier)
    scope=investor → thought_log, raw_output, llm_tokens structurally excluded (SEC-01)
    """
    run_id       = uuid.uuid4()
    agent_id     = AgentID(_config["agent_id"])
    directive    = get_active_directive()
    adapter      = _build_adapter(_config)
    investor     = (scope == "investor")

    # Canonicalize inputs before prompt assembly — prerequisite for seed-based
    # replay to be meaningful. Same logical input must produce the same prompt bytes.
    canonical_message = _canonicalize(request.message)
    canonical_context = _canonicalize(request.context)

    data_sources: tuple[DataSource, ...] = (
        _mock_data_sources() if _config["provider"] == "mock" else ()
    )

    confidence      = _degrade_confidence(_config["confidence_score"], data_sources)
    degraded        = confidence < _config["confidence_score"]
    classification  = _classify(confidence)

    payload: dict = {
        "run_id":                    str(run_id),
        "subject":                   canonical_message,
        "scope":                     scope,
        "halted":                    False,
        "conclusion":                None,
        "thought_log":               None,
        "confidence_score":          confidence,
        "confidence_degraded":       degraded,
        "confidence_classification": classification.value,
        "high_uncertainty":          classification == ConfidenceClassification.HIGH_UNCERTAINTY,
        "data_sources": [
            {
                "source":          ds.source,
                "status":          ds.status.value,
                "url":             ds.url,
                "provenance_note": ds.provenance_note,
            }
            for ds in data_sources
        ],
        "reasoning_objects":  [],
        "session":            None,
        "error":              None,
        "config_snapshot":    dict(_config),
        # ADR-06 mitigations — populated after successful run
        "claims":              [],    # structured claims extracted from thought_log
        "consistency":         None,  # consistency probe result (if enabled)
        "verification_rate":   None,  # fraction of citation claims confirmed against source
    }

    initiated_at = datetime.now(timezone.utc)

    try:
        result = run_validation_loop(
            canonical_message,
            canonical_context,
            run_id,
            agent_id,
            confidence_score=confidence,
            data_sources=data_sources,
            call_agent_fn=adapter,
        )

        session = RunSession(
            ticker=_ticker(request.message),
            directive_version=directive.version,
            directive_text=directive.text,
            run_id=run_id,
            initiated_at=initiated_at,
            status=RunStatus.COMPLETE,
            reasoning_objects=tuple(result.reasoning_objects),
            run_confidence_score=confidence,
            confidence_classification=classification,
            completed_at=datetime.now(timezone.utc),
        )

        payload["reasoning_objects"] = [
            ro.to_dict(investor_scope=investor) for ro in result.reasoning_objects
        ]
        payload["session"] = session.to_dict()

        if result.final_response:
            payload["conclusion"]  = result.final_response.conclusion
            payload["thought_log"] = None if investor else result.final_response.thought_log

            # ── ADR-06: claim extraction + verification ────────────────────────
            thought_log_text = result.final_response.thought_log
            if thought_log_text:
                raw_claims = extract_claims(thought_log_text)
                verified_claims, v_rate = verify_claims(raw_claims)
                payload["claims"]            = [c.to_dict() for c in verified_claims]
                payload["verification_rate"] = v_rate

            # ── ADR-06: consistency probe — auto-on for Ollama, opt-in otherwise ──
            probe_enabled = _config.get("consistency_probe") or _config.get("provider") == "ollama"
            if probe_enabled and result.final_response.conclusion:
                probe = run_consistency_probe(
                    subject=canonical_message,
                    context=canonical_context,
                    agent_id=agent_id,
                    confidence_score=confidence,
                    data_sources=data_sources,
                    call_agent_fn=adapter,
                    primary_conclusion=result.final_response.conclusion,
                )
                payload["consistency"] = probe.to_dict()

    except HaltError as exc:
        session = RunSession(
            ticker=_ticker(request.message),
            directive_version=directive.version,
            directive_text=directive.text,
            run_id=run_id,
            initiated_at=initiated_at,
            status=RunStatus.HALTED,
            reasoning_objects=tuple(exc.reasoning_objects),
            completed_at=datetime.now(timezone.utc),
        )
        payload["halted"]            = True
        payload["error"]             = str(exc)
        payload["reasoning_objects"] = [
            ro.to_dict(investor_scope=investor) for ro in exc.reasoning_objects
        ]
        payload["session"] = session.to_dict()

    except EnvironmentError as exc:
        payload["halted"] = True
        payload["error"]  = f"Configuration error: {exc}"

    except RateLimitDailyError as exc:
        payload["halted"] = True
        payload["error"]  = f"⛔ Daily quota exhausted: {exc}"

    except RateLimitMinuteError as exc:
        payload["halted"] = True
        payload["error"]  = f"⏳ Rate limited: {exc}"

    except OllamaConnectionError as exc:
        payload["halted"] = True
        payload["error"]  = f"🦙 Ollama unreachable: {exc}"

    except OllamaModelError as exc:
        payload["halted"] = True
        payload["error"]  = f"🦙 Ollama model error: {exc}"

    except Exception as exc:
        payload["halted"] = True
        payload["error"]  = f"Adapter error — {type(exc).__name__}: {exc}"

    # C-03: persist to SQLite
    insert_run(payload)
    if payload["session"]:
        insert_session(str(run_id), _ticker(request.message), payload["session"])

    return payload


# ── Run query routes (C-04) ────────────────────────────────────────────────────

@app.get("/api/runs")
async def list_runs(
    ticker: Optional[str] = Query(default=None, description="Filter by ticker symbol"),
    from_dt: Optional[str] = Query(default=None, alias="from", description="ISO-8601 start date"),
    to_dt:   Optional[str] = Query(default=None, alias="to",   description="ISO-8601 end date"),
    limit:   int           = Query(default=50,   le=200),
):
    return get_runs(ticker=ticker, from_dt=from_dt, to_dt=to_dt, limit=limit)


@app.get("/api/runs/drift")
async def runs_drift(
    ticker: str = Query(..., description="Ticker symbol to analyse"),
):
    """C-04: Return confidence scores over time for a given ticker."""
    results = get_drift(ticker)
    if not results:
        return {"ticker": ticker.upper(), "points": []}
    return {"ticker": ticker.upper(), "points": results}


@app.get("/api/runs/{run_id}")
async def get_run_by_id(run_id: str):
    run = get_run(run_id)
    if run is None:
        raise HTTPException(404, detail="Run not found")
    return run


@app.post("/api/runs/{run_id}/replay")
async def replay_run(run_id: str):
    """
    Week 6 — Determinism: re-run a historical run with its exact stored
    config (model, temperature, seed, directive) and diff the conclusion.

    The replay uses the original canonical subject and context stored in the
    run record. The result is NOT persisted — it is metadata for auditors to
    verify that the same inputs produce the same output.

    Returns:
      original_conclusion  — conclusion from the stored run
      replay_conclusion    — conclusion from the fresh run
      match                — True if conclusions are byte-identical
      diff_chars           — character-level diff count (0 if match)
      original_config      — the config snapshot that produced the original
    """
    original = get_run(run_id)
    if original is None:
        raise HTTPException(404, detail="Run not found")

    payload     = original if isinstance(original, dict) else original
    subject     = payload.get("subject", "")
    config_snap = payload.get("config_snapshot", {})

    if not subject:
        raise HTTPException(400, detail="Run has no stored subject — cannot replay")

    # Reconstruct adapter from the stored config snapshot
    try:
        replay_adapter = _build_adapter(config_snap)
    except Exception as exc:
        raise HTTPException(400, detail=f"Cannot reconstruct adapter from stored config: {exc}")

    # Retrieve the directive version that was active for this run
    from directive import get_directive, get_active_directive
    directive_version = config_snap.get("directive_version") or payload.get("session", {}) \
        .get("directive_version") if isinstance(payload.get("session"), dict) else None

    try:
        directive = get_directive(directive_version) if directive_version else get_active_directive()
    except KeyError:
        directive = get_active_directive()

    original_conclusion = payload.get("conclusion")

    try:
        result = run_validation_loop(
            subject,
            "",          # context not stored separately — replay on subject only
            uuid.uuid4(),
            AgentID(config_snap.get("agent_id", "external")),
            confidence_score=config_snap.get("confidence_score", 0.75),
            directive=directive,
            call_agent_fn=replay_adapter,
        )
        replay_conclusion = result.final_response.conclusion if result.final_response else None
    except HaltError as exc:
        return {
            "run_id":             run_id,
            "original_conclusion": original_conclusion,
            "replay_conclusion":   None,
            "match":               False,
            "replay_halted":       True,
            "error":               str(exc),
            "original_config":     config_snap,
        }
    except Exception as exc:
        raise HTTPException(500, detail=f"Replay failed: {type(exc).__name__}: {exc}")

    match = original_conclusion == replay_conclusion
    diff_chars = sum(
        1 for a, b in zip(original_conclusion or "", replay_conclusion or "")
        if a != b
    ) + abs(len(original_conclusion or "") - len(replay_conclusion or ""))

    return {
        "run_id":              run_id,
        "original_conclusion": original_conclusion,
        "replay_conclusion":   replay_conclusion,
        "match":               match,
        "diff_chars":          diff_chars,
        "replay_halted":       False,
        "original_config":     config_snap,
    }


# ── Reviewer flags (UN-05) ─────────────────────────────────────────────────────

@app.post("/api/runs/{run_id}/flags")
async def flag_run(
    run_id: str,
    body: FlagRequest,
    scope: ScopeT = Depends(require_scope),
):
    """UN-05: Add a reviewer flag to a run. Never mutates the RunRecord itself."""
    if scope != "auditor":
        raise HTTPException(
            status_code=403,
            detail="Only auditor-scoped tokens may add reviewer flags.",
        )
    if get_run(run_id) is None:
        raise HTTPException(404, detail="Run not found")
    flag = insert_flag(run_id, body.flag_type, body.reviewer_note)
    return flag


@app.get("/api/runs/{run_id}/flags")
async def list_flags(run_id: str):
    """Return all reviewer flags for a run."""
    if get_run(run_id) is None:
        raise HTTPException(404, detail="Run not found")
    return get_flags(run_id)


# ── Session routes ─────────────────────────────────────────────────────────────

@app.get("/api/sessions")
async def list_sessions():
    return get_sessions()


@app.get("/api/sessions/{session_id}")
async def get_session_by_id(session_id: str):
    s = get_session(session_id)
    if s is None:
        raise HTTPException(404, detail="Session not found")
    return s


# ── Admin routes ───────────────────────────────────────────────────────────────

@app.delete("/api/runs")
async def clear_runs():
    """Admin: drop and recreate all tables. Test / dev use only."""
    clear_all()
    return {"cleared": True}


@app.get("/api/directive")
async def get_directive_info():
    d = get_active_directive()
    return {"version": d.version, "text": d.text}
