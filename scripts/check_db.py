import sqlite3, json, os

for p in ['skillsync.db', 'SkillSync/skillsync.db']:
	print('---', p, 'exists', os.path.exists(p))
	if not os.path.exists(p):
		continue
	conn = sqlite3.connect(p)
	cur = conn.cursor()
	try:
		cur.execute('PRAGMA table_info(resumes)')
		cols = cur.fetchall()
		print('cols:')
		print(json.dumps(cols, indent=2))
		# try to query authenticity columns if present
		try:
			cur.execute('SELECT id, resume_score, authenticity_score, authenticity_label, authenticity_explanation FROM resumes ORDER BY id DESC LIMIT 10')
			rows = cur.fetchall()
			print('rows:')
			print(json.dumps(rows, indent=2))
		except Exception as e:
			print('no authenticity columns or query failed:', e)
	finally:
		conn.close()
