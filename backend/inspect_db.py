import sqlite3
import os
path = os.path.join(os.getcwd(), 'db.sqlite3')
print('DB exists:', os.path.exists(path))
if not os.path.exists(path):
    raise SystemExit('db.sqlite3 not found')
with sqlite3.connect(path) as conn:
    cur = conn.cursor()
    cur.execute('PRAGMA table_info(api_test)')
    rows = cur.fetchall()
    print('api_test columns:')
    for row in rows:
        print(row)
