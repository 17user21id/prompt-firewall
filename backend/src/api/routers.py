"""
Main API routers combining all endpoints.
"""

from fastapi import APIRouter
from . import health, tenants, query, rules, logs, prompts, admin

# Create main router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(health.router, tags=["health"])
api_router.include_router(tenants.router, prefix="/v1", tags=["tenants"])
api_router.include_router(query.router, prefix="/v1", tags=["query"])
api_router.include_router(rules.router, prefix="/v1", tags=["rules"])
api_router.include_router(logs.router, prefix="/v1", tags=["logs"])
api_router.include_router(prompts.router, prefix="/v1", tags=["prompts"])
api_router.include_router(admin.router, prefix="/v1", tags=["admin"])

