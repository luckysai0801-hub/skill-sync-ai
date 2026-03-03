import sqlite3
import os
DBS = ['skillsync.db', 'SkillSync/skillsync.db']
for p in DBS:
    if not os.path.exists(p):
        print('skip missing', p)
        continue
    conn = sqlite3.connect(p)
    cur = conn.cursor()
    # check columns
    cur.execute("PRAGMA table_info(resumes)")
    cols = [c[1] for c in cur.fetchall()]
    print(p, 'cols before:', cols)
    if 'authenticity_score' not in cols:
        try:
            cur.execute("ALTER TABLE resumes ADD COLUMN authenticity_score FLOAT")
            print('added authenticity_score to', p)
        except Exception as e:
            print('could not add authenticity_score', e)
    if 'authenticity_label' not in cols:
        try:
            cur.execute("ALTER TABLE resumes ADD COLUMN authenticity_label VARCHAR DEFAULT 'unknown'")
            print('added authenticity_label to', p)
        except Exception as e:
            print('could not add authenticity_label', e)
    if 'authenticity_explanation' not in cols:
        try:
            cur.execute("ALTER TABLE resumes ADD COLUMN authenticity_explanation TEXT")
            print('added authenticity_explanation to', p)
        except Exception as e:
            print('could not add authenticity_explanation', e)
    conn.commit()
    cur.execute("PRAGMA table_info(resumes)")
    print(p, 'cols after:', [c[1] for c in cur.fetchall()])
    conn.close()
