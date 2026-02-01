"""
ChaosClaw Reputation Module

Data models and normalization for ERC-8004 reputation data.
This module defines the trust data structures used throughout ChaosClaw.
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class ReputationDimension(Enum):
    """
    The 5 dimensions of Proof of Agency reputation.
    These map to ChaosChain's multi-dimensional scoring system.
    """
    QUALITY = "quality"           # Output quality (0-100)
    RELIABILITY = "reliability"   # Task completion rate (0-100)
    SPEED = "speed"               # Response time (0-100)
    SAFETY = "safety"             # Safety compliance (0-100)
    ALIGNMENT = "alignment"       # Goal alignment (0-100)


@dataclass
class DimensionScore:
    """Score for a single reputation dimension."""
    dimension: ReputationDimension
    value: int  # 0-100 normalized
    raw_value: int  # Original value from contract
    decimals: int = 0  # Value decimals from ERC-8004
    
    @classmethod
    def from_contract(cls, dimension: ReputationDimension, raw_value: int, decimals: int = 0) -> "DimensionScore":
        """
        Create from raw contract value.
        Normalizes to 0-100 scale.
        """
        # If decimals > 0, scale down
        if decimals > 0:
            normalized = raw_value // (10 ** decimals)
        else:
            normalized = raw_value
        
        # Clamp to 0-100
        normalized = max(0, min(100, normalized))
        
        return cls(
            dimension=dimension,
            value=normalized,
            raw_value=raw_value,
            decimals=decimals,
        )


@dataclass
class AgentTrust:
    """
    Complete trust profile for an agent.
    This is the canonical data structure used throughout ChaosClaw.
    """
    agent_id: int
    owner: str  # Ethereum address
    uri: Optional[str] = None  # Agent metadata URI
    
    # 5-dimension scores
    quality: Optional[DimensionScore] = None
    reliability: Optional[DimensionScore] = None
    speed: Optional[DimensionScore] = None
    safety: Optional[DimensionScore] = None
    alignment: Optional[DimensionScore] = None
    
    # Aggregates
    feedback_count: int = 0
    average_score: int = 0  # 0-100
    
    # Metadata
    registered_at_block: Optional[int] = None
    tx_hash: Optional[str] = None
    
    # Flags
    has_reputation: bool = False
    registered_via_chaoschain: bool = False
    
    @property
    def dimensions(self) -> list[DimensionScore]:
        """Get all non-None dimension scores."""
        dims = [
            self.quality,
            self.reliability,
            self.speed,
            self.safety,
            self.alignment,
        ]
        return [d for d in dims if d is not None]
    
    @property
    def is_verified(self) -> bool:
        """Agent is considered verified if they have any reputation."""
        return self.has_reputation or self.feedback_count > 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "agent_id": self.agent_id,
            "owner": self.owner,
            "uri": self.uri,
            "average_score": self.average_score,
            "feedback_count": self.feedback_count,
            "has_reputation": self.has_reputation,
            "registered_via_chaoschain": self.registered_via_chaoschain,
            "dimensions": {
                d.dimension.value: d.value
                for d in self.dimensions
            },
        }


def create_agent_trust_from_sdk(
    agent_id: int,
    owner: str,
    reputation_data: Optional[dict] = None,
    tx_hash: Optional[str] = None,
    block_number: Optional[int] = None,
) -> AgentTrust:
    """
    Create AgentTrust from ChaosChain SDK reputation data.
    
    Args:
        agent_id: ERC-8004 agent ID
        owner: Owner address
        reputation_data: Output from chaoschain_sdk.get_reputation()
        tx_hash: Registration transaction hash
        block_number: Registration block number
    
    Returns:
        AgentTrust instance
    """
    agent = AgentTrust(
        agent_id=agent_id,
        owner=owner,
        tx_hash=tx_hash,
        registered_at_block=block_number,
    )
    
    if reputation_data:
        # Map SDK reputation data to dimensions
        dimension_map = {
            "quality": ReputationDimension.QUALITY,
            "reliability": ReputationDimension.RELIABILITY,
            "speed": ReputationDimension.SPEED,
            "safety": ReputationDimension.SAFETY,
            "alignment": ReputationDimension.ALIGNMENT,
        }
        
        for key, dim in dimension_map.items():
            if key in reputation_data and reputation_data[key] is not None:
                score = DimensionScore.from_contract(
                    dimension=dim,
                    raw_value=reputation_data[key],
                    decimals=reputation_data.get(f"{key}_decimals", 0),
                )
                setattr(agent, key, score)
        
        agent.feedback_count = reputation_data.get("feedback_count", 0)
        agent.average_score = reputation_data.get("average", 0)
        agent.has_reputation = agent.feedback_count > 0 or agent.average_score > 0
    
    return agent
