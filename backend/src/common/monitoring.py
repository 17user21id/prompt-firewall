"""
Monitoring and observability configuration for Prompt Firewall.
Integrates with GCP Cloud Monitoring and provides Prometheus metrics.

This module provides monitoring capabilities that can be enabled by setting
the environment variable ENABLE_METRICS_COLLECTION=true.

Features:
    - Prometheus metrics collection
    - Request tracking via middleware
    - PII and injection detection metrics
    - GCP Cloud Monitoring integration (optional)
"""

import os
from typing import Dict, Any
from prometheus_client import Counter, Histogram, Gauge
import logging

# Optional imports for GCP Cloud Monitoring
try:
    from google.cloud import monitoring_v3
    from google.cloud.monitoring import MetricServiceClient
    GCP_MONITORING_AVAILABLE = True
except ImportError:
    GCP_MONITORING_AVAILABLE = False
    monitoring_v3 = None
    MetricServiceClient = None

logger = logging.getLogger(__name__)

# Prometheus Metrics
firewall_requests_total = Counter(
    'firewall_requests_total',
    'Total number of firewall requests',
    ['method', 'endpoint', 'status']
)

firewall_request_duration = Histogram(
    'firewall_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

firewall_pii_detections_total = Counter(
    'firewall_pii_detections_total',
    'Total PII detections',
    ['type', 'severity']
)

firewall_injection_detections_total = Counter(
    'firewall_injection_detections_total',
    'Total prompt injection detections',
    ['type', 'severity']
)

firewall_active_connections = Gauge(
    'firewall_active_connections',
    'Number of active connections'
)

firewall_queue_size = Gauge(
    'firewall_queue_size',
    'Size of request queue'
)


class CloudMonitoring:
    """Google Cloud Monitoring integration."""
    
    def __init__(self, project_id: str):
        if not GCP_MONITORING_AVAILABLE:
            raise ImportError("google-cloud-monitoring package is not installed")
        
        self.project_id = project_id
        self.client = MetricServiceClient()
        self.project_name = f"projects/{project_id}"
    
    def write_metric(
        self,
        metric_type: str,
        value: float,
        labels: Dict[str, str]
    ):
        """Write custom metric to Cloud Monitoring."""
        try:
            series = monitoring_v3.TimeSeries()
            series.metric.type = f"custom.googleapis.com/{metric_type}"
            
            for key, val in labels.items():
                series.metric.labels[key] = str(val)
            
            point = monitoring_v3.Point()
            point.value.double_value = value
            
            from time import time
            from google.protobuf import timestamp_pb2
            point.interval.end_time.seconds = int(time())
            
            series.points = [point]
            
            self.client.create_time_series(
                name=self.project_name,
                time_series=[series]
            )
        except Exception as e:
            logger.error(f"Failed to write metric: {e}")
    
    def log_firewall_event(
        self,
        event_type: str,
        details: Dict[str, Any]
    ):
        """Log firewall event to Cloud Monitoring."""
        self.write_metric(
            "firewall/events",
            1.0,
            {
                "event_type": event_type,
                **{k: str(v) for k, v in details.items()}
            }
        )


class MonitoringMiddleware:
    """Middleware for request monitoring."""
    
    @staticmethod
    async def log_request(
        method: str,
        endpoint: str,
        duration: float,
        status_code: int
    ):
        """Log request metrics."""
        firewall_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=str(status_code)
        ).inc()
        
        firewall_request_duration.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    @staticmethod
    def log_pii_detection(pii_type: str, severity: str):
        """Log PII detection."""
        firewall_pii_detections_total.labels(
            type=pii_type,
            severity=severity
        ).inc()
    
    @staticmethod
    def log_injection_detection(injection_type: str, severity: str):
        """Log prompt injection detection."""
        firewall_injection_detections_total.labels(
            type=injection_type,
            severity=severity
        ).inc()


def get_monitoring_client(project_id: str = None) -> CloudMonitoring:
    """Get or create monitoring client."""
    if project_id is None:
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    
    if not project_id:
        logger.warning("No project ID provided for monitoring")
        return None
    
    return CloudMonitoring(project_id)


def enable_metrics_collection():
    """Enable metrics collection endpoint."""
    from prometheus_client import make_asgi_app
    
    metrics_app = make_asgi_app()
    return metrics_app


def get_health_metrics() -> Dict[str, Any]:
    """Get current health metrics."""
    return {
        "active_connections": firewall_active_connections._value._value,
        "queue_size": firewall_queue_size._value._value,
        "requests_total": firewall_requests_total._value._value,
    }

