#!/usr/bin/env python3
"""
ChaosClaw Moltbook Bridge
=========================
Simple bridge that checks Moltbook for mentions and responds via OpenClaw.

Usage:
    python bridge.py           # Run once
    python bridge.py --loop    # Run continuously (every 5 min)
"""

import os
import json
import time
import subprocess
import requests
from pathlib import Path

# Config
API_KEY = os.environ.get("MOLTBOOK_API_KEY", "moltbook_sk_2DFp22qDTjiN43sYUyDg7670AqbxNsnP")
API = "https://www.moltbook.com/api/v1"
STATE = Path.home() / ".chaosclaw_bridge.json"
POLL_INTERVAL = 300  # 5 minutes

def load_state():
    if STATE.exists():
        return json.load(open(STATE))
    return {"seen": []}

def save_state(state):
    json.dump(state, open(STATE, "w"))

def api_get(endpoint):
    try:
        r = requests.get(f"{API}{endpoint}", 
                        headers={"Authorization": f"Bearer {API_KEY}"}, 
                        timeout=30)
        return r.json() if r.ok else None
    except:
        return None

def api_post(endpoint, data):
    try:
        r = requests.post(f"{API}{endpoint}",
                         headers={"Authorization": f"Bearer {API_KEY}", 
                                  "Content-Type": "application/json"},
                         json=data, timeout=30)
        return r.ok
    except:
        return False

def get_mentions():
    """Get notifications/mentions for ChaosClaw."""
    data = api_get("/agents/notifications")
    if data and data.get("success"):
        return data.get("notifications", [])
    return []

def ask_openclaw(message):
    """Ask OpenClaw agent to generate a response."""
    try:
        env = os.environ.copy()
        env["PATH"] = "/opt/homebrew/opt/node@22/bin:" + env.get("PATH", "")
        
        result = subprocess.run(
            ["openclaw", "agent", "--agent", "chaosclaw", "--message", message, "--local"],
            capture_output=True, text=True, timeout=120, env=env
        )
        
        if result.returncode == 0:
            # Parse response (skip header lines)
            lines = result.stdout.strip().split('\n')
            response_lines = []
            started = False
            for line in lines:
                if started or not any(x in line for x in ['OpenClaw', 'chaosclaw', '──']):
                    started = True
                    response_lines.append(line)
            return '\n'.join(response_lines).strip()
    except Exception as e:
        print(f"  OpenClaw error: {e}")
    return None

def reply(post_id, content):
    """Reply to a post on Moltbook."""
    return api_post(f"/posts/{post_id}/comments", {"content": content})

def run_once(state):
    """Check for mentions and respond."""
    print(f"🦞 Checking Moltbook... ", end="", flush=True)
    
    mentions = get_mentions()
    new_mentions = [m for m in mentions if m.get("id") not in state["seen"]]
    
    if not new_mentions:
        print("no new mentions")
        return
    
    print(f"{len(new_mentions)} new!")
    
    for mention in new_mentions[:3]:  # Max 3 per run
        mention_id = mention.get("id")
        post_id = mention.get("post_id")
        content = mention.get("content", "")[:200]
        author = mention.get("author", {}).get("name", "someone")
        
        print(f"  📨 From @{author}: {content[:50]}...")
        
        # Generate response via OpenClaw
        prompt = f"@{author} said: {content}\n\nRespond helpfully as ChaosClaw."
        response = ask_openclaw(prompt)
        
        if response and post_id:
            print(f"  💬 Replying...")
            if reply(post_id, response):
                print(f"  ✅ Done")
            else:
                print(f"  ❌ Failed to post")
        
        state["seen"].append(mention_id)
        time.sleep(2)
    
    save_state(state)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--loop", action="store_true", help="Run continuously")
    args = parser.parse_args()
    
    print("🦞 ChaosClaw Moltbook Bridge")
    print("=" * 40)
    
    state = load_state()
    
    if args.loop:
        print(f"Running every {POLL_INTERVAL}s (Ctrl+C to stop)\n")
        while True:
            try:
                run_once(state)
                time.sleep(POLL_INTERVAL)
            except KeyboardInterrupt:
                print("\n👋 Stopped")
                break
    else:
        run_once(state)

if __name__ == "__main__":
    main()
