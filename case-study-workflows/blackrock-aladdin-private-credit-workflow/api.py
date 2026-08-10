"""
Curl-runnable API wrapper — same convention as the JPMorgan reference
implementation in this case study series. No Python editing required to run
a scenario; set your provider and key in .env, start this, and curl it.

Start:
    uvicorn api:app --reload

Then:
    curl -X POST http://localhost:8000/query \\
      -H "Content-Type: application/json" \\
      -d '{"query": "What is our exposure to Example Industrial Holdings, and is leverage elevated?"}'
"""
import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

from src.llm_providers import build_provider
from src.pipeline import build_default_pipeline

load_dotenv()
app = FastAPI(title="Aladdin Private Credit Query Pipeline — Reference Implementation")

_provider_name = os.environ.get("PROVIDER", "claude")
_key_env_var = {
    "claude": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
}.get(_provider_name)
_api_key = os.environ.get(_key_env_var, "")


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    passed: bool
    escalated: bool
    unverified_figures: list
    answer: str


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    llm = build_provider(_provider_name, _api_key)
    pipeline = build_default_pipeline(llm)
    result = await pipeline.run(request.query)
    return QueryResponse(
        passed=result.passed,
        escalated=result.escalated,
        unverified_figures=result.unverified_figures,
        answer=result.verified_draft,
    )


@app.get("/health")
async def health():
    return {"status": "ok", "provider": _provider_name}
