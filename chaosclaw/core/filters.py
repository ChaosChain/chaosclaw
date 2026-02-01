"""
ChaosClaw Filter Module

Determines which agents should be announced.
High-signal filtering to avoid noise.
"""

from dataclasses import dataclass
from typing import Callable
from .reputation import AgentTrust


@dataclass
class TrustFilter:
    """Configuration for trust-based filtering."""
    min_trust_score: int = 60  # Minimum average score to announce
    announce_chaoschain_registrations: bool = True  # Always announce if via ChaosChain
    announce_with_any_reputation: bool = True  # Announce if has any feedback
    
    def __call__(self, agent: AgentTrust) -> bool:
        """Check if agent passes filter."""
        return should_announce(agent, self)


def should_announce(agent: AgentTrust, config: TrustFilter = None) -> bool:
    """
    Determine if an agent registration should be announced.
    
    ChaosClaw only announces HIGH-SIGNAL registrations:
    1. Agent was registered via ChaosChain skill
    2. OR agent already has non-zero reputation
    3. OR agent's average trust score >= threshold
    
    Args:
        agent: The agent trust profile
        config: Filter configuration (uses defaults if None)
    
    Returns:
        True if the agent should be announced
    """
    if config is None:
        config = TrustFilter()
    
    # Rule 1: Always announce ChaosChain registrations
    if config.announce_chaoschain_registrations and agent.registered_via_chaoschain:
        return True
    
    # Rule 2: Announce if agent has any reputation
    if config.announce_with_any_reputation and agent.has_reputation:
        return True
    
    # Rule 3: Announce if trust score meets threshold
    if agent.average_score >= config.min_trust_score:
        return True
    
    return False


def is_chaoschain_registration(tx_data: dict) -> bool:
    """
    Detect if a registration came via ChaosChain skill.
    
    Detection methods:
    1. Check if tx sender is a known ChaosChain address
    2. Check for ChaosChain-specific metadata in tx input
    3. Check for specific registration patterns
    
    Args:
        tx_data: Transaction data from the blockchain
    
    Returns:
        True if registration appears to be from ChaosChain
    """
    # Known ChaosChain-related addresses (could be expanded)
    # For now, this is a placeholder - real detection would need
    # more sophisticated analysis
    chaoschain_markers = [
        "chaoschain",
        "0xCHAOS",  # If we ever deploy a known address
    ]
    
    # Check tx input data for markers (if available)
    input_data = tx_data.get("input", "")
    if isinstance(input_data, str):
        input_lower = input_data.lower()
        for marker in chaoschain_markers:
            if marker.lower() in input_lower:
                return True
    
    # Check for metadata URI containing chaoschain
    uri = tx_data.get("uri", "")
    if isinstance(uri, str) and "chaoschain" in uri.lower():
        return True
    
    return False


def filter_by_score_bucket(agent: AgentTrust, bucket: str) -> bool:
    """
    Filter by trust bucket.
    
    Buckets:
    - "exceptional": 90-100
    - "high": 70-89
    - "moderate": 50-69
    - "low": 25-49
    - "minimal": 0-24
    """
    score = agent.average_score
    
    if bucket == "exceptional":
        return score >= 90
    elif bucket == "high":
        return 70 <= score < 90
    elif bucket == "moderate":
        return 50 <= score < 70
    elif bucket == "low":
        return 25 <= score < 50
    elif bucket == "minimal":
        return score < 25
    
    return False
