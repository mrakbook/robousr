from __future__ import annotations

from datetime import datetime, time
from typing import Optional

from core.db import SessionLocal, PersonaProfile, PersonaSchedule, PersonaOverride


def _parse_hhmm(value: str) -> time:
    """Parse 'HH:MM' (24h) into a time object. Assumes valid input stored in DB."""
    hh, mm = value.split(":")
    return time(int(hh), int(mm))


def _time_matches_interval(
    now_t: time,
    start_t: time,
    end_t: time,
    today_bit: int,
    yesterday_bit: int,
    dow_mask: Optional[int],
) -> bool:
    """
    Check if 'now_t' falls within [start_t, end_t) considering overnight windows.

    Day-of-week mask semantics:
      - Bits 0..6 correspond to Monday..Sunday (matches datetime.weekday()).
      - If interval is non-overnight (start <= end), the mask applies to *today*.
      - If overnight (start > end):
          * If now_t >= start_t -> use today's bit
          * If now_t <  end_t   -> use yesterday's bit
    """
    if start_t <= end_t:
        if dow_mask is not None and (dow_mask & today_bit) == 0:
            return False
        return start_t <= now_t < end_t
    else:
        if now_t >= start_t:
            if dow_mask is not None and (dow_mask & today_bit) == 0:
                return False
            return True
        else:
            if dow_mask is not None and (dow_mask & yesterday_bit) == 0:
                return False
            return now_t < end_t


def _select_default_persona(db) -> Optional[PersonaProfile]:
    """
    Choose a default persona.
    Preference: a persona explicitly named 'default' (case-insensitive), otherwise first by id.
    """
    p = db.query(PersonaProfile).filter(PersonaProfile.name.ilike("default")).first()
    if p:
        return p
    return db.query(PersonaProfile).order_by(PersonaProfile.id.asc()).first()


def get_active_persona(
    chat_id: Optional[int] = None,
    user_id: Optional[int] = None,
) -> Optional[PersonaProfile]:
    """
    Determine the active persona for a given context.

    Priority:
      1. Chat-specific override
      2. User-specific override
      3. Time-based schedule (supports overnight intervals and DOW masks)
      4. Default persona (named 'default' or first row)
    """
    db = SessionLocal()
    try:
        if chat_id is not None:
            over = db.query(PersonaOverride).filter(PersonaOverride.chat_id == str(chat_id)).first()
            if over:
                persona = db.get(PersonaProfile, over.profile_id)
                if persona:
                    return persona

        if user_id is not None:
            over = db.query(PersonaOverride).filter(PersonaOverride.user_id == str(user_id)).first()
            if over:
                persona = db.get(PersonaProfile, over.profile_id)
                if persona:
                    return persona

        now = datetime.now()
        now_t = time(now.hour, now.minute)
        weekday = now.weekday()
        today_bit = 1 << weekday
        yesterday_bit = 1 << ((weekday - 1) % 7)

        schedules = db.query(PersonaSchedule).order_by(PersonaSchedule.id.asc()).all()
        for sched in schedules:
            try:
                start_t = _parse_hhmm(sched.start_time)
                end_t = _parse_hhmm(sched.end_time)
            except Exception:
                continue

            if _time_matches_interval(
                now_t=now_t,
                start_t=start_t,
                end_t=end_t,
                today_bit=today_bit,
                yesterday_bit=yesterday_bit,
                dow_mask=sched.dow_mask,
            ):
                persona = db.get(PersonaProfile, sched.profile_id)
                if persona:
                    return persona

        return _select_default_persona(db)
    finally:
        db.close()


def persona_to_system_message(persona: Optional[PersonaProfile]) -> str:
    """
    Convert a PersonaProfile into a concise Russian system prompt for the AI model.
    """
    if not persona:
        return "Ты дружелюбный собеседник. Отвечай по-русски, будь кратким и вежливым."

    traits = []
    if getattr(persona, "tone_funny", 0) > 5:
        traits.append("остроумный и шуточный")
    if getattr(persona, "tone_formal", 0) > 5:
        traits.append("вежливый и формальный")
    if getattr(persona, "tone_angry", 0) > 5:
        traits.append("резковатый и раздражительный")

    style = "; ".join(traits) if traits else "нейтральный"
    name = getattr(persona, "name", None) or "собеседник"

    desc = (persona.description or "").strip()
    if desc:
        return f"{desc} Стиль: {style}. Ты — {name}. Отвечай по-русски по умолчанию."
    return f"Ты — {name}, стиль общения {style}. Отвечай по-русски по умолчанию."
