"""
FastAPI middleware for request monitoring and metrics collection.
"""

import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from .logger import get_logger
from .monitoring import MonitoringMiddleware

logger = get_logger("monitoring_middleware")


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect request metrics."""
    
    async def dispatch(self, request: Request, call_next):
        """Process request and collect metrics."""
        start_time = time.time()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Collect metrics
            await MonitoringMiddleware.log_request(
                method=request.method,
                endpoint=str(request.url.path),
                duration=duration,
                status_code=response.status_code
            )
            
            return response
            
        except Exception as e:
            # Calculate duration even for errors
            duration = time.time() - start_time
            
            # Log metrics for error
            await MonitoringMiddleware.log_request(
                method=request.method,
                endpoint=str(request.url.path),
                duration=duration,
                status_code=500
            )
            
            logger.error(f"Request failed: {e}")
            raise

