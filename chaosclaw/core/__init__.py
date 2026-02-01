"""
ChaosClaw Core Module

Isolated, auditable trust logic.
This module contains NO I/O, NO network calls, NO side effects.
Pure functions for trust evaluation.
"""

from .reputation import AgentTrust, ReputationDimension
from .filters import should_announce, TrustFilter
from .scoring import calculate_average_score, trust_bucket, format_trust_display

__all__ = [
    "AgentTrust",
    "ReputationDimension",
    "should_announce",
    "TrustFilter",
    "calculate_average_score",
    "trust_bucket",
    "format_trust_display",
]
