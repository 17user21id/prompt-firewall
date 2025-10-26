"""
FastAPI main application for Prompt Firewall MVP.
Simplified main file that uses routers from api/ folder.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from datetime import datetime

from .common.app_constants import AppConstants
from .common.api_constants import ApiConstants
from .common.logger import get_logger
from .models.schemas import ErrorResponse
from .api.routers import api_router

# Initialize FastAPI app
app = FastAPI(
    title=AppConstants.APP_NAME,
    description=AppConstants.APP_DESCRIPTION,
    version=AppConstants.APP_VERSION,
    docs_url=AppConstants.DOCS_URL,
    redoc_url=AppConstants.REDOC_URL
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=AppConstants.CORS_ALLOW_ORIGINS,
    allow_credentials=AppConstants.CORS_ALLOW_CREDENTIALS,
    allow_methods=AppConstants.CORS_ALLOW_METHODS,
    allow_headers=AppConstants.CORS_ALLOW_HEADERS,
)

# Initialize logger
logger = get_logger("main")
logger.info("Prompt Firewall API starting up")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    return JSONResponse(
        status_code=ApiConstants.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error=ApiConstants.INTERNAL_SERVER_ERROR,
            message=str(exc),
            timestamp=datetime.utcnow().isoformat()
        ).dict()
    )

# Include API routers
app.include_router(api_router)

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Prompt Firewall API",
        version="1.0.0",
        description="AI Security Firewall for detecting PII and prompt injection attempts",
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "API key in format: tenant_id:api_key"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

