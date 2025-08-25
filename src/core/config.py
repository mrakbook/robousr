"""
Centralized configuration for RoboUsr.

Values are read from environment variables. No .env auto-loading is performed
so you can use a systemd EnvironmentFile or export in shell scripts.

Required/Useful variables:
- API_ID, API_HASH, SESSION_NAME, (optional) PHONE_NUMBER
- DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
- OPENAI_API_BASE, OPENAI_API_KEY, LLAMA_MODEL_NAME
- ADMIN_USER, ADMIN_PASS (or legacy DASHBOARD_USER, DASHBOARD_PASS)
"""

import os

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSION_NAME = os.getenv("SESSION_NAME", "robosession")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "telegram_bot")
DB_USER = os.getenv("DB_USER", "botuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "botpassword")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "http://127.0.0.1:8001/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "local-llama")
LLAMA_MODEL_NAME = os.getenv("LLAMA_MODEL_NAME", "saiga-llama3-8b")

ADMIN_USER = os.getenv("ADMIN_USER") or os.getenv("DASHBOARD_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS") or os.getenv("DASHBOARD_PASS", "changeme")
