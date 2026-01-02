from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class InterviewSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Session configuration
    persona = Column(String, nullable=False)  # friendly, neutral, aggressive, faang, startup
    depth_mode = Column(String, nullable=False)  # surface, interview_ready, expert
    domains = Column(JSON, nullable=False)  # List of domains: coding, system_design, ml

    # Candidate inputs
    resume_text = Column(Text, nullable=True)
    declared_weak_areas = Column(JSON, nullable=True)  # List of weak area strings

    # Session state
    status = Column(String, default="active")  # active, completed, terminated
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

    # Session results
    transcript_summary = Column(Text, nullable=True)
    feedback_report = Column(Text, nullable=True)
    detected_weak_areas = Column(JSON, nullable=True)
    scores = Column(JSON, nullable=True)  # Domain/topic scores

    # Relationship
    user = relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<InterviewSession(id={self.id}, user_id={self.user_id}, status={self.status})>"
