"""
Interactive one-time login helper.

Run:
    python -m telegram.login

This will prompt for your phone number and the code from Telegram.
A session file named after SESSION_NAME (e.g., 'robosession.session')
will be created in the working directory for future non-interactive runs.
"""

from __future__ import annotations

from telethon import TelegramClient
from core import config


async def main() -> None:
    client = TelegramClient(config.SESSION_NAME, config.API_ID, config.API_HASH)
    await client.start()
    me = await client.get_me()
    print(f"Logged in as: {getattr(me, 'username', None) or me.id}")
    await client.disconnect()
    print("Session created. You can now start the RoboUsr app.")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
