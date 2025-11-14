from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Tuple

from telethon import TelegramClient, events
from telethon.errors import RPCError

from core import config
from core.db import SessionLocal, ChatLog
from persona.manager import get_active_persona, persona_to_system_message
from ai.engine import generate_reply


client = TelegramClient(config.SESSION_NAME, config.API_ID, config.API_HASH)

BOT_PAUSED: bool = False


def pause() -> None:
    global BOT_PAUSED
    BOT_PAUSED = True


def resume() -> None:
    global BOT_PAUSED
    BOT_PAUSED = False


def is_paused() -> bool:
    return BOT_PAUSED


async def _gather_history(chat_id: int, limit: int = 5) -> List[Tuple[str, str]]:
    db = SessionLocal()
    try:
        rows = (
            db.query(ChatLog)
            .filter(ChatLog.chat_id == str(chat_id))
            .order_by(ChatLog.id.desc())
            .limit(limit)
            .all()
        )
        rows.reverse()
        history: List[Tuple[str, str]] = []
        for r in rows:
            role = "assistant" if r.is_bot else "user"
            if r.message_text:
                history.append((role, r.message_text))
        return history
    finally:
        db.close()


async def _log_messages(
    chat_id: int,
    sender_id: int,
    incoming_text: str,
    reply_text: str | None,
    incoming_dt,
) -> None:
    db = SessionLocal()
    try:
        ts_in = incoming_dt
        if ts_in is None:
            ts_in = datetime.now(timezone.utc)
        if getattr(ts_in, "tzinfo", None) is not None:
            ts_in = ts_in.astimezone(timezone.utc).replace(tzinfo=None)

        db.add(
            ChatLog(
                chat_id=str(chat_id),
                sender_id=str(sender_id),
                message_text=incoming_text,
                timestamp=ts_in,
                is_bot=False,
            )
        )
        if reply_text:
            db.add(
                ChatLog(
                    chat_id=str(chat_id),
                    sender_id=str(sender_id),
                    message_text=reply_text,
                    timestamp=datetime.utcnow(),
                    is_bot=True,
                )
            )
        db.commit()
    finally:
        db.close()


@client.on(events.NewMessage(incoming=True))
async def handle_new_message(event: events.NewMessage.Event) -> None:
    if event.out or not event.message:
        return
    if BOT_PAUSED:
        return

    chat_id = event.chat_id
    sender_id = event.sender_id
    incoming_text = event.raw_text or ""

    try:
        persona = get_active_persona(chat_id=chat_id, user_id=sender_id)
        system_prompt = persona_to_system_message(persona)

        history = await _gather_history(chat_id, limit=5)

        async with client.action(event.chat_id, "typing"):
            reply = generate_reply(system_prompt, history, incoming_text)

        if reply:
            await event.reply(reply)

        await _log_messages(
            chat_id=chat_id,
            sender_id=sender_id,
            incoming_text=incoming_text,
            reply_text=reply,
            incoming_dt=getattr(event, "date", None),
        )

    except RPCError as e:
        print(f"[Telegram RPCError] {e}")
    except Exception as e:
        print(f"[HandlerError] {e}")
