#backend/app/storage/init_db.py
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

SCHEMA_PATH = Path(__file__).parent / "schema.sql"

def _ensure_column(conn: sqlite3.Connection, table: str, column: str, ddl: str) -> None:
    existing = [row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    if column not in existing:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {ddl}")

def init_db(conn: sqlite3.Connection, data_dir: str) -> None:
    conn.executescript(SCHEMA_PATH.read_text())
    # Ensure the "content" column exists in the documents table
    _ensure_column(conn, "documents", "content", "content TEXT NOT NULL DEFAULT ''")
    # Initializing the watched_directories with default data directory
    conn.execute(
        "INSERT OR IGNORE INTO watched_directories (path, is_default, added_at) VALUES (?, 1, ?)",
        (data_dir, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()