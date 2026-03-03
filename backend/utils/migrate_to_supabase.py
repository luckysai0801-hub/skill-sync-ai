"""
One-time helper: copy sqlite -> postgres.  Run with the same env variables
you use for the app (DATABASE_URL points at the Supabase connection string).
"""

import os, sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# make sure project root (parent of `backend`) is on sys.path so `backend` can be imported
# file is: <project>/backend/utils/migrate_to_supabase.py
# so go three levels up to reach the project root
root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, root)
# Ensure `DATABASE_URL` is rewritten to use the psycopg (psycopg3) driver
# so that SQLAlchemy does not attempt to import the legacy psycopg2 package.
# Read the environment variable (if any), rewrite it, and set it back into
# os.environ before importing `backend.database` which creates an engine at
# import time.
TGT_URL_ENV = os.getenv("DATABASE_URL")
if TGT_URL_ENV and TGT_URL_ENV.startswith("postgresql://"):
    # rewrite to use psycopg v3 dialect/driver that is installed via
    # `psycopg[binary]` in requirements
    rewritten = TGT_URL_ENV.replace("postgresql://", "postgresql+psycopg://", 1)
    os.environ["DATABASE_URL"] = rewritten

from backend.database import Base
from backend.models.user import User
from backend.models.resume import Resume
from backend.models.job import Job
from backend.models.match import Match

# source = sqlite
SRC_URL = "sqlite:///./skillsync.db"
src_engine = create_engine(SRC_URL, echo=False)
SrcSession = sessionmaker(bind=src_engine)

# target = postgres (supabase).  we only need DATABASE_URL if the
# SQLAlchemy/DBAPI route is going to be attempted; when running in a
# driverless environment we'll fall back to the REST importer and the
# URL is not required.
TGT_URL = os.getenv("DATABASE_URL")
if TGT_URL:
    tgt_url_fixed = TGT_URL
    # rewrite to psycopg3 dialect if necessary
    if TGT_URL.startswith("postgresql://"):
        tgt_url_fixed = TGT_URL.replace("postgresql://", "postgresql+psycopg://", 1)
    tgt_engine = create_engine(tgt_url_fixed, echo=True)
    TgtSession = sessionmaker(bind=tgt_engine)
else:
    # no URL provided; SQLAlchemy path will be skipped later
    tgt_engine = None
    TgtSession = None


def rest_migrate():
    """Fallback migration using Supabase REST API. This avoids installing
    a Postgres DBAPI driver locally. Requires these env vars:
      - SUPABASE_URL (e.g. https://xyz.supabase.co)
      - SUPABASE_KEY (service_role key for full inserts)

    The script will read rows from the local SQLite DB and POST them
    into the Supabase REST endpoints in the correct order.
    """
    import sqlite3
    import json
    try:
        import requests
    except Exception:
        raise RuntimeError("requests is required for REST fallback. Install with: pip install requests")

    supabase_url = os.getenv("SUPABASE_URL")
    if supabase_url:
        supabase_url = supabase_url.strip()
    supabase_key = os.getenv("SUPABASE_KEY")
    if not supabase_url or not supabase_key:
        raise RuntimeError("Set SUPABASE_URL and SUPABASE_KEY environment variables for REST fallback")

    hdrs = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }

    conn = sqlite3.connect(os.path.join(root, 'skillsync.db'))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    def fetch_rows(table, cols):
        cur.execute(f"SELECT {', '.join(cols)} FROM {table};")
        return [dict(row) for row in cur.fetchall()]

    def normalize_value(v):
        # sqlite JSON stored as text — try to parse JSON-like strings
        if v is None or v == '':
            return None
        if isinstance(v, (list, dict)):
            return v
        if isinstance(v, (int, float, bool)):
            return v
        s = str(v)
        s_stripped = s.strip()
        if (s_stripped.startswith('[') or s_stripped.startswith('{')):
            try:
                return json.loads(s)
            except Exception:
                return s
        return s

    TABLES = [
        ('users', ['id', 'email', 'name', 'role', 'created_at']),
        ('resumes', ['id', 'user_id', 'raw_text', 'skills', 'years_experience', 'education', 'location_city', 'location_state', 'expected_salary', 'embedding', 'resume_score', 'improvement_suggestions', 'created_at']),
        ('jobs', ['id', 'employer_id', 'title', 'description', 'required_skills', 'required_experience', 'salary_min', 'salary_max', 'location_city', 'location_state', 'is_remote', 'embedding', 'created_at']),
        ('matches', ['id', 'resume_id', 'job_id', 'final_score', 'semantic_score', 'skill_overlap', 'experience_score', 'location_score', 'salary_score', 'interview_probability', 'missing_skills', 'computed_at']),
    ]

    for table, cols in TABLES:
        rows = fetch_rows(table, cols)
        if not rows:
            print(f"no rows to import for {table}")
            continue
        payload = []
        for r in rows:
            obj = {}
            for c in cols:
                obj[c] = normalize_value(r[c])
            payload.append(obj)

        url = supabase_url.rstrip('/') + f"/rest/v1/{table}"
        print(f"POSTing {len(payload)} rows to {url}")
        # insert in batches to avoid huge payloads
        BATCH = 200
        for i in range(0, len(payload), BATCH):
            batch = payload[i:i+BATCH]
            hdrs_with_pref = hdrs.copy()
            hdrs_with_pref['Prefer'] = 'return=representation'

            params = {'return': 'representation', 'on_conflict': 'id'}
            # attempt each batch a few times in case of flaky network
            for attempt in range(1, 4):
                try:
                    resp = requests.post(url, headers=hdrs_with_pref, json=batch, params=params, timeout=15)
                except requests.exceptions.RequestException as exc:
                    print(f"batch POST failed (attempt {attempt}): {exc}")
                    if attempt == 3:
                        raise
                    continue
                if 200 <= resp.status_code < 300:
                    break
                # handle missing-table error specially
                if resp.status_code == 404 and 'Could not find the table' in resp.text:
                    raise RuntimeError(
                        "Supabase tables appear to be missing. "
                        "Create the database schema before running this script. "
                        "You can run backend/utils/print_ddl.py to see the required CREATE TABLE statements."
                    )
                # if conflict or other error, raise (on_conflict should suppress dupes)
                raise RuntimeError(f"Supabase REST insert failed for {table}: {resp.status_code} {resp.text}")
        print(f"imported {table}")

    conn.close()
    print('REST migration complete')

