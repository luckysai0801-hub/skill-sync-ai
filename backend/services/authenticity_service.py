"""
services/authenticity_service.py - Lightweight heuristic authenticity detector.

This module provides `assess_authenticity(text, skills, resume_score)` which
returns a dict with keys:
  - authenticity_score: float 0-100 (higher = more likely real)
  - authenticity_label: 'real' or 'fake'
  - authenticity_explanation: human-readable reasoning

The implementation is intentionally lightweight and deterministic so it runs
quickly without heavy ML dependencies. It combines several heuristics:
  - document length
  - token diversity
  - ratio of alphabetic characters
  - overlap between listed skills and text
  - the existing resume quality score (if available)

These heuristics give a reasonable signal for demo/test purposes; production
should replace with a trained model or external verification service.
"""
from typing import List, Dict
import re

_WORD_RE = re.compile(r"\b[a-zA-Z]{2,}\b")


def _alpha_ratio(text: str) -> float:
    chars = [c for c in text if c.isalpha()]
    if not text:
        return 0.0
    return len(chars) / max(1, len(text))


def _token_diversity(text: str) -> float:
    toks = [t.lower() for t in re.findall(r"\w+", text) if t.strip()]
    if not toks:
        return 0.0
    unique = len(set(toks))
    return unique / len(toks)


def assess_authenticity(text: str, skills: List[str] | None = None, resume_score: float | None = None) -> Dict:
    """Return a small dict describing authenticity assessment."""
    if skills is None:
        skills = []

    length = len(text or "")
    alpha = _alpha_ratio(text)
    diversity = _token_diversity(text)
    word_count = len(_WORD_RE.findall(text or ""))

    score = 50.0

    # Document length: very short resumes are suspicious
    if length < 200:
        score -= 25
    elif length < 500:
        score -= 10
    else:
        score += 5

    # Alpha ratio: lots of weird chars reduces score
    if alpha < 0.6:
        score -= 15
    elif alpha > 0.85:
        score += 5

    # Token diversity: low diversity -> generated or copied garbage
    if diversity < 0.25:
        score -= 20
    elif diversity < 0.45:
        score -= 5
    else:
        score += 5

    # Word count too low
    if word_count < 50:
        score -= 20

    # Skills overlap: if listed skills appear in text, that's a positive signal
    found = 0
    lower = (text or "").lower()
    for s in skills:
        if s and s.lower() in lower:
            found += 1
    if skills:
        skill_ratio = found / max(1, len(skills))
    else:
        skill_ratio = 0.0
    score += skill_ratio * 15.0

    # Use resume quality signal if provided
    if resume_score is not None:
        # resume_score is 0-100; map to -10..+10 impact
        score += (resume_score - 50.0) * 0.2

    # Clamp
    score = max(0.0, min(100.0, round(score, 2)))

    label = "real" if score >= 60.0 else "fake"

    # Explanation bullets
    parts = []
    parts.append(f"Length: {length} chars")
    parts.append(f"Alpha ratio: {alpha:.2f}")
    parts.append(f"Token diversity: {diversity:.2f}")
    parts.append(f"Words: {word_count}")
    parts.append(f"Skill match: {found}/{len(skills) if skills else 0}")
    if resume_score is not None:
        parts.append(f"Resume quality score: {resume_score}")

    explanation = "; ".join(parts)

    return {
        "authenticity_score": score,
        "authenticity_label": label,
        "authenticity_explanation": explanation,
    }
