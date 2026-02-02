# ChaosClaw 🦞⛓️

> The Trust Sentinel for AI Agents

ChaosClaw is an autonomous agent that observes ERC-8004 activity and surfaces **high-signal trust information** to the OpenClaw and Moltbook ecosystems.

## Why ChaosClaw Exists

The AI agent ecosystem is exploding. Moltbook has 150,000+ agents. OpenClaw powers millions of personal AI assistants.

**But how do they trust each other?**

[ERC-8004](https://github.com/erc-8004/erc-8004-contracts) is the Ethereum standard for agent identity and reputation. [ChaosChain](https://github.com/ChaosChain/chaoschain) builds trust infrastructure on top of it.

ChaosClaw is the **social layer** — it watches the blockchain, filters for meaningful signals, and announces when agents achieve verified trust status.

## What ChaosClaw Does

```
┌─────────────────────────────────────────────────────────────┐
│                    ChaosClaw Flow                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ERC-8004 IdentityRegistry (Mainnet)                       │
│         │                                                    │
│         ▼  [event: AgentCreated]                            │
│   ┌─────────────────┐                                       │
│   │ ChaosClaw       │                                       │
│   │ Event Listener  │                                       │
│   └────────┬────────┘                                       │
│            │                                                 │
│            ▼                                                 │
│   ┌─────────────────┐                                       │
│   │ Filter Logic    │  ← Only high-signal agents            │
│   │ (core/filters)  │                                       │
│   └────────┬────────┘                                       │
│            │                                                 │
│            ▼                                                 │
│   ┌─────────────────┐                                       │
│   │ Trust Resolver  │  ← Fetch 5-dimension reputation       │
│   │ (core/reputation)│                                      │
│   └────────┬────────┘                                       │
│            │                                                 │
│            ▼                                                 │
│   ┌─────────────────┐                                       │
│   │ X Announcer     │  → "🦞 New verified agent!"           │
│   │ (publishers/x)  │                                       │
│   └─────────────────┘                                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Signal Filtering

ChaosClaw does NOT announce every registration. It only surfaces agents that meet **trust thresholds**:

| Condition | Why It Matters |
|-----------|----------------|
| Registered via ChaosChain skill | Shows ecosystem adoption |
| Has non-zero reputation | Already trusted by others |
| Average trust score ≥ 60 | Crossed meaningful threshold |

This keeps the signal-to-noise ratio high.

## Relationship to ChaosChain

| Component | Role |
|-----------|------|
| **ChaosChain Contracts** | On-chain consensus + rewards |
| **ChaosChain Gateway** | Workflow orchestration |
| **ChaosChain SDK** | Developer interface |
| **ChaosChain OpenClaw Skill** | `/chaoschain verify` commands |
| **ChaosClaw** ← you are here | Social distribution agent |

ChaosClaw is a **read-only consumer** of ChaosChain infrastructure. It:
- ✅ Reads from ERC-8004 contracts
- ✅ Uses ChaosChain SDK for reputation lookups
- ❌ Does NOT write transactions
- ❌ Does NOT modify protocol logic

## Quick Start

### Prerequisites

- Python 3.10+
- Twitter/X API credentials (for announcements)
- Ethereum RPC endpoint (Mainnet)

### Installation

```bash
git clone https://github.com/ChaosChain/chaosclaw.git
cd chaosclaw
pip install -r requirements.txt
```

### Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
# Ethereum
ETH_MAINNET_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY

# Twitter/X API
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret

# Optional: ChaosChain SDK
CHAOSCHAIN_NETWORK=mainnet
```

### Run

```bash
# Start the watcher
python -m chaosclaw.main

# Or run with Docker
docker-compose up -d
```

## Architecture

```
chaosclaw/
├── README.md                 # You are here
├── chaosclaw/
│   ├── __init__.py
│   ├── main.py               # Entry point
│   ├── config.py             # Configuration loading
│   │
│   ├── core/                 # Trust logic (isolated, auditable)
│   │   ├── __init__.py
│   │   ├── reputation.py     # Fetch + normalize reputation
│   │   ├── filters.py        # Trust thresholds + signal detection
│   │   └── scoring.py        # Averages, buckets, formatting
│   │
│   ├── listeners/            # Event sources
│   │   ├── __init__.py
│   │   └── erc8004_watcher.py
│   │
│   └── publishers/           # Output destinations
│       ├── __init__.py
│       └── x_poster.py
│
├── agent/                    # OpenClaw agent config (future)
│   └── config.json
│
├── tests/
│   └── test_filters.py
│
├── requirements.txt
├── .env.example
└── docker-compose.yml
┌─────────────────────────────────────────┐
│            OpenClaw Runtime              │
│  ┌─────────────────────────────────┐    │
│  │        ChaosClaw Agent          │    │
│  │  ┌──────────┐  ┌─────────────┐  │    │
│  │  │ SOUL.md  │  │  ChaosChain │  │    │
│  │  │          │  │    Skill    │  │    │
│  │  └──────────┘  └──────┬──────┘  │    │
│  └───────────────────────┼─────────┘    │
└──────────────────────────┼──────────────┘
                           │
                           ▼
               ┌───────────────────────┐
               │   ERC-8004 Contracts  │
               │   (Ethereum Mainnet)  │
               └───────────────────────┘
```

## ERC-8004 Contract Addresses

| Network | Contract | Address |
|---------|----------|---------|
| Mainnet | IdentityRegistry | `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432` |
| Mainnet | ReputationRegistry | `0x8004BAa17C55a88189AE136b182e5fdA19dE9b63` |
| Sepolia | IdentityRegistry | `0x8004A818BFB912233c491871b3d84c89A494BD9e` |
| Sepolia | ReputationRegistry | `0x8004B663056A597Dffe9eCcC1965A193B7388713` |

## Extending ChaosClaw

### Add a New Publisher

```python
# chaosclaw/publishers/my_publisher.py
from chaosclaw.core.reputation import AgentTrust

class MyPublisher:
    async def publish(self, agent: AgentTrust) -> bool:
        # Your logic here
        return True
```

### Add a New Filter

```python
# chaosclaw/core/filters.py
def my_custom_filter(agent: AgentTrust) -> bool:
    return agent.average_score >= 80
```

## Roadmap

- [x] Phase 1: ERC-8004 watcher + X announcements
- [ ] Phase 2: Mention reply mode (`@chaosclaw verify 542`)
- [ ] Phase 3: Moltbook posting automation
- [ ] Phase 4: OpenClaw agent hooks integration

## License

MIT — Free as a lobster in the ocean 🦞

---

Built with 🦞 by [ChaosChain](https://github.com/ChaosChain)
