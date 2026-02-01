"""
X (Twitter) Publisher

Posts agent announcements to X/Twitter.
Includes rate limiting and dry-run mode.
"""

import asyncio
import time
from collections import deque
from typing import Optional
import structlog
import tweepy

from ..config import TwitterConfig
from ..core.reputation import AgentTrust
from ..core.scoring import format_tweet


logger = structlog.get_logger(__name__)


class XPoster:
    """
    Posts agent announcements to X/Twitter.
    
    Features:
    - Rate limiting (configurable tweets per hour)
    - Dry-run mode for testing
    - Async-compatible
    """
    
    def __init__(
        self,
        config: TwitterConfig,
        max_tweets_per_hour: int = 10,
        dry_run: bool = False,
        network: str = "mainnet",
    ):
        """
        Initialize the X poster.
        
        Args:
            config: Twitter API configuration
            max_tweets_per_hour: Rate limit
            dry_run: If True, log but don't post
            network: Network name for 8004scan links
        """
        self.config = config
        self.max_tweets_per_hour = max_tweets_per_hour
        self.dry_run = dry_run
        self.network = network
        
        # Rate limiting: track timestamps of recent tweets
        self.recent_tweets: deque[float] = deque(maxlen=max_tweets_per_hour)
        
        # Initialize Twitter client
        self.client: Optional[tweepy.Client] = None
        if config.is_configured and not dry_run:
            try:
                self.client = tweepy.Client(
                    consumer_key=config.api_key,
                    consumer_secret=config.api_secret,
                    access_token=config.access_token,
                    access_token_secret=config.access_secret,
                )
                logger.info("x_poster_initialized", dry_run=dry_run)
            except Exception as e:
                logger.error("x_poster_init_failed", error=str(e))
                self.client = None
        else:
            logger.info(
                "x_poster_initialized",
                dry_run=dry_run,
                configured=config.is_configured,
            )
    
    async def post(self, agent: AgentTrust) -> bool:
        """
        Post an agent announcement to X.
        
        Args:
            agent: The agent to announce
        
        Returns:
            True if posted (or would post in dry-run), False if rate limited
        """
        # Check rate limit
        if not self._check_rate_limit():
            logger.warning(
                "x_poster_rate_limited",
                agent_id=agent.agent_id,
                recent_count=len(self.recent_tweets),
            )
            return False
        
        # Format tweet
        tweet = format_tweet(agent, network=self.network)
        
        # Log the tweet
        logger.info(
            "x_poster_posting",
            agent_id=agent.agent_id,
            average_score=agent.average_score,
            dry_run=self.dry_run,
            tweet_length=len(tweet),
        )
        
        if self.dry_run:
            # In dry-run mode, just log and return success
            logger.info(
                "x_poster_dry_run",
                tweet=tweet,
            )
            self._record_tweet()
            return True
        
        if self.client is None:
            logger.error("x_poster_no_client", agent_id=agent.agent_id)
            return False
        
        # Post to X
        try:
            # Run in executor since tweepy is sync
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.create_tweet(text=tweet),
            )
            
            tweet_id = response.data.get("id") if response.data else None
            
            logger.info(
                "x_poster_success",
                agent_id=agent.agent_id,
                tweet_id=tweet_id,
            )
            
            self._record_tweet()
            return True
            
        except tweepy.TweepyException as e:
            logger.error(
                "x_poster_failed",
                agent_id=agent.agent_id,
                error=str(e),
            )
            return False
    
    def _check_rate_limit(self) -> bool:
        """
        Check if we're within rate limits.
        
        Returns:
            True if we can post, False if rate limited
        """
        now = time.time()
        hour_ago = now - 3600
        
        # Remove tweets older than 1 hour
        while self.recent_tweets and self.recent_tweets[0] < hour_ago:
            self.recent_tweets.popleft()
        
        # Check if we're at the limit
        return len(self.recent_tweets) < self.max_tweets_per_hour
    
    def _record_tweet(self) -> None:
        """Record a tweet timestamp for rate limiting."""
        self.recent_tweets.append(time.time())
    
    @property
    def tweets_remaining(self) -> int:
        """Get remaining tweets in current rate limit window."""
        now = time.time()
        hour_ago = now - 3600
        
        # Remove old tweets
        while self.recent_tweets and self.recent_tweets[0] < hour_ago:
            self.recent_tweets.popleft()
        
        return max(0, self.max_tweets_per_hour - len(self.recent_tweets))


class MockXPoster(XPoster):
    """
    Mock X poster for testing.
    Records all posts without actually posting.
    """
    
    def __init__(self, **kwargs):
        """Initialize with dry_run always True."""
        super().__init__(
            config=TwitterConfig(
                api_key="mock",
                api_secret="mock",
                access_token="mock",
                access_secret="mock",
            ),
            dry_run=True,
            **kwargs,
        )
        self.posted: list[AgentTrust] = []
    
    async def post(self, agent: AgentTrust) -> bool:
        """Record the post."""
        result = await super().post(agent)
        if result:
            self.posted.append(agent)
        return result
