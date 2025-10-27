# Firewall detection and rules package

from .detector import FirewallDetector
from .detection_patterns import (
    DetectionPatternRegistry,
    RiskCategory,
    categorize_risk_type
)

__all__ = [
    'FirewallDetector',
    'DetectionPatternRegistry',
    'RiskCategory',
    'categorize_risk_type'
]
