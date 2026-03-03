import os
import sys

# Ensure 'backend' package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from database import engine
from sqlalchemy import text

with engine.begin() as conn:
    print("Forcing addition of updated_at to public.users...")
    try:
        conn.execute(text('ALTER TABLE public.users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();'))
        print("ALTER TABLE executed successfully.")
    except Exception as e:
        print(f"Error executing ALTER TABLE: {e}")

    print("\nVerifying columns in public.users:")
    result = conn.execute(text("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'public' AND table_name = 'users';
    """))
    found_updated_at = False
    for row in result:
        print(f" - {row[0]} ({row[1]})")
        if row[0] == 'updated_at':
            found_updated_at = True
    
    if found_updated_at:
        print("\n✅ Verified: updated_at exists in public.users!")
    else:
        print("\n❌ Failed: updated_at does NOT exist in public.users!")
