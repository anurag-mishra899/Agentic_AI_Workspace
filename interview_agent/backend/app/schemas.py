from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# Auth Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Session Schemas
class SessionCreate(BaseModel):
    persona: str  # friendly, neutral, aggressive, faang, startup
    depth_mode: str  # surface, interview_ready, expert
    domains: List[str]  # coding, system_design, ml
    declared_weak_areas: Optional[List[str]] = None


class SessionResponse(BaseModel):
    id: int
    user_id: int
    persona: str
    depth_mode: str
    domains: List[str]
    status: str
    started_at: datetime
    ended_at: Optional[datetime]
    declared_weak_areas: Optional[List[str]]

    class Config:
        from_attributes = True


class SessionDetailResponse(SessionResponse):
    resume_text: Optional[str]
    transcript_summary: Optional[str]
    feedback_report: Optional[str]
    detected_weak_areas: Optional[List[str]]
    scores: Optional[dict]


# Resume Schemas
class ResumeParseResponse(BaseModel):
    text: str
    parsed_at: datetime


# Skill Schemas
class SkillResponse(BaseModel):
    domain: str
    topic: str
    subtopic: Optional[str]
    score: Optional[float]
    status: str
    confidence: float
    times_assessed: int
    updated_at: datetime

    class Config:
        from_attributes = True


# Feedback Schemas
class FeedbackResponse(BaseModel):
    session_id: int
    report_markdown: str
    generated_at: datetime
