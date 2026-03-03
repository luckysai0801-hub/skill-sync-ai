"""
Export SQLite tables to CSV without requiring the sqlite3 CLI.
Run from the project root with the venv active:

    .venv/Scripts/activate
    python backend/utils/export_sqlite_to_csv.py

This writes: users.csv, resumes.csv, jobs.csv, matches.csv into the project root.
"""

import sqlite3
import csv
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'skillsync.db')
OUT_DIR = os.path.dirname(DB_PATH)

TABLES = {
    'users': ['id', 'email', 'name', 'role', 'created_at'],
    'resumes': ['id', 'user_id', 'raw_text', 'skills', 'years_experience', 'education', 'location_city', 'location_state', 'expected_salary', 'embedding', 'resume_score', 'improvement_suggestions', 'created_at'],
    'jobs': ['id', 'employer_id', 'title', 'description', 'required_skills', 'required_experience', 'salary_min', 'salary_max', 'location_city', 'location_state', 'is_remote', 'embedding', 'created_at'],
    'matches': ['id', 'resume_id', 'job_id', 'final_score', 'semantic_score', 'skill_overlap', 'experience_score', 'location_score', 'salary_score', 'interview_probability', 'missing_skills', 'computed_at'],
}

if not os.path.exists(DB_PATH):
    raise SystemExit(f"Could not find SQLite DB at {DB_PATH}. Run from project root.")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

for table, cols in TABLES.items():
    out_path = os.path.join(OUT_DIR, f"{table}.csv")
    print(f"Exporting {table} -> {out_path}")
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(cols)
        try:
            cur.execute(f"SELECT {', '.join(cols)} FROM {table};")
        except Exception as e:
            print(f"Error querying {table}: {e}")
            continue
        rows = cur.fetchall()
        for r in rows:
            row = []
            for c in cols:
                v = r[c]
                # Ensure bytes -> str, None -> empty
                if isinstance(v, bytes):
                    try:
                        v = v.decode('utf-8')
                    except Exception:
                        v = repr(v)
                if v is None:
                    v = ''
                row.append(v)
            writer.writerow(row)

conn.close()
print("Export complete. CSVs are in:", OUT_DIR)
