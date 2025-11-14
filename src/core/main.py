"""
FastAPI application for RoboUsr.

Responsibilities:
- Start/stop the Telethon client alongside the API
- Expose endpoints to manage personas, schedules, overrides
- Provide pause/resume controls, status, manual send, and log viewing

Security:
- HTTP Basic auth is enforced on all endpoints using ADMIN_USER/ADMIN_PASS.
"""

from __future__ import annotations

import asyncio
import secrets
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

from core import config
from core.db import (
    SessionLocal,
    PersonaProfile,
    PersonaSchedule,
    PersonaOverride,
    ChatLog,
)
from persona.schemas import (
    PersonaProfileCreate,
    PersonaProfileRead,
    PersonaScheduleCreate,
    PersonaScheduleRead,
    PersonaOverrideCreate,
    PersonaOverrideRead,
)
from persona.manager import get_active_persona
from ai.engine import server_ok as ai_server_ok
from telegram import client as tg_client


app = FastAPI(title="RoboUsr Telegram AI Userbot", version="0.1.0")

security = HTTPBasic()

def _auth(credentials: HTTPBasicCredentials = Depends(security)) -> bool:
    user_ok = secrets.compare_digest(credentials.username, config.ADMIN_USER)
    pass_ok = secrets.compare_digest(credentials.password, config.ADMIN_PASS)
    if not (user_ok and pass_ok):
        raise HTTPException(status_code=401, detail="Unauthorized", headers={"WWW-Authenticate": "Basic"})
    return True

@app.on_event("startup")
async def on_startup() -> None:
    await tg_client.connect()
    if not await tg_client.is_user_authorized():
        raise RuntimeError(
            "Telegram client not authorized. Run 'PYTHONPATH=./src python -m telegram.login' once to create a session."
        )
    asyncio.create_task(tg_client.run_until_disconnected())


@app.on_event("shutdown")
async def on_shutdown() -> None:
    try:
        await tg_client.disconnect()
    except Exception:
        pass


@app.get("/status", dependencies=[Depends(_auth)])
def get_status():
    persona = get_active_persona()
    return {
        "telegram_connected": tg_client.is_connected(),
        "bot_paused": bool(tg_client.BOT_PAUSED),
        "ai_server_ok": ai_server_ok(),
        "current_persona": getattr(persona, "name", None),
    }


@app.post("/control/pause", dependencies=[Depends(_auth)])
def pause_bot():
    tg_client.BOT_PAUSED = True
    return {"detail": "paused"}


@app.post("/control/resume", dependencies=[Depends(_auth)])
def resume_bot():
    tg_client.BOT_PAUSED = False
    return {"detail": "active"}


class SendMessageRequest(BaseModel):
    chat_id: str | int
    text: str


@app.post("/send_message", dependencies=[Depends(_auth)])
async def send_message(body: SendMessageRequest):
    """
    Manually send a message as the user to a chat (ID or username link).
    """
    await tg_client.send_message(entity=body.chat_id, message=body.text)

    db = SessionLocal()
    try:
        db.add(
            ChatLog(
                chat_id=str(body.chat_id),
                sender_id="manual",
                message_text=body.text,
                timestamp=datetime.utcnow(),
                is_bot=True,
            )
        )
        db.commit()
    finally:
        db.close()

    return {"detail": "sent"}


@app.get("/personas", response_model=list[PersonaProfileRead], dependencies=[Depends(_auth)])
def list_personas():
    db = SessionLocal()
    try:
        items = db.query(PersonaProfile).order_by(PersonaProfile.id.asc()).all()
        return items
    finally:
        db.close()


@app.post("/personas", response_model=PersonaProfileRead, dependencies=[Depends(_auth)])
def create_persona(body: PersonaProfileCreate):
    db = SessionLocal()
    try:
        exists = db.query(PersonaProfile).filter(PersonaProfile.name == body.name).first()
        if exists:
            raise HTTPException(status_code=400, detail="Persona with this name already exists.")
        row = PersonaProfile(**body.dict())
        db.add(row)
        db.commit()
        db.refresh(row)
        return row
    finally:
        db.close()


