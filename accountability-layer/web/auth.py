"""
SEC-02 — JWT Authentication
Issues and validates Bearer tokens carrying scope claims.

Scopes:
  auditor  — full record including thought_log (internal tier)
  investor — structurally excludes thought_log, raw_output, llm_tokens

Token issuance:
  POST /api/auth/token  { "scope": "auditor"|"investor" }
  Returns { "access_token": "<jwt>", "token_type": "bearer", "scope": "..." }

  In production the endpoint should require an admin credential (e.g. API key).
  For the Phase 1 prototype it accepts any request so the test UI can self-serve
  a token without a separate identity system.  The placeholder is clearly marked
  with a TODO so it can't be accidentally shipped.

Validation:
  FastAPI dependency  require_scope()  is injected into protected routes.
  It reads Authorization: Bearer <token>, verifies the signature, and returns
  the decoded scope string.  Missing / invalid / expired tokens → 401.

Secret:
  Read from ACCOUNTABILITY_SECRET env var.  Falls back to a hard-coded dev
  secret that is intentionally obvious so it cannot be mistaken for production.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Literal

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# ── Secret ─────────────────────────────────────────────────────────────────────

_DEV_SECRET = "dev-only-not-for-production-change-via-ACCOUNTABILITY_SECRET"
_ALGORITHM  = "HS256"
_TTL_HOURS  = 8

ScopeT = Literal["auditor", "investor"]

_bearer_scheme = HTTPBearer(auto_error=False)


def _secret() -> str:
    return os.environ.get("ACCOUNTABILITY_SECRET", _DEV_SECRET)


# ── Issue ──────────────────────────────────────────────────────────────────────

def issue_token(scope: ScopeT) -> str:
    """
    Create a signed JWT carrying the requested scope.

    TODO (SEC-02 production hardening): verify caller identity before issuing
    an auditor-scoped token.  In production, require an admin API key or SSO
    credential in the request before calling this function.
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub":   "accountability-layer-user",
        "scope": scope,
        "iat":   now,
        "exp":   now + timedelta(hours=_TTL_HOURS),
    }
    return jwt.encode(payload, _secret(), algorithm=_ALGORITHM)


# ── Validate ───────────────────────────────────────────────────────────────────

def _decode(token: str) -> dict:
    try:
        return jwt.decode(token, _secret(), algorithms=[_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Request a new token from POST /api/auth/token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_scope(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> ScopeT:
    """
    FastAPI dependency.  Validates the Bearer token and returns the scope claim.
    Inject into any route that needs SEC-01 scope enforcement.

    Usage:
        @app.post("/api/chat")
        async def chat(scope: ScopeT = Depends(require_scope)):
            ...
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header. Include 'Authorization: Bearer <token>'.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    claims = _decode(credentials.credentials)
    scope  = claims.get("scope")
    if scope not in ("auditor", "investor"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Token carries unknown scope {scope!r}. Must be 'auditor' or 'investor'.",
        )
    return scope  # type: ignore[return-value]
