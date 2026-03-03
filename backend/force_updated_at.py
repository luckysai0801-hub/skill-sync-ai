import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine
from sqlalchemy import text

print("Adding 'updated_at' to 'users' table if it doesn't exist...")
with engine.connect() as conn:
    try:
        conn.execute(text('ALTER TABLE users ADD COLUMN updated_at TIMESTAMP DEFAULT NOW();'))
        conn.commit()
        print("Successfully added updated_at!")
    except Exception as e:
        print(f"Error (might already exist): {e}")

print("Done!")