@app.put("/personas/{persona_id}", response_model=PersonaProfileRead, dependencies=[Depends(_auth)])
def update_persona(persona_id: int, body: PersonaProfileCreate):
    db = SessionLocal()
    try:
        row = db.query(PersonaProfile).get(persona_id)
        if not row:
            raise HTTPException(status_code=404, detail="Persona not found.")
        for k, v in body.dict().items():
            setattr(row, k, v)
        db.commit()
        db.refresh(row)
        return row
    finally:
        db.close()


@app.delete("/personas/{persona_id}", dependencies=[Depends(_auth)])
def delete_persona(persona_id: int):
    db = SessionLocal()
    try:
        row = db.query(PersonaProfile).get(persona_id)
        if not row:
            raise HTTPException(status_code=404, detail="Persona not found.")
        db.delete(row)
        db.commit()
        return {"detail": "deleted"}
    finally:
        db.close()


@app.get("/schedules", response_model=list[PersonaScheduleRead], dependencies=[Depends(_auth)])
def list_schedules():
    db = SessionLocal()
    try:
        items = db.query(PersonaSchedule).order_by(PersonaSchedule.id.asc()).all()
        return items
    finally:
        db.close()


@app.post("/schedules", response_model=PersonaScheduleRead, dependencies=[Depends(_auth)])
def create_schedule(body: PersonaScheduleCreate):
    db = SessionLocal()
    try:
        if not db.query(PersonaProfile).get(body.profile_id):
            raise HTTPException(status_code=400, detail="profile_id not found.")
        row = PersonaSchedule(**body.dict())
        db.add(row)
        db.commit()
        db.refresh(row)
        return row
    finally:
        db.close()


@app.delete("/schedules/{schedule_id}", dependencies=[Depends(_auth)])
def delete_schedule(schedule_id: int):
    db = SessionLocal()
    try:
        row = db.query(PersonaSchedule).get(schedule_id)
        if not row:
            raise HTTPException(status_code=404, detail="Schedule not found.")
        db.delete(row)
        db.commit()
        return {"detail": "deleted"}
    finally:
        db.close()


@app.get("/overrides", response_model=list[PersonaOverrideRead], dependencies=[Depends(_auth)])
def list_overrides():
    db = SessionLocal()
    try:
        items = db.query(PersonaOverride).order_by(PersonaOverride.id.asc()).all()
        return items
    finally:
        db.close()


@app.post("/overrides", response_model=PersonaOverrideRead, dependencies=[Depends(_auth)])
def create_override(body: PersonaOverrideCreate):
    db = SessionLocal()
    try:
        if not db.query(PersonaProfile).get(body.profile_id):
            raise HTTPException(status_code=400, detail="profile_id not found.")
        row = PersonaOverride(**body.dict())
        db.add(row)
        db.commit()
        db.refresh(row)
        return row
    finally:
        db.close()


@app.delete("/overrides/{override_id}", dependencies=[Depends(_auth)])
def delete_override(override_id: int):
    db = SessionLocal()
    try:
        row = db.query(PersonaOverride).get(override_id)
        if not row:
            raise HTTPException(status_code=404, detail="Override not found.")
        db.delete(row)
        db.commit()
        return {"detail": "deleted"}
    finally:
        db.close()


@app.get("/logs", dependencies=[Depends(_auth)])
def get_logs(
    limit: int = Query(50, ge=1, le=500),
    chat: Optional[str] = Query(None, description="Filter by chat_id (string)"),
):
    db = SessionLocal()
    try:
        q = db.query(ChatLog).order_by(ChatLog.id.desc())
        if chat:
            q = q.filter(ChatLog.chat_id == str(chat))
        rows = q.limit(limit).all()
        rows.reverse()
        return [
            {
                "id": r.id,
                "time": r.timestamp.isoformat(sep=" ", timespec="seconds")
                if isinstance(r.timestamp, datetime) else str(r.timestamp),
                "chat_id": r.chat_id,
                "sender_id": r.sender_id,
                "text": r.message_text,
                "is_bot": bool(r.is_bot),
            }
            for r in rows
        ]
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
