"""
RoboUsr · Core package.

Contains:
- config: environment-driven settings (DB URL, Telegram API keys, AI server info)
- db: SQLAlchemy engine, session factory, and ORM models
- main: FastAPI application (startup/shutdown hooks, REST endpoints)

Note: The database schema is NOT created by code. Import schema.sql manually.
"""

__all__ = ["config", "db"]
__version__ = "0.1.0"
