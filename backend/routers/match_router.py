"""
routers/match_router.py - Core matching, ranking, skill-gap, and analytics endpoints (PROTECTED).

Endpoints:
  GET /match-jobs/{candidate_id}          → Top 5 jobs for a candidate
  GET /match-candidates/{job_id}          → Top 5 candidates for a job
  GET /skill-gap/{candidate_id}/{job_id}  → Skill gap analysis
  GET /interview-probability/{candidate_id}/{job_id}  → Interview probability
  GET /recruiter-dashboard/{job_id}       → Full analytics dashboard
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from collections import Counter

from database import get_db
from models.user import User
from models.resume import Resume
from models.job import Job
from models.match import Match
from schemas.match import MatchOut, ScoreBreakdown, SkillGapOut, DashboardOut
from services.matching_engine import compute_match_scores
from services.skill_gap import analyze_skill_gap
from services.probability_estimator import estimate_interview_probability
from utils.auth_deps import get_current_user, require_employer

router = APIRouter(tags=["Matching"])


# ─── Helper: compute or retrieve a match ──────────────────────────────────────

def _get_or_compute_match(resume: Resume, job: Job, db: Session) -> Match:
    """
    Look up cached match in DB; if missing, compute and store it.
    """
    existing = (
        db.query(Match)
        .filter(Match.resume_id == resume.id, Match.job_id == job.id)
        .first()
    )
    if existing:
        return existing

    if not resume.embedding or not job.embedding:
        raise HTTPException(status_code=400, detail="Embeddings not generated yet")

    scores = compute_match_scores(
        resume_embedding=resume.embedding,
        job_embedding=job.embedding,
        candidate_skills=resume.skills or [],
        required_skills=job.required_skills or [],
        candidate_exp=resume.years_experience,
        required_exp=job.required_experience,
        candidate_city=resume.location_city or "",
        candidate_state=resume.location_state or "",
        candidate_salary=resume.expected_salary or 0.0,
        job_city=job.location_city or "",
        job_state=job.location_state or "",
        is_remote=job.is_remote,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
    )

    gap = analyze_skill_gap(
        candidate_skills=resume.skills or [],
        required_skills=job.required_skills or [],
        current_final_score=scores["final_score"],
    )

    prob = estimate_interview_probability(scores["final_score"], job.required_skills or [])

    match = Match(
        resume_id=resume.id,
        job_id=job.id,
        **scores,
        interview_probability=prob,
        missing_skills=gap["missing_skills"],
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    return match


def _match_to_out(match: Match, job_title: str = "") -> MatchOut:
    return MatchOut(
        match_id=match.id,
        resume_id=match.resume_id,
        job_id=match.job_id,
        job_title=job_title,
        scores=ScoreBreakdown(
            final_score=match.final_score,
            semantic_score=match.semantic_score,
            skill_overlap=match.skill_overlap,
            experience_score=match.experience_score,
            location_score=match.location_score,
            salary_score=match.salary_score,
        ),
        interview_probability=match.interview_probability,
        missing_skills=match.missing_skills or [],
    )


# ─── GET /match-jobs/{candidate_id} ───────────────────────────────────────────

@router.get("/match-jobs/{candidate_id}", response_model=List[MatchOut])
async def match_jobs_for_candidate(
    candidate_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Return top-5 ranked jobs for a given candidate (resume ID) (PROTECTED).

    Requirements:
    - User must be authenticated

    Computes matches against all jobs and returns best 5 by final_score.
    """
    resume = db.query(Resume).filter(Resume.id == candidate_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    jobs = db.query(Job).all()
    if not jobs:
        raise HTTPException(status_code=404, detail="No jobs available")

    matches = []
    for job in jobs:
        try:
            m = _get_or_compute_match(resume, job, db)
            matches.append((m, job.title))
        except Exception:
            continue

    matches.sort(key=lambda x: x[0].final_score, reverse=True)
    return [_match_to_out(m, title) for m, title in matches[:5]]


# ─── GET /match-candidates/{job_id} ───────────────────────────────────────────

@router.get("/match-candidates/{job_id}", response_model=List[MatchOut])
async def match_candidates_for_job(
    job_id: int,
    current_user: User = Depends(require_employer),
    db: Session = Depends(get_db)
):
    """
    Return top-5 ranked candidates for a given job (PROTECTED).

    Requirements:
    - User must be authenticated as EMPLOYER

    Computes matches against all resumes and returns best 5 by final_score.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    resumes = db.query(Resume).all()
    if not resumes:
        raise HTTPException(status_code=404, detail="No candidates available")

    matches = []
    for resume in resumes:
        try:
            m = _get_or_compute_match(resume, job, db)
            matches.append((m, job.title))
        except Exception:
            continue

    matches.sort(key=lambda x: x[0].final_score, reverse=True)
    return [_match_to_out(m, title) for m, title in matches[:5]]


# ─── GET /skill-gap/{candidate_id}/{job_id} ───────────────────────────────────

@router.get("/skill-gap/{candidate_id}/{job_id}", response_model=SkillGapOut)
async def skill_gap(
    candidate_id: int,
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Return skill gap analysis and simulated improved score (PROTECTED).

    Requirements:
    - User must be authenticated
    """
    resume = db.query(Resume).filter(Resume.id == candidate_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    match = _get_or_compute_match(resume, job, db)

    from services.skill_gap import analyze_skill_gap, get_skill_demand_weight
    gap = analyze_skill_gap(
        candidate_skills=resume.skills or [],
        required_skills=job.required_skills or [],
        current_final_score=match.final_score,
    )
    return SkillGapOut(
        candidate_id=candidate_id,
        job_id=job_id,
        missing_skills=gap["missing_skills"],
        current_score=gap["current_score"],
        simulated_score=gap["simulated_score"],
        skill_demand_weight=gap["skill_demand_weight"],
    )


# ─── GET /interview-probability/{candidate_id}/{job_id} ───────────────────────

@router.get("/interview-probability/{candidate_id}/{job_id}")
async def interview_probability(
    candidate_id: int,
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Return interview call probability percentage (PROTECTED).

    Requirements:
    - User must be authenticated
    """
    resume = db.query(Resume).filter(Resume.id == candidate_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    match = _get_or_compute_match(resume, job, db)
    return {
        "candidate_id":           candidate_id,
        "job_id":                 job_id,
        "interview_probability":  match.interview_probability,
        "final_score":            match.final_score,
    }


# ─── GET /recruiter-dashboard/{job_id} ────────────────────────────────────────

@router.get("/recruiter-dashboard/{job_id}", response_model=DashboardOut)
async def recruiter_dashboard(
    job_id: int,
    current_user: User = Depends(require_employer),
    db: Session = Depends(get_db)
):
    """
    Full recruiter analytics dashboard (PROTECTED).

    Requirements:
    - User must be authenticated as EMPLOYER

    Returns:
      • Average candidate score
      • Top 5 candidates
      • Skill distribution across all candidates
      • Experience distribution
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    resumes = db.query(Resume).all()
    if not resumes:
        raise HTTPException(status_code=404, detail="No candidates available")

    all_matches = []
    for resume in resumes:
        try:
            m = _get_or_compute_match(resume, job, db)
            all_matches.append((m, resume))
        except Exception:
            continue

    if not all_matches:
        raise HTTPException(status_code=404, detail="Could not compute matches")

    # Sort by final_score
    all_matches.sort(key=lambda x: x[0].final_score, reverse=True)

    # Average score
    avg_score = round(sum(m.final_score for m, _ in all_matches) / len(all_matches), 2)

    # Top 5
    top5 = [_match_to_out(m, job.title) for m, _ in all_matches[:5]]

    # Skill distribution (all candidate skills across all resumes)
    all_skills = []
    for _, r in all_matches:
        all_skills.extend(r.skills or [])
    skill_dist = dict(Counter(all_skills).most_common(15))

    # Experience distribution buckets
    exp_buckets = {"0-1": 0, "1-3": 0, "3-5": 0, "5-10": 0, "10+": 0}
    for _, r in all_matches:
        e = r.years_experience or 0
        if e <= 1:
            exp_buckets["0-1"] += 1
        elif e <= 3:
            exp_buckets["1-3"] += 1
        elif e <= 5:
            exp_buckets["3-5"] += 1
        elif e <= 10:
            exp_buckets["5-10"] += 1
        else:
            exp_buckets["10+"] += 1

    return DashboardOut(
        job_id=job_id,
        job_title=job.title,
        total_candidates=len(all_matches),
        average_score=avg_score,
        top_candidates=top5,
        skill_distribution=skill_dist,
        experience_distribution=exp_buckets,
    )
