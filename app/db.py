import sqlite3
import threading
from datetime import datetime, timezone

_lock = threading.Lock()

SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room TEXT NOT NULL,
    username TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_messages_room ON messages(room, id);
"""


def _connect(path):
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_app(app):
    conn = _connect(app.config["DATABASE_PATH"])
    conn.executescript(SCHEMA)
    conn.commit()
    app.extensions["chat_db"] = conn


def _conn():
    from flask import current_app
    return current_app.extensions["chat_db"]


def save_message(room, username, body):
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with _lock:
        conn = _conn()
        cur = conn.execute(
            "INSERT INTO messages (room, username, body, created_at) VALUES (?, ?, ?, ?)",
            (room, username, body, created_at),
        )
        conn.commit()
    return {"id": cur.lastrowid, "room": room, "username": username,
            "body": body, "created_at": created_at}


def recent_messages(room, limit):
    with _lock:
        rows = _conn().execute(
            "SELECT * FROM messages WHERE room = ? ORDER BY id DESC LIMIT ?",
            (room, limit),
        ).fetchall()
    return [dict(r) for r in reversed(rows)]


def ping():
    with _lock:
        _conn().execute("SELECT 1").fetchone()
