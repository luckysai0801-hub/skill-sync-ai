"""
models/job.py - Job posting model for employers.
"""

from sqlalchemy import Column, Integer, String, Text, Float, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    employer_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    required_skills = Column(JSON, default=list)     # list of strings
    required_experience = Column(Float, default=0.0) # years
    salary_min = Column(Float, default=0.0)
    salary_max = Column(Float, default=0.0)
    location_city = Column(String, default="")
    location_state = Column(String, default="")
    is_remote = Column(Boolean, default=False)

    # AI vector embedding stored as JSON array
    embedding = Column(JSON, nullable=True)          # list[float] – 384-dim

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    employer = relationship("User", back_populates="jobs")
    matches = relationship("Match", back_populates="job", cascade="all, delete-orphan")
