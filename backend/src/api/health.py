"""
Health check API gateways.
"""

from fastapi import APIRouter
from datetime import datetime, timezone
from ..models.schemas import HealthResponse
from ..common.app_constants import AppConstants
from ..common.api_constants import ApiConstants
from ..common.database_constants import DatabaseConstants

router = APIRouter()

@router.get(AppConstants.HEALTH_ENDPOINT, response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status=ApiConstants.HEALTH_STATUS,
        timestamp=datetime.now(timezone.utc).isoformat(),
        version=AppConstants.APP_VERSION,
        services={
            DatabaseConstants.FIRESTORE_SERVICE: ApiConstants.FIRESTORE_STATUS,
            DatabaseConstants.DETECTOR_SERVICE: ApiConstants.DETECTOR_STATUS,
            DatabaseConstants.RULES_ENGINE_SERVICE: ApiConstants.RULES_ENGINE_STATUS
        }
    )

