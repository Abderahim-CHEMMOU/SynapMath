from enum import Enum
from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel


class Difficulty(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class RegisterRequest(BaseModel):
    user_id: str
    name: str
    password: str
    level: Optional[str] = None


class LoginRequest(BaseModel):
    user_id: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class Skill(BaseModel):
    id: str
    name: str
    description: Optional[str] = None


class Exercise(BaseModel):
    id: str
    skill_id: str
    skill_external_id: Optional[str] = None
    prompt: str
    difficulty: Difficulty
    options: Optional[List[str]] = None
    answer: Optional[str] = None
    solution: Optional[str] = None


class ExerciseCreate(BaseModel):
    skill_id: str
    skill_external_id: Optional[str] = None
    exercise_id: Optional[str] = None
    prompt: str
    difficulty: Difficulty
    options: Optional[List[str]] = None
    answer: Optional[str] = None
    solution: Optional[str] = None


class InteractionCreate(BaseModel):
    user_id: str
    exercise_id: str
    skill_id: str
    correct: bool
    timestamp: Optional[datetime] = None


class Interaction(InteractionCreate):
    id: str
    probability_before: Optional[float] = None
    probability_after: Optional[float] = None


class RecommendationResponse(BaseModel):
    user_id: str
    exercise_id: str
    skill_id: str
    skill_external_id: Optional[str] = None
    prompt: str
    options: Optional[List[str]] = None
    answer: Optional[str] = None
    probability: float
    difficulty: Difficulty
    mastery: bool = False


class UserProfile(BaseModel):
    id: str
    user_id: str
    name: str
    level: Optional[str] = None
    created_at: datetime


class ProgressSnapshot(BaseModel):
    user_id: str
    mastered_skills: List[str]
    struggling_skills: List[str]
    last_updated: datetime
