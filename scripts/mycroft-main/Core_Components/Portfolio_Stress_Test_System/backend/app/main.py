from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.api.routes import analysis, health
from app.api.routes import crash_simulation
from app.api.routes import factor_exposure
from app.api.routes import regime_performance          # ← Layer 4
from app.core.config import settings
from app.core.logging_config import setup_logging

logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Portfolio Stress Testing API — Layers 1–4")
    yield
    logger.info("Shutting down Portfolio Stress Testing API")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description=(
        "Layer 1: Regime-Dependent Diversification  |  "
        "Layer 2: Historical Crash Simulation  |  "
        "Layer 3: Factor Exposure Decomposition  |  "
        "Layer 4: Regime-Specific Performance Analysis"
    ),
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router,              prefix="/health",  tags=["Health"])
app.include_router(analysis.router,            prefix="/api/v1",  tags=["Layer 1 — Regime Analysis"])
app.include_router(crash_simulation.router,    prefix="/api/v1",  tags=["Layer 2 — Crash Simulation"])
app.include_router(factor_exposure.router,     prefix="/api/v1",  tags=["Layer 3 — Factor Exposure"])
app.include_router(regime_performance.router,  prefix="/api/v1",  tags=["Layer 4 — Regime Performance"])

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)