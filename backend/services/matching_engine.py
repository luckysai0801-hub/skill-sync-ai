"""
services/matching_engine.py - Core AI matching engine.

Computes a weighted final score (0–100) using:
  • Semantic score    (0.40) – cosine similarity of embeddings
  • Skill overlap     (0.20) – Jaccard-style overlap of skill sets
  • Experience score  (0.15) – ratio of candidate vs required experience
  • Location score    (0.15) – exact/state/remote/different match
  • Salary score      (0.10) – whether expected salary is within range

Final Score = 0.4×Semantic + 0.2×SkillOverlap + 0.15×Exp + 0.15×Loc + 0.1×Salary
All sub-scores are 0–100.
"""

from typing import List, Dict, Any
from .embedding_service import cosine_similarity


# ─── Weights ──────────────────────────────────────────────────────────────────
W_SEMANTIC    = 0.40
W_SKILL       = 0.20
W_EXPERIENCE  = 0.15
W_LOCATION    = 0.15
W_SALARY      = 0.10




def compute_skill_overlap(candidate_skills: List[str], required_skills: List[str]) -> float:
    """
    Compute skill overlap as intersection / union (Jaccard similarity), scaled to 0–100.
    If no required skills, return 100 (no penalty).
    """
    if not required_skills:
        return 100.0
    c_set = set(s.lower() for s in candidate_skills)
    r_set = set(s.lower() for s in required_skills)
    if not r_set:
        return 100.0
    intersection = len(c_set & r_set)
    # Use required-skill recall: what % of required skills does candidate have?
    overlap = (intersection / len(r_set)) * 100.0
    return round(min(100.0, overlap), 2)


def compute_experience_score(candidate_exp: float, required_exp: float) -> float:
    """
    Experience score:
      candidate_exp >= required_exp → 100
      else → (candidate_exp / required_exp) × 100
    """
    if required_exp <= 0:
        return 100.0
    if candidate_exp >= required_exp:
        return 100.0
    return round((candidate_exp / required_exp) * 100.0, 2)


def compute_location_score(
    candidate_city: str, candidate_state: str,
    job_city: str, job_state: str, is_remote: bool
) -> float:
    """
    Location score:
      Remote job → 100
      Exact city match → 100
      Same state → 70
      Different state → 30
    """
    if is_remote:
        return 100.0
    if candidate_city.strip().lower() == job_city.strip().lower() and job_city:
        return 100.0
    if candidate_state.strip().lower() == job_state.strip().lower() and job_state:
        return 70.0
    return 30.0


def compute_salary_score(
    expected_salary: float, salary_min: float, salary_max: float
) -> float:
    """
    Salary score:
      Within range → 100
      Outside range → 50
      No salary expectation → 80 (neutral)
    """
    if expected_salary <= 0:
        return 80.0
    if salary_min <= expected_salary <= salary_max:
        return 100.0
    return 50.0


def compute_match_scores(
    resume_embedding: List[float],
    job_embedding: List[float],
    candidate_skills: List[str],
    required_skills: List[str],
    candidate_exp: float,
    required_exp: float,
    candidate_city: str,
    candidate_state: str,
    candidate_salary: float,
    job_city: str,
    job_state: str,
    is_remote: bool,
    salary_min: float,
    salary_max: float,
) -> Dict[str, float]:
    """
    Compute all score components and the weighted final score.
    Returns a dict with all score fields (0–100 scale).
    """
    # 1. Semantic similarity
    cos_sim = cosine_similarity(resume_embedding, job_embedding)
    semantic_score = round(cos_sim * 100.0, 2)

    # 2. Skill overlap
    skill_overlap = compute_skill_overlap(candidate_skills, required_skills)

    # 3. Experience score
    experience_score = compute_experience_score(candidate_exp, required_exp)

    # 4. Location score
    location_score = compute_location_score(
        candidate_city, candidate_state, job_city, job_state, is_remote
    )

    # 5. Salary score
    salary_score = compute_salary_score(candidate_salary, salary_min, salary_max)

    # 6. Weighted final score
    final_score = (
        W_SEMANTIC   * semantic_score +
        W_SKILL      * skill_overlap +
        W_EXPERIENCE * experience_score +
        W_LOCATION   * location_score +
        W_SALARY     * salary_score
    )
    final_score = round(min(100.0, final_score), 2)

    return {
        "final_score":       final_score,
        "semantic_score":    semantic_score,
        "skill_overlap":     skill_overlap,
        "experience_score":  experience_score,
        "location_score":    location_score,
        "salary_score":      salary_score,
    }
