"""
Metrics endpoint for Prometheus monitoring.
"""

from fastapi import APIRouter
from prometheus_client import generate_latest, REGISTRY
from starlette.responses import Response

router = APIRouter()

@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(REGISTRY),
        media_type="text/plain"
    )

