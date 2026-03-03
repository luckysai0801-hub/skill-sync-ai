"""
services/probability_estimator.py - Interview probability estimation.

Formula:
  Probability = 0.6 × Final Score + 0.4 × Skill Demand Weight

Both inputs are 0–100 (final_score) and 0–1 (skill_demand_weight scaled ×100).
Returns a percentage (0–100).
"""

from typing import List
from .skill_gap import get_skill_demand_weight


def estimate_interview_probability(
    final_score: float,
    required_skills: List[str],
) -> float:
    """
    Estimate interview call probability as a percentage.

    Args:
        final_score:      Weighted match score (0–100)
        required_skills:  Skills required by the job posting

    Returns:
        Probability (0–100 float)
    """
    # Skill demand weight: average market demand of required skills (0–1)
    demand_weight = get_skill_demand_weight(required_skills)

    # Scale demand weight to 0–100
    demand_score = demand_weight * 100.0

    # Weighted probability
    probability = 0.6 * final_score + 0.4 * demand_score
    return round(min(100.0, max(0.0, probability)), 2)
