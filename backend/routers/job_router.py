"""
routers/job_router.py - Protected endpoints for job creation and retrieval.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from models.job import Job
from schemas.job import JobCreate, JobOut
from services.embedding_service import generate_embedding
from utils.auth_deps import get_current_user, get_current_verified_user, require_employer

router = APIRouter(prefix="/job", tags=["Job"])


@router.post("/create-job", response_model=JobOut)
async def create_job(
    payload: JobCreate,
    current_user: User = Depends(require_employer),
    db: Session = Depends(get_db)
):
    """
    Employer posts a new job (PROTECTED).

    Requirements:
    - User must be authenticated as EMPLOYER
    - User must have verified email
    - employer_id will be overridden with current_user.id for security

    Generates a semantic embedding for the job description.
    Stores everything in the jobs table.
    """
    # Generate embedding from title + description + skills
    combined_text = f"{payload.title}. {payload.description}. Skills: {', '.join(payload.required_skills)}"
    embedding = generate_embedding(combined_text)

    # Use current_user.id instead of payload.employer_id for security
    job = Job(
        employer_id=current_user.id,
        title=payload.title,
        description=payload.description,
        required_skills=payload.required_skills,
        required_experience=payload.required_experience,
        salary_min=payload.salary_min,
        salary_max=payload.salary_max,
        location_city=payload.location_city,
        location_state=payload.location_state,
        is_remote=payload.is_remote,
        embedding=embedding,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("/jobs", response_model=list[JobOut])
async def list_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all available jobs (PROTECTED).

    Requirements:
    - User must be authenticated
    """
    return db.query(Job).order_by(Job.created_at.desc()).all()


@router.get("/jobs/{job_id}", response_model=JobOut)
async def get_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a single job by ID (PROTECTED).

    Requirements:
    - User must be authenticated
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

