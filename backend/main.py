"""
main.py - SkillSync AI FastAPI application entry point.

Run with:
  cd backend
  uvicorn main:app --reload --host 0.0.0.0 --port 8000

API Docs: http://localhost:8000/docs
"""

import os
import sys
import traceback

# Load .env file first thing (before any imports that use os.getenv)
from dotenv import load_dotenv
load_dotenv()

# Ensure 'backend' package is importable when running from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from database import engine, Base
from routers.resume_router import router as resume_router
from routers.job_router import router as job_router
from routers.match_router import router as match_router
from routers.auth_router import router as auth_router
from middleware.security_headers import add_security_headers
from utils.rate_limiter import limiter
from database import get_db
from sqlalchemy.orm import Session
from models.resume import Resume
from schemas.resume import ResumeOut


# ─── Create all database tables ───────────────────────────────────────────────
# Import models so SQLAlchemy knows about them before create_all()
import models.user    # noqa
import models.resume  # noqa
import models.job     # noqa
import models.match   # noqa
try:
    # make sure we can connect; this will raise if DB is unreachable
    with engine.connect() as conn:
        pass
    Base.metadata.create_all(bind=engine)
except Exception as e:
    # print informative message and re-raise so uvicorn logs it
    print(f"Fatal: unable to connect to database at {engine.url}: {e}")
    raise

# ─── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="SkillSync AI",
    description="Explainable Smart Job Matching & Career Intelligence Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── Rate Limiter Setup ─────────────────────────────────────────────────────
app.state.limiter = limiter

# ─── CORS (Restrict to development localhost) ──────────────────────────────
allowed_origins = [
    "http://localhost:5173",   # React dev server (Vite)
    "http://localhost:5174",   # Alternate Vite port
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5173",
    "http://localhost:3000",   # Alternate dev port
    # Add production URLs here when deploying:
    # "https://skillsync.com",
    # "https://www.skillsync.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,       # Enable cookies
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Explicit methods
    allow_headers=["Content-Type", "Authorization"],  # Only necessary headers
    max_age=600,  # Cache preflight requests for 10 minutes
)

# ─── Security Headers Middleware ───────────────────────────────────────────
from middleware.security_headers import add_security_headers as security_headers_middleware

@app.middleware("http")
async def add_security_headers_middleware(request, call_next):
    return await security_headers_middleware(request, call_next)


# ─── Global Exception Handler ───────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_msg = traceback.format_exc()
    with open("error_log.txt", "w") as f:
        f.write(f"\\n\\n--- ERROR AT {request.url} ---\\n{error_msg}")
    print(f"500 Error: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


# ─── Middleware Configuration ──────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(resume_router)
app.include_router(job_router)
app.include_router(match_router)


# ─── Startup: seed demo data ───────────────────────────────────────────────────
@app.on_event("startup")
def on_startup():
    """Seed demo data if database is empty.

    Skip seeding if SKIP_SEED=1 is set (e.g. database already populated,
    or production environment).
    """
    if os.getenv("SKIP_SEED") == "1":
        print("ℹ️  SKIP_SEED=1 – skipping demo data seeding.")
        return
    try:
        from utils.seed_data import seed_demo_data
        seed_demo_data()
    except Exception as e:
        print(f"Warning: Could not seed demo data: {e}")


# ─── Root endpoint ─────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "app": "SkillSync AI",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running",
    }


# ─── Health check ─────────────────────────────────────────────────────────────
@app.get("/health")
def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/add-updated-at")
def add_updated_at():
    from sqlalchemy import text
    with engine.connect() as conn:
        try:
            conn.execute(text('ALTER TABLE users ADD COLUMN updated_at TIMESTAMP DEFAULT NOW();'))
            conn.commit()
            return {"status": "success", "message": "Added updated_at to users table"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

@app.get("/verify-schema")
def verify_schema():
    from sqlalchemy import text
    with engine.connect() as conn:
        result = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'users';"))
        columns = [{"name": row[0], "type": row[1]} for row in result]
        return {"columns": columns}

@app.get("/resume-detail/{resume_id}", response_model=ResumeOut)
def resume_detail(resume_id: int, db: Session = Depends(get_db)):
    """Temporary resume detail endpoint to return full resume with authenticity."""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume
