"""
services/resume_parser.py - Parses resume text to extract structured fields.

Extracts:
  • Skills        – matched against a predefined technology skill list + spaCy NER
  • Experience    – years extracted via regex patterns
  • Education     – degree keywords
  • Location      – city/state via spaCy GPE entities

Anonymization removes: Name (spaCy PERSON), Age (regex), Gender words.
"""

import re
import json
from typing import List, Tuple, Dict, Any

# spaCy is optional for quick runs. If unavailable we fall back to a simple
# regex-based parser that extracts skills, experience, and education.
_HAS_SPACY = False
try:
    import spacy  # type: ignore
    _HAS_SPACY = True
except Exception:
    _HAS_SPACY = False

_nlp = None

def _get_nlp():
    global _nlp
    if not _HAS_SPACY:
        return None
    if _nlp is None:
        try:
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            import subprocess, sys
            subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], check=True)
            _nlp = spacy.load("en_core_web_sm")
    return _nlp


# ─── Predefined skill taxonomy ─────────────────────────────────────────────────
SKILL_LIST = [
    # Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "kotlin", "swift", "ruby", "php", "scala", "r", "matlab", "sql",
    # Frameworks / Libraries
    "react", "angular", "vue", "node.js", "fastapi", "django", "flask",
    "spring boot", "express", "next.js", "nuxt.js", "svelte",
    "tensorflow", "pytorch", "keras", "scikit-learn", "xgboost", "lightgbm",
    "pandas", "numpy", "matplotlib", "seaborn", "plotly",
    # Databases
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "cassandra", "dynamodb", "sqlite", "neo4j",
    # Cloud / DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
    "terraform", "ansible", "jenkins", "github actions", "gitlab ci",
    "linux", "bash", "nginx", "apache",
    # AI / ML
    "machine learning", "deep learning", "nlp", "computer vision",
    "llm", "generative ai", "rag", "bert", "gpt", "hugging face",
    "sentence transformers", "openai", "langchain",
    # Data Engineering
    "spark", "hadoop", "kafka", "airflow", "dbt", "snowflake",
    "bigquery", "data warehouse", "etl",
    # Tools
    "git", "jira", "confluence", "figma", "postman", "swagger",
    "selenium", "pytest", "jest", "cypress",
    # Soft / Domain
    "agile", "scrum", "rest api", "graphql", "microservices",
    "system design", "data structures", "algorithms",
]

# ─── Gender / age anonymization words ─────────────────────────────────────────
_GENDER_WORDS = re.compile(
    r"\b(male|female|man|woman|he|she|his|her|mr\.?|mrs\.?|ms\.?)\b",
    re.IGNORECASE
)
_AGE_PATTERN = re.compile(r"\b(age[d]?\s*:?\s*\d{1,2}|\d{1,2}\s*years?\s*old)\b", re.IGNORECASE)


# ─── Experience extraction ─────────────────────────────────────────────────────
_EXP_PATTERNS = [
    re.compile(r"(\d+(?:\.\d+)?)\+?\s*years?\s*(?:of\s+)?(?:experience|exp)", re.IGNORECASE),
    re.compile(r"experience[:\s]+(\d+(?:\.\d+)?)\+?\s*years?", re.IGNORECASE),
]

def _extract_experience(text: str) -> float:
    """Return the maximum years of experience found via regex, or 0.0."""
    years = []
    for pattern in _EXP_PATTERNS:
        for match in pattern.finditer(text):
            try:
                years.append(float(match.group(1)))
            except ValueError:
                pass
    return max(years) if years else 0.0


# ─── Education extraction ──────────────────────────────────────────────────────
_DEGREE_KEYWORDS = [
    "phd", "ph.d", "doctorate",
    "master", "m.s.", "m.sc", "mba", "m.tech",
    "bachelor", "b.s.", "b.sc", "b.tech", "b.e.",
    "associate", "diploma", "high school",
]

def _extract_education(text: str) -> str:
    """Return the highest degree found in the text."""
    lower = text.lower()
    for degree in _DEGREE_KEYWORDS:
        if degree in lower:
            return degree.title()
    return "Not specified"


# ─── Main parsing function ─────────────────────────────────────────────────────
def parse_resume_text(raw_text: str) -> Dict[str, Any]:
    """
    Parse raw resume text and return a structured dict.
    Also anonymizes name, age, and gender information.
    """
    # If spaCy is available, use it for anonymization and GPE extraction;
    # otherwise do a best-effort lightweight parse.
    nlp = _get_nlp()

    # Anonymize gender and age tokens
    text = _GENDER_WORDS.sub("[REDACTED]", raw_text)
    text = _AGE_PATTERN.sub("[REDACTED]", text)

    anonymized = text
    city = ""
    state = ""

    if nlp is not None:
        doc = nlp(text)
        # Remove PERSON entities (names)
        for ent in reversed(doc.ents):
            if ent.label_ == "PERSON":
                anonymized = anonymized[:ent.start_char] + "[NAME]" + anonymized[ent.end_char:]
        # GPE entities for location
        gpe = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
        city = gpe[0] if gpe else ""
        state = gpe[1] if len(gpe) > 1 else city
    else:
        # Fallback: no name redaction beyond gender/age; location empty
        anonymized = text

    # Skill extraction (works in both modes): simple substring match
    lower_text = anonymized.lower()
    found_skills = [skill for skill in SKILL_LIST if skill in lower_text]

    years_exp = _extract_experience(anonymized)
    education = _extract_education(anonymized)

    return {
        "anonymized_text": anonymized,
        "skills": list(set(found_skills)),
        "years_experience": years_exp,
        "education": education,
        "location_city": city,
        "location_state": state,
    }
