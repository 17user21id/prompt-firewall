"""
Prometheus metrics endpoint for monitoring.
This endpoint provides Prometheus-compatible metrics.
"""

import os
from fastapi import APIRouter
from fastapi.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from ..common.config_constants import ConfigConstants

router = APIRouter()

@router.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint.
    Exposes application metrics in Prometheus format.
    
    Returns:
        Response: Prometheus metrics data
    """
    if os.getenv(ConfigConstants.ENABLE_METRICS_COLLECTION_ENV, "false").lower() == "true":
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )
    return Response(
        status_code=404,
        content="Metrics collection not enabled. Set ENABLE_METRICS_COLLECTION=true"
    )

