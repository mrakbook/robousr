# Architecture

RoboUsr consists of four main parts:

1. **FastAPI app** (`src/core/main.py`)  
   - Starts/stops the Telethon client on startup/shutdown  
   - Exposes admin endpoints (status, pause/resume, send, CRUD for personas/schedules/overrides, logs)  
   - Secured with HTTP Basic auth (`ADMIN_USER`/`ADMIN_PASS`)

2. **Telegram integration** (`src/telegram/*`)  
   - `TelegramClient` from Telethon listens for incoming messages  
   - Gathers recent conversation from DB (`chat_log`)  
   - Selects an active persona using `persona.manager.get_active_persona`  
   - Calls the AI engine to produce a reply and posts it back
   - Logs both incoming and outgoing messages to DB

3. **AI engine** (`src/ai/engine.py`)  
   - Talks to a local **llama.cpp** server exposing an OpenAI‑compatible API (`/v1/*`)  
   - Works with either the `openai` v1 client or legacy API configured to point at `OPENAI_API_BASE`  
   - Uses the model alias set on the server (`LLAMA_MODEL_NAME`)

4. **Persistence (MariaDB)** (`db/schema.sql`, `src/core/db.py`)  
   - `persona_profile` – named personas with tone sliders  
   - `persona_schedule` – HH:MM ranges + DOW bitmask (Mon=bit0 … Sun=bit6)  
   - `persona_override` – per chat or per user overrides  
   - `chat_log` – simple append‑only history (incoming/outgoing)

## Persona selection order

1) **Chat override** → 2) **User override** → 3) **Schedule** (supports overnight windows) → 4) **Default persona** (named *default* or first record).

## Data flow

```
[Telegram] → [Telethon handler] → [DB recent history]
                               → [Persona manager] → [AI engine → llama.cpp]
                               → [Reply to Telegram] → [DB log]
```

## Defaults & language

The default system prompt is in **Russian**. You can set descriptions and tone knobs per persona to affect style; the generated prompt is sent as the `system` message.

## Health checks

- `/status` shows `telegram_connected`, `bot_paused`, `ai_server_ok`, and current persona name.
- `ai.server_ok()` performs a lightweight `models.list()` call to the local server.
