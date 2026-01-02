from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class UserSkill(Base):
    __tablename__ = "user_skills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Skill identification
    domain = Column(String, nullable=False)  # coding, system_design, ml
    topic = Column(String, nullable=False)  # e.g., dynamic_programming, scaling
    subtopic = Column(String, nullable=True)  # e.g., 1d_dp, horizontal_scaling

    # Skill assessment
    score = Column(Float, nullable=True)  # 0.0 to 1.0
    status = Column(String, default="unknown")  # weak, improving, strong, unknown
    confidence = Column(Float, default=0.0)  # How confident system is in assessment

    # Tracking
    times_assessed = Column(Integer, default=0)
    last_session_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="skills")

    def __repr__(self):
        return f"<UserSkill(user_id={self.user_id}, domain={self.domain}, topic={self.topic}, status={self.status})>"
