import sqlite3
import os

db_path = "health_reports.db"

def migrate():
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(reports)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "full_results" not in columns:
            print("Adding full_results column to reports table...")
            cursor.execute("ALTER TABLE reports ADD COLUMN full_results TEXT")
            conn.commit()
            print("Migration successful.")
        else:
            print("Column full_results already exists.")
            
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
