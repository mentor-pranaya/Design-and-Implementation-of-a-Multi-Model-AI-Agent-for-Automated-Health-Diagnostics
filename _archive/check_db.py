import sqlite3
import os

# Check blood_reports.db
if os.path.exists('blood_reports.db'):
    conn = sqlite3.connect('blood_reports.db')
    cursor = conn.cursor()

    # Get table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in blood_reports.db:", tables)

    # Check reports table
    if ('reports',) in tables:
        cursor.execute("SELECT COUNT(*) FROM reports")
        count = cursor.fetchone()[0]
        print(f"Number of reports in blood_reports.db: {count}")

        # Show recent reports
        cursor.execute("SELECT id, filename, created_at FROM reports ORDER BY created_at DESC LIMIT 5")
        recent = cursor.fetchall()
        print("Recent reports:")
        for row in recent:
            print(f"  ID: {row[0]}, File: {row[1]}, Date: {row[2]}")

    conn.close()
else:
    print("blood_reports.db not found")

# Check health_reports.db
if os.path.exists('health_reports.db'):
    conn = sqlite3.connect('health_reports.db')
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in health_reports.db:", tables)

    if ('reports',) in tables:
        cursor.execute("SELECT COUNT(*) FROM reports")
        count = cursor.fetchone()[0]
        print(f"Number of reports in health_reports.db: {count}")

    conn.close()
else:
    print("health_reports.db not found")
