"""
ERC-8004 IdentityRegistry Event Watcher

Polls the IdentityRegistry contract for new agent registrations.
Fetches reputation data and yields AgentTrust objects.
"""

import asyncio
import structlog
from typing import AsyncIterator, Optional
from web3 import Web3
from web3.contract import Contract

from ..config import EthereumConfig
from ..core.reputation import AgentTrust, create_agent_trust_from_sdk
from ..core.filters import is_chaoschain_registration


logger = structlog.get_logger(__name__)


# ERC-8004 IdentityRegistry ABI (minimal - just what we need)
IDENTITY_REGISTRY_ABI = [
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "agentId", "type": "uint256"},
            {"indexed": True, "name": "owner", "type": "address"},
            {"indexed": False, "name": "uri", "type": "string"},
        ],
        "name": "Transfer",  # ERC-721 Transfer event (mint)
        "type": "event",
    },
    {
        "inputs": [{"name": "tokenId", "type": "uint256"}],
        "name": "ownerOf",
        "outputs": [{"name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"name": "tokenId", "type": "uint256"}],
        "name": "tokenURI",
        "outputs": [{"name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function",
    },
]

# ERC-8004 ReputationRegistry ABI (minimal)
REPUTATION_REGISTRY_ABI = [
    {
        "inputs": [
            {"name": "agentId", "type": "uint256"},
            {"name": "clientAddresses", "type": "address[]"},
        ],
        "name": "getSummary",
        "outputs": [
            {"name": "count", "type": "uint256"},
            {"name": "value", "type": "int128"},
            {"name": "valueDecimals", "type": "uint8"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"name": "agentId", "type": "uint256"}],
        "name": "getClients",
        "outputs": [{"name": "", "type": "address[]"}],
        "stateMutability": "view",
        "type": "function",
    },
]


class ERC8004Watcher:
    """
    Watches ERC-8004 IdentityRegistry for new agent registrations.
    
    Uses polling (not websockets) for reliability and compatibility.
    """
    
    def __init__(
        self,
        config: EthereumConfig,
        poll_interval: int = 60,
        lookback_blocks: int = 1000,
    ):
        """
        Initialize the watcher.
        
        Args:
            config: Ethereum configuration
            poll_interval: Seconds between polls
            lookback_blocks: How far back to look on first run
        """
        self.config = config
        self.poll_interval = poll_interval
        self.lookback_blocks = lookback_blocks
        
        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(config.rpc_url))
        
        # Initialize contracts
        self.identity_registry: Contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(config.identity_registry_address),
            abi=IDENTITY_REGISTRY_ABI,
        )
        self.reputation_registry: Contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(config.reputation_registry_address),
            abi=REPUTATION_REGISTRY_ABI,
        )
        
        # State
        self.last_block: Optional[int] = None
        self.seen_agents: set[int] = set()
        
        logger.info(
            "erc8004_watcher_initialized",
            network=config.network,
            identity_registry=config.identity_registry_address,
            reputation_registry=config.reputation_registry_address,
        )
    
    async def watch(self) -> AsyncIterator[AgentTrust]:
        """
        Watch for new registrations and yield AgentTrust objects.
        
        This is an infinite async generator that polls for new events.
        """
        logger.info("erc8004_watcher_starting", poll_interval=self.poll_interval)
        
        while True:
            try:
                async for agent in self._poll_once():
                    yield agent
            except Exception as e:
                logger.error("erc8004_watcher_error", error=str(e))
            
            await asyncio.sleep(self.poll_interval)
    
    async def _poll_once(self) -> AsyncIterator[AgentTrust]:
        """
        Poll for new registrations once.
        """
        current_block = self.w3.eth.block_number
        
        # Determine from_block
        if self.last_block is None:
            from_block = max(0, current_block - self.lookback_blocks)
            logger.info(
                "erc8004_watcher_initial_scan",
                from_block=from_block,
                to_block=current_block,
            )
        else:
            from_block = self.last_block + 1
        
        if from_block > current_block:
            return
        
        # Get Transfer events (mints have from=0x0)
        # Note: ERC-721 Transfer(from, to, tokenId)
        # For mints, from = 0x0000...
        try:
            events = self.identity_registry.events.Transfer.get_logs(
                fromBlock=from_block,
                toBlock=current_block,
            )
        except Exception as e:
            logger.warning("erc8004_watcher_event_fetch_failed", error=str(e))
            events = []
        
        for event in events:
            # Filter for mints only (from = zero address)
            # The Transfer event has 'from' in args
            from_addr = event.args.get("from", "0x" + "0" * 40)
            if from_addr != "0x" + "0" * 40:
                continue  # Not a mint
            
            agent_id = event.args.get("agentId") or event.args.get("tokenId")
            if agent_id is None:
                continue
            
            # Skip if already seen
            if agent_id in self.seen_agents:
                continue
            
            self.seen_agents.add(agent_id)
            
            # Fetch agent data
            try:
                agent = await self._fetch_agent_trust(
                    agent_id=agent_id,
                    tx_hash=event.transactionHash.hex() if event.transactionHash else None,
                    block_number=event.blockNumber,
                )
                
                logger.info(
                    "erc8004_watcher_new_agent",
                    agent_id=agent_id,
                    owner=agent.owner,
                    average_score=agent.average_score,
                    has_reputation=agent.has_reputation,
                )
                
                yield agent
                
            except Exception as e:
                logger.warning(
                    "erc8004_watcher_agent_fetch_failed",
                    agent_id=agent_id,
                    error=str(e),
                )
        
        self.last_block = current_block
    
    async def _fetch_agent_trust(
        self,
        agent_id: int,
        tx_hash: Optional[str] = None,
        block_number: Optional[int] = None,
    ) -> AgentTrust:
        """
        Fetch complete trust profile for an agent.
        
        Args:
            agent_id: The agent ID
            tx_hash: Registration transaction hash
            block_number: Registration block number
        
        Returns:
            AgentTrust with reputation data
        """
        # Fetch owner
        try:
            owner = self.identity_registry.functions.ownerOf(agent_id).call()
        except Exception:
            owner = "0x" + "0" * 40
        
        # Fetch URI
        try:
            uri = self.identity_registry.functions.tokenURI(agent_id).call()
        except Exception:
            uri = None
        
        # Fetch reputation
        reputation_data = await self._fetch_reputation(agent_id)
        
        # Check if registered via ChaosChain
        registered_via_chaoschain = False
        if tx_hash:
            try:
                tx = self.w3.eth.get_transaction(tx_hash)
                registered_via_chaoschain = is_chaoschain_registration({
                    "input": tx.input.hex() if tx.input else "",
                    "uri": uri,
                })
            except Exception:
                pass
        
        agent = create_agent_trust_from_sdk(
            agent_id=agent_id,
            owner=owner,
            reputation_data=reputation_data,
            tx_hash=tx_hash,
            block_number=block_number,
        )
        agent.uri = uri
        agent.registered_via_chaoschain = registered_via_chaoschain
        
        return agent
    
    async def _fetch_reputation(self, agent_id: int) -> Optional[dict]:
        """
        Fetch reputation data from ReputationRegistry.
        
        Returns dict compatible with ChaosChain SDK format.
        """
        try:
            # Get clients first
            clients = self.reputation_registry.functions.getClients(agent_id).call()
            
            # Get summary
            count, value, decimals = self.reputation_registry.functions.getSummary(
                agent_id, clients
            ).call()
            
            # Normalize value
            if decimals > 0:
                normalized_value = value // (10 ** decimals)
            else:
                normalized_value = value
            
            return {
                "feedback_count": count,
                "average": max(0, min(100, normalized_value)),
                # Note: Individual dimensions would need more calls
                # For now, we just have the aggregate
            }
            
        except Exception as e:
            logger.debug(
                "erc8004_watcher_reputation_fetch_failed",
                agent_id=agent_id,
                error=str(e),
            )
            return None
    
    async def get_agent(self, agent_id: int) -> Optional[AgentTrust]:
        """
        Fetch a single agent by ID (for mention handling).
        
        Args:
            agent_id: The agent ID to fetch
        
        Returns:
            AgentTrust or None if not found
        """
        try:
            return await self._fetch_agent_trust(agent_id)
        except Exception as e:
            logger.warning(
                "erc8004_watcher_get_agent_failed",
                agent_id=agent_id,
                error=str(e),
            )
            return None
