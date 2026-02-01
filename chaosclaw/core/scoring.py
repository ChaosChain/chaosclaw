"""
ChaosClaw Scoring Module

Utilities for calculating and formatting trust scores.
Pure functions, no side effects.
"""

from typing import Optional
from .reputation import AgentTrust, DimensionScore, ReputationDimension


def calculate_average_score(dimensions: list[DimensionScore]) -> int:
    """
    Calculate average score from dimension scores.
    
    Args:
        dimensions: List of dimension scores
    
    Returns:
        Average score (0-100), or 0 if no dimensions
    """
    if not dimensions:
        return 0
    
    total = sum(d.value for d in dimensions)
    return total // len(dimensions)


def trust_bucket(score: int) -> str:
    """
    Categorize a trust score into a human-readable bucket.
    
    Args:
        score: Trust score (0-100)
    
    Returns:
        Bucket name
    """
    if score >= 90:
        return "exceptional"
    elif score >= 70:
        return "high"
    elif score >= 50:
        return "moderate"
    elif score >= 25:
        return "low"
    else:
        return "minimal"


def trust_emoji(score: int) -> str:
    """
    Get an emoji representing the trust level.
    
    Args:
        score: Trust score (0-100)
    
    Returns:
        Emoji string
    """
    if score >= 90:
        return "🟢"  # Green circle - exceptional
    elif score >= 70:
        return "🔵"  # Blue circle - high
    elif score >= 50:
        return "🟡"  # Yellow circle - moderate
    elif score >= 25:
        return "🟠"  # Orange circle - low
    else:
        return "⚪"  # White circle - minimal/new


def format_trust_display(agent: AgentTrust) -> str:
    """
    Format a trust profile for display.
    
    Args:
        agent: Agent trust profile
    
    Returns:
        Formatted string for display
    """
    lines = [
        f"Agent #{agent.agent_id}",
        f"Trust: {agent.average_score}/100 {trust_emoji(agent.average_score)}",
    ]
    
    if agent.dimensions:
        lines.append("Dimensions:")
        for dim in agent.dimensions:
            lines.append(f"  • {dim.dimension.value.capitalize()}: {dim.value}")
    
    if agent.feedback_count > 0:
        lines.append(f"Feedback count: {agent.feedback_count}")
    
    return "\n".join(lines)


def format_tweet(agent: AgentTrust, network: str = "mainnet") -> str:
    """
    Format an agent announcement as a tweet.
    
    Args:
        agent: Agent trust profile
        network: Network name for 8004scan link
    
    Returns:
        Tweet text (under 280 chars)
    """
    emoji = trust_emoji(agent.average_score)
    bucket = trust_bucket(agent.average_score)
    
    # Build dimension summary if available
    dim_summary = ""
    if agent.dimensions:
        dim_parts = [f"{d.dimension.value[:3].upper()}:{d.value}" for d in agent.dimensions[:3]]
        dim_summary = f"\n📊 {' | '.join(dim_parts)}"
    
    # Build tweet
    tweet = f"""🦞 New AI agent verified on ERC-8004!

Agent #{agent.agent_id}
{emoji} Trust: {agent.average_score}/100 ({bucket}){dim_summary}

Verify: /chaoschain verify {agent.agent_id}
🔗 https://8004scan.io/agents/{network}/{agent.agent_id}

#ERC8004 #AIAgents @Ch40sChain"""
    
    # Ensure under 280 chars
    if len(tweet) > 280:
        # Truncate dimension summary if needed
        tweet = f"""🦞 New AI agent verified!

Agent #{agent.agent_id}
{emoji} Trust: {agent.average_score}/100

/chaoschain verify {agent.agent_id}
🔗 8004scan.io/agents/{network}/{agent.agent_id}

#ERC8004 @Ch40sChain"""
    
    return tweet


def format_dimension_bars(agent: AgentTrust) -> str:
    """
    Format dimensions as ASCII progress bars.
    Useful for detailed displays.
    
    Args:
        agent: Agent trust profile
    
    Returns:
        ASCII bar visualization
    """
    if not agent.dimensions:
        return "No reputation data"
    
    lines = []
    for dim in agent.dimensions:
        filled = dim.value // 10
        empty = 10 - filled
        bar = "█" * filled + "░" * empty
        lines.append(f"{dim.dimension.value[:8]:8s} [{bar}] {dim.value:3d}")
    
    return "\n".join(lines)
