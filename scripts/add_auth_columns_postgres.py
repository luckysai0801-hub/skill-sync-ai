import os
from dotenv import load_dotenv
load_dotenv()
from sqlalchemy import create_engine, text

def ensure_columns(engine):
    with engine.connect() as conn:
        # check columns via information_schema
        for col, ddl in [
            ('authenticity_score', "ALTER TABLE resumes ADD COLUMN IF NOT EXISTS authenticity_score double precision"),
            ('authenticity_label', "ALTER TABLE resumes ADD COLUMN IF NOT EXISTS authenticity_label varchar DEFAULT 'unknown'"),
            ('authenticity_explanation', "ALTER TABLE resumes ADD COLUMN IF NOT EXISTS authenticity_explanation text")
        ]:
            res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='resumes' AND column_name=:col"), {'col': col})
            if res.first() is None:
                print('Adding', col)
                conn.execute(text(ddl))
            else:
                print(col, 'exists')

if __name__ == '__main__':
    url = os.getenv('DATABASE_URL')
    if not url:
        raise SystemExit('DATABASE_URL not set')
    engine = create_engine(url)
    try:
        ensure_columns(engine)
        print('Done')
    except Exception as e:
        print('Error:', e)
        raise
