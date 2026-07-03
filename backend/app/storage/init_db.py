#backend/app/storage/init_db.py
import sqlite3
from pathlib import Path
from backend.app.config.settings import get_settings
from datetime import datetime, timezone

SCHEMA_PATH = Path(__file__).parent / "schema.sql"

def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_PATH.read_text())
    settings = get_settings();
    # Initializing the watched_directories with default data directory
    conn.execute(
        "INSERT OR IGNORE INTO watched_directories (path, is_default, added_at) VALUES (?, 1, ?)",
        (settings.data_dir, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()