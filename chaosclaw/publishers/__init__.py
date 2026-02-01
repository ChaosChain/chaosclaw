"""
ChaosClaw Publishers Module

Output destinations for agent announcements.
Currently supports X/Twitter.
"""

from .x_poster import XPoster

__all__ = ["XPoster"]