def migrate():
    # try SQLAlchemy path first (requires DBAPI). On failure use REST fallback.
    if tgt_engine is not None:
        try:
            Base.metadata.create_all(bind=tgt_engine)

            with SrcSession() as src, TgtSession() as tgt:
                # users
                for u in src.query(User).all():
                    tgt.merge(User(
                        id=u.id,
                        email=u.email,
                        name=u.name,
                        role=u.role,
                        created_at=u.created_at,
                    ))
                tgt.commit()

                # resumes
                for r in src.query(Resume).all():
                    tgt.merge(Resume(
                        id=r.id,
                        user_id=r.user_id,
                        raw_text=r.raw_text,
                        skills=r.skills,
                        years_experience=r.years_experience,
                        education=r.education,
                        location_city=r.location_city,
                        location_state=r.location_state,
                        expected_salary=r.expected_salary,
                        embedding=r.embedding,
                        resume_score=r.resume_score,
                        improvement_suggestions=r.improvement_suggestions,
                        created_at=r.created_at,
                    ))
                tgt.commit()

                # jobs
                for j in src.query(Job).all():
                    tgt.merge(Job(
                        id=j.id,
                        employer_id=j.employer_id,
                        title=j.title,
                        description=j.description,
                        required_skills=j.required_skills,
                        required_experience=j.required_experience,
                        salary_min=j.salary_min,
                        salary_max=j.salary_max,
                        location_city=j.location_city,
                        location_state=j.location_state,
                        is_remote=j.is_remote,
                        embedding=j.embedding,
                        created_at=j.created_at,
                    ))
                tgt.commit()

                # matches
                for m in src.query(Match).all():
                    tgt.merge(Match(
                        id=m.id,
                        resume_id=m.resume_id,
                        job_id=m.job_id,
                        final_score=m.final_score,
                        semantic_score=m.semantic_score,
                        skill_overlap=m.skill_overlap,
                        experience_score=m.experience_score,
                        location_score=m.location_score,
                        salary_score=m.salary_score,
                        interview_probability=m.interview_probability,
                        missing_skills=m.missing_skills,
                        computed_at=m.computed_at,
                    ))
                tgt.commit()

            print("migration complete")
            return
        except Exception as e:
            print('SQLAlchemy/Postgres path failed, falling back to REST method:', e)
    else:
        print("DATABASE_URL not provided; skipping direct SQLAlchemy path")

    rest_migrate()

if __name__ == "__main__":
    migrate()
