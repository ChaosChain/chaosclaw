"""
ChaosClaw Listeners Module

Event sources for ChaosClaw.
Currently supports ERC-8004 IdentityRegistry event watching.
"""

from .erc8004_watcher import ERC8004Watcher

__all__ = ["ERC8004Watcher"]
