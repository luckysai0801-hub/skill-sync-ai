"""
services/skill_gap.py - Skill gap analysis and score simulation.

Compares required job skills vs candidate's existing skills to identify:
  • Missing skills list
  • Simulated improved score if all missing skills were added
  • Skill demand weight (used for interview probability)
"""

from typing import List, Tuple, Dict
from .matching_engine import compute_skill_overlap


# Popularity / demand weight per skill (higher = more in demand)
SKILL_DEMAND = {
    "python": 0.95,      "javascript": 0.92,    "typescript": 0.88,
    "react": 0.90,       "node.js": 0.85,        "aws": 0.90,
    "docker": 0.87,      "kubernetes": 0.85,     "machine learning": 0.88,
    "deep learning": 0.86, "sql": 0.80,          "postgresql": 0.78,
    "fastapi": 0.75,     "django": 0.77,         "tensorflow": 0.82,
    "pytorch": 0.84,     "scikit-learn": 0.80,   "pandas": 0.78,
    "numpy": 0.75,       "git": 0.72,            "linux": 0.70,
    "java": 0.82,        "spring boot": 0.78,    "microservices": 0.80,
    "rest api": 0.78,    "graphql": 0.72,        "mongodb": 0.75,
    "redis": 0.72,       "kafka": 0.74,          "airflow": 0.70,
    "llm": 0.90,         "generative ai": 0.92,  "langchain": 0.88,
    "gcp": 0.82,         "azure": 0.80,          "spark": 0.76,
}

DEFAULT_DEMAND = 0.65   # demand weight for skills not in above dict


def get_skill_demand_weight(skills: List[str]) -> float:
    """
    Compute average skill demand weight for a list of skills.
    Returns 0–1 float.
    """
    if not skills:
        return DEFAULT_DEMAND
    weights = [SKILL_DEMAND.get(s.lower(), DEFAULT_DEMAND) for s in skills]
    return round(sum(weights) / len(weights), 4)


def analyze_skill_gap(
    candidate_skills: List[str],
    required_skills: List[str],
    current_final_score: float,
) -> Dict:
    """
    Compare candidate_skills vs required_skills.
    Returns missing skills and a simulated score if those skills were added.

    Simulation strategy:
      • Add all missing skills to candidate set
      • Recompute skill_overlap (now ~100%)
      • Gain = (new_overlap - old_overlap) × weight_of_skill_component (0.20)
      • simulated_score = current_score + gain (capped at 100)
    """
    c_set = set(s.lower() for s in candidate_skills)
    r_set = set(s.lower() for s in required_skills)

    missing = sorted(list(r_set - c_set))

    # Current skill overlap
    current_overlap = compute_skill_overlap(list(c_set), list(r_set))

    # Simulated skill overlap after adding missing skills
    simulated_skills = list(c_set | r_set)
    simulated_overlap = compute_skill_overlap(simulated_skills, list(r_set))

    # Score improvement from skill component
    skill_gain = (simulated_overlap - current_overlap) * 0.20
    simulated_score = round(min(100.0, current_final_score + skill_gain), 2)

    # Skill demand weight for missing skills
    demand_weight = get_skill_demand_weight(missing) if missing else get_skill_demand_weight(list(r_set))

    return {
        "missing_skills":      missing,
        "current_score":       round(current_final_score, 2),
        "simulated_score":     simulated_score,
        "skill_demand_weight": demand_weight,
    }
