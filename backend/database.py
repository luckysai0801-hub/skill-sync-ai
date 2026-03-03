"""
database.py - Database connection and session management using SQLAlchemy.
Uses PostgreSQL. Embeddings stored as JSON arrays (FLOAT[]).
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
load_dotenv()

# ─── Database URL ─────────────────────────────────────────────────────────────
# The application requires a DATABASE_URL environment variable pointing to
# a PostgreSQL database (e.g., Supabase). No fallback is provided.
# Example:
#   set DATABASE_URL=postgresql://user:password@host:5432/dbname
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL must be set to a valid PostgreSQL URL")

# ─── Engine & Session ─────────────────────────────────────────────────────────
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ─── Base Model ───────────────────────────────────────────────────────────────
Base = declarative_base()


def get_db():
    """Dependency: yields a database session and closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
