"""
schemas/match.py - Pydantic schemas for match results and score breakdowns.
"""

from pydantic import BaseModel
from typing import List


class ScoreBreakdown(BaseModel):
    """Explainable AI score breakdown for a single match."""
    final_score: float
    semantic_score: float
    skill_overlap: float
    experience_score: float
    location_score: float
    salary_score: float


class MatchOut(BaseModel):
    """Full match response including job/resume metadata."""
    match_id: int
    resume_id: int
    job_id: int
    job_title: str = ""
    scores: ScoreBreakdown
    interview_probability: float
    missing_skills: List[str]

    class Config:
        from_attributes = True


class SkillGapOut(BaseModel):
    """Response for the skill gap endpoint."""
    candidate_id: int
    job_id: int
    missing_skills: List[str]
    current_score: float
    simulated_score: float          # score if missing skills were added
    skill_demand_weight: float


class DashboardOut(BaseModel):
    """Recruiter analytics dashboard response."""
    job_id: int
    job_title: str
    total_candidates: int
    average_score: float
    top_candidates: List[MatchOut]
    skill_distribution: dict
    experience_distribution: dict
