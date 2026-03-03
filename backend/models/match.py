"""
models/match.py - Match table storing computed AI scores between resumes and jobs.
"""

from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)

    # Score components (all 0–100)
    final_score = Column(Float, default=0.0)
    semantic_score = Column(Float, default=0.0)
    skill_overlap = Column(Float, default=0.0)
    experience_score = Column(Float, default=0.0)
    location_score = Column(Float, default=0.0)
    salary_score = Column(Float, default=0.0)

    # Additional analytics
    interview_probability = Column(Float, default=0.0)
    missing_skills = Column(JSON, default=list)

    computed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    resume = relationship("Resume", back_populates="matches")
    job = relationship("Job", back_populates="matches")
