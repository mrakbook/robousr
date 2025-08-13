# Configuration

All configuration is provided via environment variables (no implicit `.env` auto‑loading inside the app). Use the provided scripts, systemd `EnvironmentFile`, or export vars in your shell.

## Telegram (Telethon)

| Variable       | Required | Description |
| -------------- | -------- | ----------- |
| `API_ID`       | ✅       | Telegram API ID from https://my.telegram.org |
| `API_HASH`     | ✅       | Telegram API hash |
| `SESSION_NAME` | ➖       | Session filename prefix (default: `robosession`) |
| `PHONE_NUMBER` | ➖       | Only used by the one‑time login helper |

## Database (MariaDB)

| Variable     | Default        | Description |
| ------------ | -------------- | ----------- |
| `DB_HOST`    | `localhost`    | DB host |
| `DB_PORT`    | `3306`         | DB port |
| `DB_NAME`    | `telegram_bot` | Database name |
| `DB_USER`    | `botuser`      | DB user |
| `DB_PASSWORD`| `botpassword`  | DB password |

**SQLAlchemy URL** is composed as:  
`mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}`

> Tables are **not** created automatically. Import `db/schema.sql` manually.

## Local LLM (llama.cpp HTTP server)

| Variable           | Default                      | Description |
| ------------------ | ---------------------------- | ----------- |
| `OPENAI_API_BASE`  | `http://127.0.0.1:8001/v1`  | Base URL of llama.cpp server |
| `OPENAI_API_KEY`   | `local-llama`               | Dummy key required by SDKs |
| `LLAMA_MODEL_NAME` | `saiga-llama3-8b`           | Model alias exposed by the server |

**Optional knobs** (used by `start_model.sh`):

| Variable          | Default                      | Description |
| ----------------- | ---------------------------- | ----------- |
| `LLAMA_MODEL_PATH`| `./models/model-q4_K.gguf`   | Path to a GGUF model |
| `LLAMA_THREADS`   | `4`                           | CPU threads for inference |
| `LLAMA_HOST`      | `127.0.0.1`                   | Bind host |
| `LLAMA_PORT`      | `8001`                        | Bind port |

## FastAPI app

| Variable     | Default     | Description |
| ------------ | ----------- | ----------- |
| `APP_HOST`   | `127.0.0.1` | Host when using `start_bot.sh` |
| `APP_PORT`   | `8000`      | Port when using `start_bot.sh` |
| `ADMIN_USER` | `admin`     | HTTP Basic username (or `DASHBOARD_USER`) |
| `ADMIN_PASS` | `changeme`  | HTTP Basic password (or `DASHBOARD_PASS`) |

## Example `.env`

```ini
# Telegram
API_ID=123456
API_HASH=abcdef1234567890abcdef1234567890
SESSION_NAME=robosession
PHONE_NUMBER=+10000000000

# DB
DB_HOST=localhost
DB_PORT=3306
DB_NAME=telegram_bot
DB_USER=botuser
DB_PASSWORD=botpassword

# LLM
OPENAI_API_BASE=http://127.0.0.1:8001/v1
OPENAI_API_KEY=local-llama
LLAMA_MODEL_NAME=saiga-llama3-8b

LLAMA_MODEL_PATH=./models/model-q4_K.gguf
LLAMA_THREADS=4
LLAMA_HOST=127.0.0.1
LLAMA_PORT=8001

# App
APP_HOST=127.0.0.1
APP_PORT=8000
ADMIN_USER=admin
ADMIN_PASS=changeme
```
