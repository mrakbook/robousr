from __future__ import annotations

from typing import Optional

try:
    from pydantic import BaseModel, ConfigDict
    _HAS_PYDANTIC_V2 = True
except Exception:
    from pydantic import BaseModel
    ConfigDict = None
    _HAS_PYDANTIC_V2 = False


class _FromAttributesMixin:
    """Cross-version support for returning ORM objects from FastAPI."""
    if _HAS_PYDANTIC_V2:
        model_config = ConfigDict(from_attributes=True)
    else:
        class Config:
            orm_mode = True


class PersonaProfileCreate(BaseModel):
    name: str
    description: str = ""
    tone_formal: int = 0
    tone_funny: int = 0
    tone_angry: int = 0


class PersonaProfileRead(_FromAttributesMixin, BaseModel):
    id: int
    name: str
    description: str
    tone_formal: int
    tone_funny: int
    tone_angry: int


class PersonaScheduleCreate(BaseModel):
    profile_id: int
    start_time: str
    end_time: str
    dow_mask: Optional[int] = 127


class PersonaScheduleRead(_FromAttributesMixin, BaseModel):
    id: int
    profile_id: int
    start_time: str
    end_time: str
    dow_mask: Optional[int] = 127


class PersonaOverrideCreate(BaseModel):
    profile_id: int
    chat_id: Optional[str] = None
    user_id: Optional[str] = None


class PersonaOverrideRead(_FromAttributesMixin, BaseModel):
    id: int
    profile_id: int
    chat_id: Optional[str] = None
    user_id: Optional[str] = None
