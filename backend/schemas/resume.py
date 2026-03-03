"""
schemas/resume.py - Pydantic schemas for resume request/response validation.
"""

from pydantic import BaseModel
from typing import List, Optional


class ResumeCreate(BaseModel):
    """Schema sent when creating a resume manually (for demo data seeding)."""
    user_id: int
    raw_text: str
    skills: List[str] = []
    years_experience: float = 0.0
    education: str = ""
    location_city: str = ""
    location_state: str = ""
    expected_salary: float = 0.0


class ResumeOut(BaseModel):
    """Schema returned to the client."""
    id: int
    user_id: int
    skills: List[str]
    years_experience: float
    education: str
    location_city: str
    location_state: str
    expected_salary: float
    resume_score: float
    improvement_suggestions: List[str]
    # Authenticity fields
    authenticity_score: Optional[float] = None
    authenticity_label: Optional[str] = None
    authenticity_explanation: Optional[str] = None

    class Config:
        from_attributes = True


class ResumeScoreOut(BaseModel):
    """Score + suggestions for the resume quality endpoint."""
    resume_id: int
    resume_score: float
    improvement_suggestions: List[str]
