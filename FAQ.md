# FAQ

**Q: Is this a bot account?**  
A: No. It's a *userbot* that controls your personal account via Telethon.

**Q: Which language does it reply in?**  
A: By default the system prompt is in Russian. You can change persona descriptions to influence language/style.

**Q: Can I use SQLite instead of MariaDB?**  
A: The code ships with a MariaDB schema and connection string. You can adapt `core/config.py` and `core/db.py` to use SQLite, but that is not supported out of the box.

**Q: What models does it support?**  
A: Any model you can serve via `llama-cpp-python` as an OpenAI‑compatible endpoint. Adjust `LLAMA_MODEL_NAME` to the alias you expose.

**Q: How do I stop it from auto‑replying for a while?**  
A: Call `POST /control/pause` (and later `POST /control/resume`).

**Q: Where are messages stored?**  
A: In `chat_log` (MariaDB). It stores the text, sender id, chat id, timestamp, and whether it was a bot message. See **PRIVACY.md**.
