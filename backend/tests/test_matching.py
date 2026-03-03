import pytest
import sys, os
# Ensure backend package root is on sys.path for tests
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from services.matching_engine import (
    compute_skill_overlap,
    compute_experience_score,
    compute_location_score,
    compute_salary_score,
    compute_match_scores,
)
from services.skill_gap import analyze_skill_gap


def test_skill_overlap_basic():
    # exact match
    s = compute_skill_overlap(["python", "django"], ["python", "django"]) 
    assert s == 100.0

    # partial match weighted
    s2 = compute_skill_overlap(["python"], ["python", "django"]) 
    assert 40.0 <= s2 <= 100.0


def test_experience_score():
    assert compute_experience_score(5, 3) == 100.0
    assert compute_experience_score(1, 2) == pytest.approx(50.0)


def test_location_score():
    assert compute_location_score("Seattle", "WA", "Seattle", "WA", False) == 100.0
    assert compute_location_score("Portland", "OR", "Seattle", "WA", False) == 30.0
    assert compute_location_score("Any", "Any", "", "", True) == 100.0


def test_salary_score():
    assert compute_salary_score(90000, 80000, 100000) == 100.0
    assert compute_salary_score(120000, 80000, 100000) == 50.0
    assert compute_salary_score(0, 80000, 100000) == 80.0


def test_full_match_scores_dummy_embeddings():
    # Use simple embeddings (lists) where cosine_similarity fallback will compute dot
    emb_a = [1.0, 0.0, 0.0]
    emb_b = [1.0, 0.0, 0.0]
    scores = compute_match_scores(
        resume_embedding=emb_a,
        job_embedding=emb_b,
        candidate_skills=["python", "django"],
        required_skills=["python", "django"],
        candidate_exp=4,
        required_exp=3,
        candidate_city="Seattle",
        candidate_state="WA",
        candidate_salary=95000,
        job_city="Seattle",
        job_state="WA",
        is_remote=False,
        salary_min=90000,
        salary_max=100000,
    )
    assert "final_score" in scores
    assert scores["final_score"] <= 100.0


def test_skill_gap_simulation():
    gap = analyze_skill_gap(["python"], ["python", "aws"], 60.0)
    assert "missing_skills" in gap
    assert "simulated_score" in gap
