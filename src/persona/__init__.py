"""
Persona package for RoboUsr.

Exports:
- get_active_persona: choose a persona based on chat/user/time rules.
- persona_to_system_message: convert a persona profile into a system prompt string.
- Pydantic schemas for API I/O.
"""

from .manager import get_active_persona, persona_to_system_message
from .schemas import (
    PersonaProfileCreate,
    PersonaProfileRead,
    PersonaScheduleCreate,
    PersonaScheduleRead,
    PersonaOverrideCreate,
    PersonaOverrideRead,
)

__all__ = [
    "get_active_persona",
    "persona_to_system_message",
    "PersonaProfileCreate",
    "PersonaProfileRead",
    "PersonaScheduleCreate",
    "PersonaScheduleRead",
    "PersonaOverrideCreate",
    "PersonaOverrideRead",
]
