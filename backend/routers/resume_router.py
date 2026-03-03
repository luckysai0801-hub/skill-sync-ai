"""
routers/resume_router.py - Protected endpoints for resume upload, parsing, and scoring.
"""

import io
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
import pdfplumber

from database import get_db
from models.user import User
from models.resume import Resume
from schemas.resume import ResumeOut, ResumeScoreOut
from services.resume_parser import parse_resume_text
from services.embedding_service import generate_embedding
from services.resume_scorer import score_resume
from services.authenticity_service import assess_authenticity
from utils.auth_deps import get_current_user, get_current_verified_user, require_candidate

router = APIRouter(prefix="/resume", tags=["Resume"])


@router.post("/upload-resume", response_model=ResumeOut)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """
    Upload a PDF resume for a candidate (PROTECTED).

    Requirements:
    - User must be authenticated
    - User must have verified email

    Parses text, anonymizes PII, extracts skills/experience/location,
    generates embedding, and scores resume quality.
    """
    # Check if user's role is candidate (or allow all authenticated users for now)

    # ── Extract text from PDF ──────────────────────────────────────────────────
    content = await file.read()
    raw_text = ""
    try:
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page in pdf.pages:
                raw_text += (page.extract_text() or "") + "\n"
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF parsing failed: {str(e)}")

    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")

    # ── Parse & anonymize ──────────────────────────────────────────────────────
    parsed = parse_resume_text(raw_text)

    # ── Generate embedding ─────────────────────────────────────────────────────
    embedding = generate_embedding(parsed["anonymized_text"])

    # ── Score resume quality ───────────────────────────────────────────────────
    score_result = score_resume(parsed["anonymized_text"], parsed["skills"])

    # ── Assess authenticity (fake vs real) ───────────────────────────────────
    auth = assess_authenticity(parsed["anonymized_text"], parsed.get("skills", []), score_result.get("resume_score"))

    # ── Store in database ──────────────────────────────────────────────────────
    # Use current_user.id instead of form parameter (security best practice)
    resume = Resume(
        user_id=current_user.id,
        raw_text=parsed["anonymized_text"],
        skills=parsed["skills"],
        years_experience=parsed["years_experience"],
        education=parsed["education"],
        location_city=parsed["location_city"],
        location_state=parsed["location_state"],
        expected_salary=0.0,   # extracted from form if needed
        embedding=embedding,
        resume_score=score_result["resume_score"],
        improvement_suggestions=score_result["improvement_suggestions"],
        authenticity_score=auth.get("authenticity_score"),
        authenticity_label=auth.get("authenticity_label"),
        authenticity_explanation=auth.get("authenticity_explanation"),
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


@router.get("/resume-score/{candidate_id}", response_model=ResumeScoreOut)
async def get_resume_score(
    candidate_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get resume quality score and improvement suggestions (PROTECTED).

    Requirements:
    - User must be authenticated
    """
    resume = db.query(Resume).filter(Resume.id == candidate_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    return ResumeScoreOut(
        resume_id=resume.id,
        resume_score=resume.resume_score,
        improvement_suggestions=resume.improvement_suggestions or [],
    )


@router.get("/{resume_id}", response_model=ResumeOut)
async def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Return full resume record including authenticity fields (PROTECTED).

    Requirements:
    - User must be authenticated
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    return resume
