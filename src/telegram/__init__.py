"""
RoboUsr · Telegram integration package.

Exports:
- client: Telethon TelegramClient instance (unstarted; FastAPI starts it).
- BOT_PAUSED: global pause flag checked by the message handler.
- pause(), resume(), is_paused(): helpers to control pause state.
"""

from __future__ import annotations

from .client import client, BOT_PAUSED, pause, resume, is_paused

__all__ = ["client", "BOT_PAUSED", "pause", "resume", "is_paused"]

__version__ = "0.1.0"
