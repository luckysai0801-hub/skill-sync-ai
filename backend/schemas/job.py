"""
schemas/job.py - Pydantic schemas for job request/response validation.
"""

from pydantic import BaseModel
from typing import List, Optional

# (no changes just keep to align) 

class JobCreate(BaseModel):
    """Schema used when an employer posts a new job."""
    employer_id: int
    title: str
    description: str
    required_skills: List[str] = []
    required_experience: float = 0.0
    salary_min: float = 0.0
    salary_max: float = 0.0
    location_city: str = ""
    location_state: str = ""
    is_remote: bool = False


class JobOut(BaseModel):
    """Schema returned to the client."""
    id: int
    employer_id: int
    title: str
    description: str
    required_skills: List[str]
    required_experience: float
    salary_min: float
    salary_max: float
    location_city: str
    location_state: str
    is_remote: bool

    class Config:
        from_attributes = True
