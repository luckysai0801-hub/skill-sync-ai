"""
services/resume_scorer.py - Resume quality scoring.

Scores a resume 0–100 based on:
  • Measurable achievements   – numbers, %, $ metrics detected via regex  (25 pts)
  • Action verb usage         – leadership/action words at sentence start  (25 pts)
  • Skill clarity             – number of recognized skills                (25 pts)
  • Keyword density           – tech keyword frequency in text             (25 pts)

Returns score + specific improvement suggestions.
"""

import re
from typing import List, Dict, Tuple

# ─── Scoring constants ─────────────────────────────────────────────────────────
MAX_ACHIEVEMENTS = 25
MAX_VERBS        = 25
MAX_SKILLS       = 25
MAX_KEYWORDS     = 25

# Common resume action verbs
ACTION_VERBS = [
    "achieved", "built", "created", "designed", "developed", "engineered",
    "implemented", "improved", "increased", "launched", "led", "managed",
    "optimized", "reduced", "scaled", "shipped", "streamlined", "trained",
    "deployed", "automated", "analyzed", "architected", "collaborated",
    "delivered", "established", "generated", "integrated", "maintained",
    "migrated", "modernized", "orchestrated", "refactored", "supervised",
]

# Regex: detect numeric metrics (e.g., "30%", "$2M", "10x", "reduced by 50")
_METRIC_PATTERN = re.compile(
    r"(\$[\d,]+[MKB]?|\d+[%xX]|\d+\s*(times|x|percent|pts?|points?)|\d{2,})",
    re.IGNORECASE
)


def _score_achievements(text: str) -> Tuple[float, List[str]]:
    """Score based on measurable achievement indicators."""
    matches = _METRIC_PATTERN.findall(text)
    count = len(matches)
    suggestions = []
    if count == 0:
        score = 0
        suggestions.append("Add measurable achievements (e.g., 'increased sales by 30%')")
    elif count < 3:
        score = MAX_ACHIEVEMENTS * 0.5
        suggestions.append("Add more quantified results – aim for 5+ metric-backed achievements")
    elif count < 6:
        score = MAX_ACHIEVEMENTS * 0.75
    else:
        score = MAX_ACHIEVEMENTS
    return score, suggestions


def _score_action_verbs(text: str) -> Tuple[float, List[str]]:
    """Score based on strong action verb usage."""
    words = re.findall(r"\b\w+\b", text.lower())
    found = [v for v in ACTION_VERBS if v in words]
    unique_count = len(set(found))
    suggestions = []
    if unique_count == 0:
        score = 0
        suggestions.append("Start bullet points with strong action verbs (e.g., 'Built', 'Led', 'Optimized')")
    elif unique_count < 5:
        score = MAX_VERBS * 0.5
        suggestions.append("Use more varied action verbs to showcase impact")
    elif unique_count < 10:
        score = MAX_VERBS * 0.75
    else:
        score = MAX_VERBS
    return score, suggestions


def _score_skill_clarity(skills: List[str]) -> Tuple[float, List[str]]:
    """Score based on number of recognized skills."""
    count = len(skills)
    suggestions = []
    if count == 0:
        score = 0
        suggestions.append("Add a dedicated 'Skills' section with specific technologies")
    elif count < 5:
        score = MAX_SKILLS * 0.4
        suggestions.append("List more technical skills (aim for 8–15 relevant skills)")
    elif count < 10:
        score = MAX_SKILLS * 0.75
    else:
        score = MAX_SKILLS
    return score, suggestions


def _score_keyword_density(text: str) -> Tuple[float, List[str]]:
    """Score based on tech keyword presence relative to document length."""
    words = text.lower().split()
    total = max(len(words), 1)
    tech_words = ["api", "software", "system", "database", "cloud", "service",
                  "engineer", "developer", "platform", "architecture", "pipeline",
                  "framework", "library", "model", "algorithm", "performance"]
    count = sum(1 for w in words if w in tech_words)
    density = (count / total) * 100
    suggestions = []
    if density < 1:
        score = MAX_KEYWORDS * 0.3
        suggestions.append("Include more industry-specific technical keywords in your resume")
    elif density < 2:
        score = MAX_KEYWORDS * 0.6
    elif density < 4:
        score = MAX_KEYWORDS * 0.85
    else:
        score = MAX_KEYWORDS
    return score, suggestions


def score_resume(text: str, skills: List[str]) -> Dict:
    """
    Main entrypoint: score a resume and return structured feedback.
    Returns { resume_score: float, improvement_suggestions: List[str] }
    """
    s1, sg1 = _score_achievements(text)
    s2, sg2 = _score_action_verbs(text)
    s3, sg3 = _score_skill_clarity(skills)
    s4, sg4 = _score_keyword_density(text)

    total = round(s1 + s2 + s3 + s4, 2)
    suggestions = sg1 + sg2 + sg3 + sg4

    if not suggestions:
        suggestions.append("Great resume! Consider tailoring it further for each job application.")

    return {
        "resume_score":            total,
        "improvement_suggestions": suggestions,
        "breakdown": {
            "achievements_score":  round(s1, 2),
            "action_verbs_score":  round(s2, 2),
            "skill_clarity_score": round(s3, 2),
            "keyword_density_score": round(s4, 2),
        }
    }
