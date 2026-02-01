"""
Tests for ChaosClaw filter logic.

These tests verify the high-signal filtering behavior.
"""

import pytest
from chaosclaw.core.reputation import AgentTrust, DimensionScore, ReputationDimension
from chaosclaw.core.filters import TrustFilter, should_announce, filter_by_score_bucket
from chaosclaw.core.scoring import (
    calculate_average_score,
    trust_bucket,
    trust_emoji,
    format_tweet,
)


class TestTrustFilter:
    """Tests for should_announce logic."""
    
    def test_announces_chaoschain_registration(self):
        """Agents registered via ChaosChain should always be announced."""
        agent = AgentTrust(
            agent_id=1,
            owner="0x1234",
            average_score=0,
            has_reputation=False,
            registered_via_chaoschain=True,
        )
        
        assert should_announce(agent) is True
    
    def test_announces_agent_with_reputation(self):
        """Agents with any reputation should be announced."""
        agent = AgentTrust(
            agent_id=2,
            owner="0x1234",
            average_score=30,
            has_reputation=True,
            registered_via_chaoschain=False,
        )
        
        assert should_announce(agent) is True
    
    def test_announces_high_trust_agent(self):
        """Agents meeting trust threshold should be announced."""
        agent = AgentTrust(
            agent_id=3,
            owner="0x1234",
            average_score=75,
            has_reputation=False,
            registered_via_chaoschain=False,
        )
        
        config = TrustFilter(min_trust_score=60)
        assert should_announce(agent, config) is True
    
    def test_filters_low_trust_agent(self):
        """Agents below threshold with no reputation should be filtered."""
        agent = AgentTrust(
            agent_id=4,
            owner="0x1234",
            average_score=30,
            has_reputation=False,
            registered_via_chaoschain=False,
        )
        
        config = TrustFilter(
            min_trust_score=60,
            announce_with_any_reputation=False,  # Disable this rule
        )
        assert should_announce(agent, config) is False
    
    def test_custom_threshold(self):
        """Custom trust threshold should be respected."""
        agent = AgentTrust(
            agent_id=5,
            owner="0x1234",
            average_score=85,
            has_reputation=False,
            registered_via_chaoschain=False,
        )
        
        # With threshold of 90, should filter
        high_config = TrustFilter(
            min_trust_score=90,
            announce_chaoschain_registrations=False,
            announce_with_any_reputation=False,
        )
        assert should_announce(agent, high_config) is False
        
        # With threshold of 80, should pass
        low_config = TrustFilter(
            min_trust_score=80,
            announce_chaoschain_registrations=False,
            announce_with_any_reputation=False,
        )
        assert should_announce(agent, low_config) is True


class TestScoring:
    """Tests for scoring utilities."""
    
    def test_calculate_average(self):
        """Average calculation should work correctly."""
        dims = [
            DimensionScore(ReputationDimension.QUALITY, 80, 80),
            DimensionScore(ReputationDimension.RELIABILITY, 90, 90),
            DimensionScore(ReputationDimension.SPEED, 70, 70),
        ]
        
        avg = calculate_average_score(dims)
        assert avg == 80  # (80 + 90 + 70) / 3 = 80
    
    def test_calculate_average_empty(self):
        """Empty dimensions should return 0."""
        assert calculate_average_score([]) == 0
    
    def test_trust_buckets(self):
        """Trust buckets should be assigned correctly."""
        assert trust_bucket(95) == "exceptional"
        assert trust_bucket(90) == "exceptional"
        assert trust_bucket(75) == "high"
        assert trust_bucket(70) == "high"
        assert trust_bucket(55) == "moderate"
        assert trust_bucket(50) == "moderate"
        assert trust_bucket(35) == "low"
        assert trust_bucket(25) == "low"
        assert trust_bucket(10) == "minimal"
        assert trust_bucket(0) == "minimal"
    
    def test_trust_emoji(self):
        """Trust emojis should match buckets."""
        assert trust_emoji(95) == "🟢"
        assert trust_emoji(75) == "🔵"
        assert trust_emoji(55) == "🟡"
        assert trust_emoji(35) == "🟠"
        assert trust_emoji(10) == "⚪"


class TestTweetFormatting:
    """Tests for tweet formatting."""
    
    def test_format_tweet_basic(self):
        """Basic tweet should be well-formed."""
        agent = AgentTrust(
            agent_id=542,
            owner="0x1234",
            average_score=87,
        )
        
        tweet = format_tweet(agent)
        
        assert "Agent #542" in tweet
        assert "87/100" in tweet
        assert "/chaoschain verify 542" in tweet
        assert "8004scan.io" in tweet
        assert len(tweet) <= 280
    
    def test_format_tweet_with_dimensions(self):
        """Tweet with dimensions should include summary."""
        agent = AgentTrust(
            agent_id=123,
            owner="0x1234",
            average_score=75,
            quality=DimensionScore(ReputationDimension.QUALITY, 80, 80),
            reliability=DimensionScore(ReputationDimension.RELIABILITY, 70, 70),
        )
        
        tweet = format_tweet(agent)
        
        # Should include some dimension info
        assert "Agent #123" in tweet
        assert len(tweet) <= 280
    
    def test_format_tweet_respects_length(self):
        """Tweet should never exceed 280 characters."""
        agent = AgentTrust(
            agent_id=999999,
            owner="0x" + "1" * 40,
            average_score=100,
            quality=DimensionScore(ReputationDimension.QUALITY, 100, 100),
            reliability=DimensionScore(ReputationDimension.RELIABILITY, 100, 100),
            speed=DimensionScore(ReputationDimension.SPEED, 100, 100),
            safety=DimensionScore(ReputationDimension.SAFETY, 100, 100),
            alignment=DimensionScore(ReputationDimension.ALIGNMENT, 100, 100),
        )
        
        tweet = format_tweet(agent)
        assert len(tweet) <= 280


class TestFilterByBucket:
    """Tests for bucket-based filtering."""
    
    def test_filter_exceptional(self):
        """Exceptional filter should work."""
        high = AgentTrust(agent_id=1, owner="0x", average_score=95)
        low = AgentTrust(agent_id=2, owner="0x", average_score=50)
        
        assert filter_by_score_bucket(high, "exceptional") is True
        assert filter_by_score_bucket(low, "exceptional") is False
    
    def test_filter_high(self):
        """High filter should work."""
        agent = AgentTrust(agent_id=1, owner="0x", average_score=75)
        
        assert filter_by_score_bucket(agent, "high") is True
        assert filter_by_score_bucket(agent, "exceptional") is False
