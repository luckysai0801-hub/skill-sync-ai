import os
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace') if hasattr(sys.stdout, 'reconfigure') else None

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set in .env")
    sys.exit(1)

# Use psycopg2 directly for raw DDL
# DATABASE_URL is postgresql+psycopg2://... strip the driver prefix
conn_str = DATABASE_URL.replace("postgresql+psycopg2://", "postgresql://")

try:
    import psycopg2
except ImportError:
    print("psycopg2 not found, trying psycopg2-binary...")
    os.system("pip install psycopg2-binary")
    import psycopg2

print(f"Connecting to database...")
conn = psycopg2.connect(conn_str)
conn.autocommit = True
cur = conn.cursor()

# List of (column_name, column_definition) pairs to add if missing
COLUMNS_TO_ADD = [
    ("password_hash",               "VARCHAR"),
    ("email_verified",              "BOOLEAN DEFAULT FALSE"),
    ("email_verification_token",    "VARCHAR UNIQUE"),
    ("verification_token_expires",  "TIMESTAMP"),
    ("last_login",                  "TIMESTAMP"),
    ("failed_login_attempts",       "INTEGER DEFAULT 0"),
    ("last_failed_login",           "TIMESTAMP"),
    ("reset_token",                 "VARCHAR UNIQUE"),
    ("reset_token_expires",         "TIMESTAMP"),
    ("is_active",                   "BOOLEAN DEFAULT TRUE"),
    ("updated_at",                  "TIMESTAMP DEFAULT NOW()"),
]

print("\nChecking and adding missing columns to 'users' table...")
added = []
skipped = []

for col_name, col_def in COLUMNS_TO_ADD:
    # Check if column already exists
    cur.execute("""
        SELECT COUNT(*) FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = %s
    """, (col_name,))
    exists = cur.fetchone()[0] > 0

    if exists:
        skipped.append(col_name)
        print(f"  ✓ {col_name} already exists – skipped")
    else:
        try:
            cur.execute(f'ALTER TABLE users ADD COLUMN "{col_name}" {col_def};')
            added.append(col_name)
            print(f"  ✅ Added {col_name} ({col_def})")
        except Exception as e:
            print(f"  ❌ Failed to add {col_name}: {e}")

# Add indexes for token columns (for fast lookups)
INDEX_CMDS = [
    ("idx_email_verification_token", "users", "email_verification_token"),
    ("idx_reset_token",              "users", "reset_token"),
    ("idx_last_login",               "users", "last_login"),
]

print("\nAdding indexes...")
for idx_name, table, column in INDEX_CMDS:
    try:
        cur.execute(f"""
            CREATE INDEX IF NOT EXISTS {idx_name} ON {table} ("{column}");
        """)
        print(f"  ✅ Index {idx_name} ensured")
    except Exception as e:
        print(f"  ❌ Index {idx_name} failed: {e}")

cur.close()
conn.close()

print(f"\n{'='*50}")
print(f"Migration complete!")
print(f"  Added  : {len(added)} columns  → {added}")
print(f"  Skipped: {len(skipped)} columns (already existed)")
print(f"{'='*50}")
print("\nYou can now restart the backend server and try registering again.")
