from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db import Base
from app.schemas import Difficulty


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    external_id = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)

    exercises = relationship("Exercise", back_populates="skill", cascade="all, delete-orphan")


class Exercise(Base):
    __tablename__ = "exercises"
    __table_args__ = (UniqueConstraint("skill_id", "difficulty", "prompt", name="uq_exercise_prompt"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    exercise_id = Column(String(64), unique=True, nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    prompt = Column(Text, nullable=False)
    difficulty = Column(Enum(Difficulty, name="difficulty_enum"), nullable=False)
    options = Column(Text, nullable=True)  # JSON serialised as text for simplicity
    answer = Column(String(255), nullable=False)
    solution = Column(Text, nullable=True)

    skill = relationship("Skill", back_populates="exercises")
    interactions = relationship("Interaction", back_populates="exercise", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(64), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    level = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    interactions = relationship("Interaction", back_populates="user", cascade="all, delete-orphan")
    credential = relationship("UserCredential", back_populates="user", uselist=False, cascade="all, delete-orphan")
    tokens = relationship("AuthToken", back_populates="user", cascade="all, delete-orphan")


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False)
    correct = Column(Boolean, nullable=False)
    probability_before = Column(Float, nullable=True)
    probability_after = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="interactions")
    exercise = relationship("Exercise", back_populates="interactions")


class UserCredential(Base):
    __tablename__ = "user_credentials"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    password_hash = Column(String(255), nullable=False)

    user = relationship("User", back_populates="credential")


class AuthToken(Base):
    __tablename__ = "auth_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(128), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="tokens")
