import sqlite3
import json

DB_NAME = "health_app.db"


def init_db():

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        report_data TEXT
    )
    """)

    conn.commit()
    conn.close()


def create_user(username, password):

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    try:
        c.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

    return True


def login_user(username, password):

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )

    user = c.fetchone()
    conn.close()

    return user


def save_report(username, report):

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute(
        "INSERT INTO reports (username, report_data) VALUES (?, ?)",
        (username, json.dumps(report))
    )

    conn.commit()
    conn.close()


def get_reports(username):

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute(
        "SELECT report_data FROM reports WHERE username=?",
        (username,)
    )

    rows = c.fetchall()
    conn.close()

    return [json.loads(r[0]) for r in rows]
