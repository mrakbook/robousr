# RoboUsr

A self‑hosted **Telegram AI userbot** with persona scheduling. Built with **FastAPI + Telethon** and a local **llama.cpp** server that exposes an OpenAI‑compatible API.

> Author: **Boris Karaoglanov** · Contact: **<boris@mrakbook.com>** · License: MIT

## ✨ Features

- **Userbot** that replies from your personal Telegram account using a local LLM
- **Persona engine**: default persona, time‑based schedules (with DOW mask), and per‑chat / per‑user overrides
- **Local LLM** via `llama-cpp-python` HTTP server (OpenAI‑compatible `/v1/*`)
- **Admin REST API** with HTTP Basic auth; pause/resume bot, send manual message, view logs
- **MariaDB** persistence for personas, schedules, overrides, and chat logs
- **Systemd units & helper scripts** for production deployment

> ⚠️ **Important**: This is a *userbot*. Using automated behavior on a user account can be risky. Make sure you understand local law, platform rules, and accept full responsibility for how you use this software.

## 📦 Repository layout

```
/
├─ src/
│  ├─ core/        # config, DB models, FastAPI app
│  ├─ telegram/    # Telethon client & message handler
│  ├─ ai/          # llama.cpp OpenAI-compatible integration
│  └─ persona/     # persona schemas, manager, system prompt
├─ db/schema.sql   # MariaDB schema (import manually)
├─ start_model.sh  # run local llama.cpp server
├─ start_bot.sh    # run FastAPI app (starts Telethon client)
├─ robousr.service           # systemd unit for the app
└─ robousr-llama.service     # systemd unit for the model server
```

## 🚀 Quickstart

### 1) Create and activate a virtualenv

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -U pip
# If you have requirements.txt, prefer:
# pip install -r requirements.txt
# Or install the needed libs explicitly:
pip install -U fastapi uvicorn telethon SQLAlchemy PyMySQL pydantic openai "llama-cpp-python[server]"
```

### 2) Configure environment

Copy `.env.example` to `.env` and fill your values (Telegram API keys, DB creds, model path, etc.). See **CONFIGURATION.md** for details.

```bash
cp .env.example .env
$EDITOR .env
```

### 3) Prepare the database (MariaDB)

Create a database and import the schema:

```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS telegram_bot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p telegram_bot < db/schema.sql
```

Update your `.env` with `DB_USER`/`DB_PASSWORD` or create a user with rights to that DB.

### 4) One‑time Telegram login

This will create a session file (name controlled by `SESSION_NAME`):

```bash
PYTHONPATH=./src python -m telegram.login
```

### 5) Start the local model server (llama.cpp)

Ensure you have a **GGUF** model file and a working `llama-cpp-python` install. Then:

```bash
./start_model.sh
# or run as a systemd service; see DEPLOYMENT.md
```

### 6) Start the app

```bash
./start_bot.sh
# or: PYTHONPATH=./src uvicorn core.main:app --host 127.0.0.1 --port 8000
```

### 7) Check status & try the API (HTTP Basic auth)

`ADMIN_USER` / `ADMIN_PASS` protect all endpoints.

```bash
curl -u admin:changeme http://127.0.0.1:8000/status
```

Key endpoints (see source for full list):
- `GET /status`
- `POST /control/pause`  · `POST /control/resume`
- `POST /send_message` with JSON `{"chat_id": "...", "text": "..."}`
- `GET/POST/PUT/DELETE /personas` · `GET/POST/DELETE /schedules` · `GET/POST/DELETE /overrides`
- `GET /logs?limit=50&chat=<id>`

## 🧠 How it works (high level)

1. **Telethon** receives messages addressed to you.  
2. Recent context is pulled from **MariaDB** (`chat_log` table).  
3. A persona is selected via **time schedule + overrides**.  
4. A system prompt is built in Russian by default, then a chat completion request is sent to the local **llama.cpp** server.  
5. The reply is posted back to Telegram and both messages are stored.

See **ARCHITECTURE.md** for details.

## 🔐 Security notes

- Admin API is protected by **HTTP Basic auth**; run behind a reverse proxy and/or on localhost.
- Treat `.env` as a secret; never commit it.
- See **SECURITY.md** and **PRIVACY.md** before deploying to the public Internet.

## 🧩 Contributing

Issues and PRs are welcome! Please read **CONTRIBUTING.md** and **CODE_OF_CONDUCT.md**.

## 📄 License

MIT © 2025 Boris Karaoglanov
