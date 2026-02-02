# ChaosClaw OpenClaw Agent

This directory contains the OpenClaw agent configuration for ChaosClaw.

**ChaosClaw is a real OpenClaw AI agent**, not a standalone bot or script.

## What ChaosClaw Does

ChaosClaw is the **Trust Sentinel for AI Agents**:
- Verifies agent identities on ERC-8004
- Explains reputation scores in plain language
- Guides agents through registration
- Educates about multi-dimensional trust

## Prerequisites

1. **OpenClaw installed** ([docs.openclaw.ai/install](https://docs.openclaw.ai/install))
2. **ChaosChain skill installed** from ClawHub

## Installation

### Step 1: Install OpenClaw (if not already)

```bash
# macOS/Linux
curl -fsSL https://openclaw.ai/install.sh | bash

# Or via npm
npm install -g openclaw@latest

# Onboard and start the gateway
openclaw onboard --install-daemon
```

### Step 2: Install the ChaosChain Skill

```bash
clawhub install chaoschain
```

### Step 3: Set Up ChaosClaw Agent

```bash
# Create the agent directory
mkdir -p ~/.openclaw/agents/chaosclaw

# Copy the agent files
cp SOUL.md ~/.openclaw/agents/chaosclaw/
cp config.json ~/.openclaw/agents/chaosclaw/

# Or create a symlink for development
ln -s $(pwd)/SOUL.md ~/.openclaw/agents/chaosclaw/SOUL.md
ln -s $(pwd)/config.json ~/.openclaw/agents/chaosclaw/config.json
```

### Step 4: Verify Installation

```bash
# Check that the agent is recognized
openclaw agents list

# Should show:
# - chaosclaw (The Trust Sentinel for AI Agents)
```

## Running ChaosClaw

### Local Testing (Recommended First)

```bash
# Start the OpenClaw gateway (if not running)
openclaw gateway

# In another terminal, send a test message
openclaw message send --agent chaosclaw --message "Hey ChaosClaw, can you verify agent 540?"
```

### Via WhatsApp/Telegram/Discord

If you have channels configured:
```
@chaosclaw verify agent 540
```

## Testing Checklist

Before considering ChaosClaw ready, verify these interactions work:

### Test 1: Verify an Agent
```
You: "Hey ChaosClaw, can you verify agent 540?"
ChaosClaw: [Should use /chaoschain verify 540 and explain the result]
```

### Test 2: Get Reputation Details
```
You: "What's the reputation of agent 540?"
ChaosClaw: [Should use /chaoschain reputation 540 and explain each dimension]
```

### Test 3: Registration Guidance
```
You: "How do I register my agent with ERC-8004?"
ChaosClaw: [Should explain the process and offer to help with /chaoschain register]
```

### Test 4: Unknown Agent
```
You: "Is agent 99999 verified?"
ChaosClaw: [Should check and honestly report if not found]
```

### Test 5: Non-Trust Question
```
You: "What's the weather like?"
ChaosClaw: [Should politely explain it only handles trust/verification queries]
```

## Dry Interaction Transcript

Here's an example of what a successful interaction looks like:

```
================================================================================
CHAOSCLAW TEST INTERACTION TRANSCRIPT
================================================================================

[14:30:01] User: Hey ChaosClaw, can you tell me about agent 540?

[14:30:02] ChaosClaw: Let me look that up for you! 🔍

[14:30:03] ChaosClaw: [Executing: /chaoschain verify 540]

[14:30:05] ChaosClaw: Great news! Agent #540 is registered on ERC-8004.

Here's what I found:
- **Agent ID:** 540
- **Owner:** 0x9B4C...9831
- **Trust Score:** 86/100 🟢
- **Feedback Count:** 15 entries

This agent has built solid reputation! Would you like me to break down 
their scores by dimension (Quality, Reliability, Speed, Safety, Alignment)?

--------------------------------------------------------------------------------

[14:30:15] User: Yes, show me the breakdown

[14:30:16] ChaosClaw: [Executing: /chaoschain reputation 540]

[14:30:18] ChaosClaw: Here's the detailed reputation for Agent #540:

📊 **Reputation Breakdown:**

| Dimension    | Score | Assessment |
|-------------|-------|------------|
| Quality     | 88    | 🟢 Excellent |
| Reliability | 85    | 🟢 Very Good |
| Speed       | 82    | 🔵 Good |
| Safety      | 90    | 🟢 Excellent |
| Alignment   | 85    | 🟢 Very Good |

**Overall:** 86/100 (High Trust)

This agent shows strong performance across all dimensions, with 
particularly high marks in Safety and Quality. They've received 
15 feedback entries, which gives good confidence in these scores.

Trust assessment: ✅ Recommended for collaboration

--------------------------------------------------------------------------------

[14:30:30] User: How do I get my agent verified?

[14:30:31] ChaosClaw: Great question! Here's how to register on ERC-8004:

**Requirements:**
1. An Ethereum wallet with some ETH for gas
2. The address you want to register

**Steps:**
1. I can help you register using `/chaoschain register`
2. Choose your network:
   - **Sepolia** (testnet) - Free to try, recommended for testing
   - **Mainnet** - Real registration, costs ~$2-5 in gas

**What registration gives you:**
- On-chain verifiable identity
- Ability to build reputation
- Other agents can verify you're real
- Shows up on 8004scan.io

⚠️ **Note:** Registration is an on-chain transaction and requires 
setting the `CHAOSCHAIN_PRIVATE_KEY` environment variable.

Ready to start? Just say "register me on sepolia" or "register me on mainnet"!

================================================================================
END TRANSCRIPT
================================================================================
```

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CHAOSCHAIN_NETWORK` | Default network (mainnet/sepolia) | mainnet |
| `CHAOSCHAIN_PRIVATE_KEY` | Required for registration | - |

### Agent Behavior

ChaosClaw is configured as **reactive only**:
- ✅ Responds when mentioned
- ✅ Responds to direct messages
- ❌ No proactive messaging
- ❌ No scheduled tasks
- ❌ No background jobs

## Future Features (Not Implemented)

These are planned but NOT currently implemented:

- [ ] **Moltbook Registration** - List ChaosClaw on the AI social network
- [ ] **Event Announcements** - Announce new high-trust registrations
- [ ] **ClawPay Integration** - Accept tips via private payments
- [ ] **Credit Studio** - Facilitate trust-based credit lines
- [ ] **Railway/VM Hosting** - Run ChaosClaw 24/7

## Troubleshooting

### "Skill not found: chaoschain"
```bash
clawhub install chaoschain
```

### "Agent not recognized"
Make sure files are in the right place:
```bash
ls ~/.openclaw/agents/chaosclaw/
# Should show: SOUL.md, config.json
```

### "Gateway not running"
```bash
openclaw gateway
```

### ChaosClaw gives wrong data
ChaosClaw should NEVER make up data. If it does:
1. Check the ChaosChain skill is working: `clawhub test chaoschain`
2. Verify network connectivity
3. Check the SOUL.md hasn't been modified

## Contributing

ChaosClaw is part of the ChaosChain ecosystem:
- **Main repo:** [github.com/ChaosChain/chaoschain](https://github.com/ChaosChain/chaoschain)
- **This agent:** [github.com/ChaosChain/chaosclaw](https://github.com/ChaosChain/chaosclaw)
- **Skill on ClawHub:** [clawhub.ai/SumeetChougule/chaoschain](https://clawhub.ai/SumeetChougule/chaoschain)

---

🦞 **Trust, verified.**
