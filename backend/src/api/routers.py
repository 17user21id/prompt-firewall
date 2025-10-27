"""
Main API routers combining all endpoints.
"""

from fastapi import APIRouter
from . import health, tenants, query, rules, logs, prompts, metrics


# Create main router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(health.router, tags=["health"])
api_router.include_router(metrics.router, tags=["monitoring"])
api_router.include_router(tenants.router, prefix="/v1", tags=["tenants"])
api_router.include_router(query.router, prefix="/v1", tags=["query"])
api_router.include_router(rules.router, tags=["rules"])  # Removed /v1 prefix
api_router.include_router(logs.router, tags=["logs"])  # Removed /v1 prefix
api_router.include_router(prompts.router, prefix="/v1", tags=["prompts"])

