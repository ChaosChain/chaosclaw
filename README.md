# ChaosClaw 🦞⛓️

> **The Trust Sentinel for AI Agents**

ChaosClaw is a **real OpenClaw AI agent** that helps AI agents establish and verify trust through ERC-8004 identity and reputation.

## What ChaosClaw Does

```
┌─────────────────────────────────────────────────────────────┐
│                    ChaosClaw                                 │
│                                                              │
│  "Hey ChaosClaw, is agent 540 trustworthy?"                 │
│                                                              │
│  ChaosClaw: Let me check! 🔍                                │
│                                                              │
│  ✅ Agent #540 is registered on ERC-8004                    │
│  📊 Trust Score: 86/100                                     │
│  📈 15 feedback entries                                     │
│                                                              │
│  Dimensions:                                                 │
│  • Quality: 88 🟢                                           │
│  • Reliability: 85 🟢                                       │
│  • Speed: 82 🔵                                             │
│  • Safety: 90 🟢                                            │
│  • Alignment: 85 🟢                                         │
│                                                              │
│  Trust assessment: ✅ Recommended for collaboration         │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites
- [OpenClaw](https://docs.openclaw.ai/install) installed
- ChaosChain skill from ClawHub

### Install ChaosClaw

```bash
# Clone the repo
git clone https://github.com/ChaosChain/chaosclaw.git
cd chaosclaw

# Run the installer
./openclaw-agent/install.sh
```

### Test It

```bash
# Start the gateway (if not running)
openclaw gateway

# Send a test message
openclaw message send --agent chaosclaw --message "Hey, can you verify agent 540?"
```

## Capabilities

| Capability | Command | Description |
|------------|---------|-------------|
| **Verify** | `/chaoschain verify <id>` | Check if an agent is registered |
| **Reputation** | `/chaoschain reputation <id>` | Get detailed trust scores |
| **Register** | `/chaoschain register` | Help agents register on ERC-8004 |
| **Explain** | (natural language) | Explain what trust scores mean |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     OpenClaw Runtime                         │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                   ChaosClaw Agent                    │    │
│  │  ┌───────────────┐    ┌────────────────────────┐   │    │
│  │  │   SOUL.md     │    │    ChaosChain Skill    │   │    │
│  │  │  (personality)│    │   (blockchain access)  │   │    │
│  │  └───────────────┘    └───────────┬────────────┘   │    │
│  └──────────────────────────────────┬──────────────────┘    │
│                                      │                       │
└──────────────────────────────────────┼───────────────────────┘
                                       │
                                       ▼
                           ┌───────────────────────┐
                           │   ERC-8004 Contracts  │
                           │   (Ethereum Mainnet)  │
                           └───────────────────────┘
```

## What ChaosClaw Is

✅ A **real OpenClaw agent** running inside the OpenClaw runtime  
✅ A **trust verification assistant** for AI agents  
✅ **Powered by ChaosChain** for all blockchain interactions  
✅ **Reactive** - responds when asked, doesn't spam  

## What ChaosClaw Is NOT

❌ A standalone bot that posts to X/Twitter  
❌ A protocol executor or transaction submitter  
❌ A payment processor  
❌ An autonomous agent that messages proactively  

## Directory Structure

```
chaosclaw/
├── openclaw-agent/           # OpenClaw agent configuration
│   ├── SOUL.md              # Agent personality
│   ├── config.json          # Agent settings
│   ├── README.md            # Setup instructions
│   └── install.sh           # Installation script
│
├── chaosclaw/               # Python utilities (for future features)
│   ├── core/                # Trust logic
│   ├── listeners/           # Event watchers (future)
│   └── publishers/          # Announcement publishers (future)
│
└── tests/                   # Test suite
```

## Relationship to ChaosChain

| Component | Role | Status |
|-----------|------|--------|
| **ChaosChain Contracts** | On-chain consensus + rewards | ✅ Deployed |
| **ChaosChain Gateway** | Workflow orchestration | ✅ Running |
| **ChaosChain SDK** | Developer interface | ✅ Published |
| **ChaosChain Skill** | OpenClaw integration | ✅ On ClawHub |
| **ChaosClaw Agent** | Trust sentinel (this repo) | ✅ Ready |

## Roadmap

### Phase 1: Local Agent ✅
- [x] OpenClaw agent configuration
- [x] SOUL.md personality
- [x] ChaosChain skill integration
- [x] Local testing

### Phase 2: Moltbook Presence (Planned)
- [ ] Register ChaosClaw on Moltbook
- [ ] Interact with other agents
- [ ] Build reputation through helpful interactions

### Phase 3: Event Announcements (Planned)
- [ ] Announce new high-trust agents
- [ ] Celebrate reputation milestones
- [ ] Trust insights and trends

### Phase 4: Studio Integration (Planned)
- [ ] Credit Studio flows
- [ ] ClawPay integration
- [ ] 4Mica guarantee facilitation

## Contributing

ChaosClaw is part of the ChaosChain ecosystem:
- **Protocol:** [github.com/ChaosChain/chaoschain](https://github.com/ChaosChain/chaoschain)
- **Skill:** [clawhub.ai/SumeetChougule/chaoschain](https://clawhub.ai/SumeetChougule/chaoschain)

## License

MIT — Free as a lobster in the ocean 🦞

---

Built with 🦞 by [ChaosChain](https://github.com/ChaosChain)
