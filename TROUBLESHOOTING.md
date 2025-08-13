# Troubleshooting

### 401 Unauthorized on API calls
- Provide `ADMIN_USER` / `ADMIN_PASS` via HTTP Basic: `curl -u user:pass ...`.
- Confirm the values in environment or systemd `EnvironmentFile`.

### Telegram client not authorized
- Run the one‑time login helper: `PYTHONPATH=./src python -m telegram.login`.
- Ensure `API_ID`, `API_HASH`, and `SESSION_NAME` are correct.

### llama.cpp server not reachable
- `OPENAI_API_BASE` must point at your local server, e.g. `http://127.0.0.1:8001/v1`.
- Start it with `./start_model.sh` or `systemctl status robousr-llama.service`.
- Check the `--model_alias` matches `LLAMA_MODEL_NAME`.

### Database errors (e.g., Unknown table)
- Import `db/schema.sql` before running the app.
- Check `DATABASE_URL` parts in `CONFIGURATION.md`.

### `uvicorn` or packages not found
- Activate your venv and ensure dependencies are installed.
- `pip install -U fastapi uvicorn telethon SQLAlchemy PyMySQL pydantic openai "llama-cpp-python[server]"`

### No replies from the bot
- See `/status` for `telegram_connected` and `ai_server_ok`.
- Ensure the bot is not paused (`POST /control/resume`).

### Time‑based persona not switching
- Verify `persona_schedule` times are `HH:MM` 24‑hour format.
- DOW mask uses bits **Mon=1<<0 ... Sun=1<<6**. Overnight intervals are supported.
