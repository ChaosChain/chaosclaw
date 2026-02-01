"""
ChaosClaw Configuration
Loads settings from environment variables with sensible defaults.
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()


@dataclass
class EthereumConfig:
    """Ethereum network configuration."""
    mainnet_rpc_url: str
    sepolia_rpc_url: Optional[str]
    network: str  # "mainnet" or "sepolia"
    
    # ERC-8004 Contract Addresses
    MAINNET_IDENTITY_REGISTRY = "0x8004A169FB4a3325136EB29fA0ceB6D2e539a432"
    MAINNET_REPUTATION_REGISTRY = "0x8004BAa17C55a88189AE136b182e5fdA19dE9b63"
    SEPOLIA_IDENTITY_REGISTRY = "0x8004A818BFB912233c491871b3d84c89A494BD9e"
    SEPOLIA_REPUTATION_REGISTRY = "0x8004B663056A597Dffe9eCcC1965A193B7388713"
    
    @property
    def rpc_url(self) -> str:
        """Get the RPC URL for the configured network."""
        if self.network == "sepolia":
            return self.sepolia_rpc_url or self.mainnet_rpc_url
        return self.mainnet_rpc_url
    
    @property
    def identity_registry_address(self) -> str:
        """Get the IdentityRegistry address for the configured network."""
        if self.network == "sepolia":
            return self.SEPOLIA_IDENTITY_REGISTRY
        return self.MAINNET_IDENTITY_REGISTRY
    
    @property
    def reputation_registry_address(self) -> str:
        """Get the ReputationRegistry address for the configured network."""
        if self.network == "sepolia":
            return self.SEPOLIA_REPUTATION_REGISTRY
        return self.MAINNET_REPUTATION_REGISTRY


@dataclass
class TwitterConfig:
    """Twitter/X API configuration."""
    api_key: str
    api_secret: str
    access_token: str
    access_secret: str
    bearer_token: Optional[str] = None
    
    @property
    def is_configured(self) -> bool:
        """Check if Twitter credentials are configured."""
        return all([
            self.api_key,
            self.api_secret,
            self.access_token,
            self.access_secret
        ])


@dataclass
class ClawConfig:
    """ChaosClaw behavior configuration."""
    min_trust_score: int  # Minimum score to announce (0-100)
    poll_interval: int  # Seconds between polls
    max_tweets_per_hour: int  # Rate limit
    dry_run: bool  # If True, log but don't post
    log_level: str


@dataclass
class Config:
    """Main configuration container."""
    ethereum: EthereumConfig
    twitter: TwitterConfig
    claw: ClawConfig
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls(
            ethereum=EthereumConfig(
                mainnet_rpc_url=os.getenv("ETH_MAINNET_RPC_URL", ""),
                sepolia_rpc_url=os.getenv("ETH_SEPOLIA_RPC_URL"),
                network=os.getenv("CHAOSCLAW_NETWORK", "mainnet"),
            ),
            twitter=TwitterConfig(
                api_key=os.getenv("TWITTER_API_KEY", ""),
                api_secret=os.getenv("TWITTER_API_SECRET", ""),
                access_token=os.getenv("TWITTER_ACCESS_TOKEN", ""),
                access_secret=os.getenv("TWITTER_ACCESS_SECRET", ""),
                bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
            ),
            claw=ClawConfig(
                min_trust_score=int(os.getenv("CHAOSCLAW_MIN_TRUST_SCORE", "60")),
                poll_interval=int(os.getenv("CHAOSCLAW_POLL_INTERVAL", "60")),
                max_tweets_per_hour=int(os.getenv("CHAOSCLAW_MAX_TWEETS_PER_HOUR", "10")),
                dry_run=os.getenv("CHAOSCLAW_DRY_RUN", "false").lower() == "true",
                log_level=os.getenv("CHAOSCLAW_LOG_LEVEL", "INFO"),
            ),
        )
    
    def validate(self) -> list[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        if not self.ethereum.mainnet_rpc_url:
            errors.append("ETH_MAINNET_RPC_URL is required")
        
        if not self.claw.dry_run and not self.twitter.is_configured:
            errors.append("Twitter API credentials required (or set CHAOSCLAW_DRY_RUN=true)")
        
        return errors


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config.from_env()
    return _config
