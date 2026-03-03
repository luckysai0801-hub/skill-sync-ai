import os
from dotenv import load_dotenv
load_dotenv()
from sqlalchemy import create_engine

url = os.getenv('DATABASE_URL')
print('DATABASE_URL:', url)
if not url:
    raise SystemExit('DATABASE_URL not set in environment or .env')

print('Creating engine...')
engine = create_engine(url, echo=False)
try:
    with engine.connect() as conn:
        r = conn.execute("SELECT version()")
        print('Connected to:', r.fetchone())
except Exception as e:
    print('Connection failed:', e)
    raise
