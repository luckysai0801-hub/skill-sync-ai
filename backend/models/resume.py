"""
models/resume.py - Resume model storing parsed data and embeddings.
Embeddings are stored as JSON (list of floats) in a Text column.
"""

from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Parsed content (anonymized – no name/age/gender)
    raw_text = Column(Text, nullable=False)
    skills = Column(JSON, default=list)          # list of strings
    years_experience = Column(Float, default=0.0)
    education = Column(String, default="")
    location_city = Column(String, default="")
    location_state = Column(String, default="")
    expected_salary = Column(Float, default=0.0)

    # AI vector embedding stored as JSON array
    embedding = Column(JSON, nullable=True)      # list[float] – 384-dim

    # Resume quality score
    resume_score = Column(Float, default=0.0)
    improvement_suggestions = Column(JSON, default=list)
    # Authenticity detection
    authenticity_score = Column(Float, nullable=True)  # 0-100 (higher = more likely real)
    authenticity_label = Column(String, default="unknown")  # 'real' or 'fake' or 'unknown'
    authenticity_explanation = Column(Text, default="")

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="resumes")
    matches = relationship("Match", back_populates="resume", cascade="all, delete-orphan")
