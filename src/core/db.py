"""
Database layer for RoboUsr (SQLAlchemy ORM).

IMPORTANT: This module does NOT create tables automatically.
Import and apply schema.sql to your MariaDB database yourself.
"""

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
)
from sqlalchemy.orm import declarative_base, sessionmaker

from core.config import DATABASE_URL

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

Base = declarative_base()


class PersonaProfile(Base):
    __tablename__ = "persona_profile"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, default="")
    tone_formal = Column(Integer, default=0)
    tone_funny = Column(Integer, default=0)
    tone_angry = Column(Integer, default=0)


class PersonaSchedule(Base):
    __tablename__ = "persona_schedule"

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, nullable=False)
    start_time = Column(String(5), nullable=False)
    end_time = Column(String(5), nullable=False)
    dow_mask = Column(Integer, nullable=True)


class PersonaOverride(Base):
    __tablename__ = "persona_override"

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, nullable=False)
    chat_id = Column(String(20), nullable=True)
    user_id = Column(String(20), nullable=True)


class ChatLog(Base):
    __tablename__ = "chat_log"

    id = Column(Integer, primary_key=True)
    chat_id = Column(String(20))
    sender_id = Column(String(20))
    message_text = Column(Text)
    timestamp = Column(DateTime)
    is_bot = Column(Boolean, default=False)
