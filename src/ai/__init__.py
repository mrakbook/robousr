"""
RoboUsr AI package.

Exposes a simple interface to generate model replies via a local
llama.cpp OpenAI-compatible server.

Public API:
- generate_reply(persona_text, conversation_history, user_message) -> str | None
- build_messages(persona_text, history, user_message) -> list[dict]
- server_ok() -> bool
"""

from .engine import generate_reply, build_messages, server_ok

__all__ = ["generate_reply", "build_messages", "server_ok"]

__version__ = "0.1.0"
