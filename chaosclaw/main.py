"""
ChaosClaw Main Entry Point

The Trust Sentinel for AI Agents.
Watches ERC-8004, filters for high-signal registrations, announces on X.
"""

import asyncio
import sys
import structlog

from .config import get_config
from .core.filters import TrustFilter, should_announce
from .listeners.erc8004_watcher import ERC8004Watcher
from .publishers.x_poster import XPoster


# Configure structured logging
import logging
import os

log_level = os.getenv("CHAOSCLAW_LOG_LEVEL", "INFO").upper()
logging.basicConfig(format="%(message)s", level=getattr(logging, log_level, logging.INFO))

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.dev.ConsoleRenderer(colors=True),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


async def run_chaosclaw():
    """
    Main ChaosClaw loop.
    
    1. Watch ERC-8004 for new registrations
    2. Filter for high-signal agents
    3. Announce on X
    """
    # Load config
    config = get_config()
    
    # Validate
    errors = config.validate()
    if errors:
        for error in errors:
            logger.error("config_error", message=error)
        sys.exit(1)
    
    logger.info(
        "chaosclaw_starting",
        network=config.ethereum.network,
        min_trust_score=config.claw.min_trust_score,
        dry_run=config.claw.dry_run,
    )
    
    # Initialize components
    watcher = ERC8004Watcher(
        config=config.ethereum,
        poll_interval=config.claw.poll_interval,
    )
    
    poster = XPoster(
        config=config.twitter,
        max_tweets_per_hour=config.claw.max_tweets_per_hour,
        dry_run=config.claw.dry_run,
        network=config.ethereum.network,
    )
    
    trust_filter = TrustFilter(
        min_trust_score=config.claw.min_trust_score,
    )
    
    # Stats
    total_seen = 0
    total_announced = 0
    total_filtered = 0
    
    logger.info("chaosclaw_watching", message="🦞 ChaosClaw is now watching the network...")
    
    # Main loop
    async for agent in watcher.watch():
        total_seen += 1
        
        # Apply filter
        if should_announce(agent, trust_filter):
            logger.info(
                "chaosclaw_announcing",
                agent_id=agent.agent_id,
                average_score=agent.average_score,
                has_reputation=agent.has_reputation,
                registered_via_chaoschain=agent.registered_via_chaoschain,
            )
            
            # Post to X
            success = await poster.post(agent)
            
            if success:
                total_announced += 1
                logger.info(
                    "chaosclaw_announced",
                    agent_id=agent.agent_id,
                    total_announced=total_announced,
                )
            else:
                logger.warning(
                    "chaosclaw_announce_failed",
                    agent_id=agent.agent_id,
                )
        else:
            total_filtered += 1
            logger.debug(
                "chaosclaw_filtered",
                agent_id=agent.agent_id,
                average_score=agent.average_score,
                reason="below_threshold",
            )
        
        # Log stats periodically
        if total_seen % 10 == 0:
            logger.info(
                "chaosclaw_stats",
                total_seen=total_seen,
                total_announced=total_announced,
                total_filtered=total_filtered,
                tweets_remaining=poster.tweets_remaining,
            )


def main():
    """Entry point."""
    print("""
    ╔═══════════════════════════════════════════╗
    ║                                           ║
    ║     🦞 ChaosClaw - Trust Sentinel 🦞      ║
    ║                                           ║
    ║   Watching ERC-8004 for trusted agents    ║
    ║                                           ║
    ╚═══════════════════════════════════════════╝
    """)
    
    try:
        asyncio.run(run_chaosclaw())
    except KeyboardInterrupt:
        logger.info("chaosclaw_shutdown", message="ChaosClaw shutting down...")
    except Exception as e:
        logger.exception("chaosclaw_fatal_error", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
