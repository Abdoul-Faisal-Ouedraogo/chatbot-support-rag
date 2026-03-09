# utils/tickets.py
import sqlite3
from datetime import datetime
import os

DB_PATH = "database/tickets.db"

# Création automatique de la base et de la table
def init_db():
    os.makedirs("database", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            summary TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

def create_ticket(session_id, summary):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO tickets (session_id, summary, status, created_at)
        VALUES (?, ?, ?, ?)
    """, (session_id, summary, "open", datetime.now().isoformat()))
    ticket_id = c.lastrowid
    conn.commit()
    conn.close()
    return ticket_id

def get_ticket(ticket_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    ticket = c.fetchone()
    conn.close()
    return ticket
