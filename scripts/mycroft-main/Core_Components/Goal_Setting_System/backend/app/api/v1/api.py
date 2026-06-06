"""
API v1 Router
Combines all endpoint routers
"""
from fastapi import APIRouter

from app.api.v1.endpoints import health, goals, simulation

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    health.router,
    tags=["Health"]
)

api_router.include_router(
    goals.router,
    prefix="/goals",
    tags=["Goal Extraction"]
)

api_router.include_router(
    simulation.router,
    prefix="/simulation",
    tags=["Portfolio Simulation"]
)