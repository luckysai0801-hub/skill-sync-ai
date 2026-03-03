import os
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL").replace("postgresql+psycopg2://", "postgresql://")

import psycopg

print("Connecting to database...")
with psycopg.connect(db_url) as conn:
    conn.autocommit = True
    with conn.cursor() as cur:
        print("Executing ALTER TABLE...")
        try:
            cur.execute("ALTER TABLE users ADD COLUMN updated_at TIMESTAMP DEFAULT NOW();")
            print("Successfully executed ALTER TABLE")
        except Exception as e:
            print(f"Exception during ALTER TABLE: {e}")

        print("\nListing columns in users table:")
        cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'users';")
        for row in cur.fetchall():
            print(f" - {row[0]} ({row[1]})")

print("\nDone!")
