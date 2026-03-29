# database.py
# SQLite database — no install, no cloud, no server needed
# Creates transcriptions.db file automatically in the backend folder

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "transcriptions.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create table if it does not exist."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transcriptions (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id    TEXT NOT NULL,
            english_text  TEXT NOT NULL,
            hindi_text    TEXT NOT NULL,
            status        TEXT NOT NULL DEFAULT 'final',
            timestamp     TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print(f"[DB] SQLite ready → {DB_PATH}")


def save_transcription(session_id: str, english_text: str, hindi_text: str, status: str = "final") -> int:
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO transcriptions (session_id, english_text, hindi_text, status, timestamp)
           VALUES (?, ?, ?, ?, ?)""",
        (session_id, english_text, hindi_text, status, datetime.utcnow().isoformat())
    )
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    print(f"[DB] Saved record #{row_id}")
    return row_id


def get_all_transcriptions(limit: int = 50) -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM transcriptions ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_all() -> int:
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM transcriptions").fetchone()[0]
    conn.execute("DELETE FROM transcriptions")
    conn.commit()
    conn.close()
    return count
