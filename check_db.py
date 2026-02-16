import sqlite3

# Connect to database
conn = sqlite3.connect('health_reports.db')
cursor = conn.cursor()

# Get total count
cursor.execute('SELECT COUNT(*) FROM reports')
total = cursor.fetchone()[0]
print(f'Total reports in database: {total}')

# Get last 10 reports
cursor.execute('SELECT id, filename, created_at FROM reports ORDER BY id DESC LIMIT 10')
print('\nLast 10 reports:')
for row in cursor.fetchall():
    print(f'  ID: {row[0]}, File: {row[1]}, Created: {row[2]}')

conn.close()
