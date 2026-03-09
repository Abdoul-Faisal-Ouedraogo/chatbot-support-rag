# utils/memory.py
import sqlite3
from datetime import datetime
import os

DB_PATH = "database/sessions.db"

# Création automatique de la base et de la table
def init_db():
    os.makedirs("database", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

def save_message(session_id, role, content):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO messages (session_id, role, content, timestamp)
        VALUES (?, ?, ?, ?)
    """, (session_id, role, content, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_recent_messages(session_id, limit=5):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT role, content FROM messages
        WHERE session_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (session_id, limit))
    rows = c.fetchall()
    conn.close()
    return rows[::-1]  # On remet dans l'ordre chronologique
