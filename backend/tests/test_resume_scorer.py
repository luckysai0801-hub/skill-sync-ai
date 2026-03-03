import sys, os
# Ensure backend package root is on sys.path for tests
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from services.resume_scorer import score_resume


def test_resume_scorer_basic():
    text = "Developed a system that increased revenue by 30% and reduced costs by $2000. Built CI/CD pipelines."
    skills = ["python", "docker", "aws"]
    out = score_resume(text, skills)
    assert "resume_score" in out
    assert out["resume_score"] >= 0
