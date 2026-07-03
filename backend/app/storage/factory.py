#backend/app/storage/factory.py
import sqlite3
from typing import cast
from pathlib import Path
from .init_db import init_db
from .sqlite_repository import SQLiteConfigRepository, SQLiteDirectoryRepository, SQLiteDocumentRepository, SQLiteIndexRepository

def get_connection(db_path: str, data_dir: str) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def build_repositories(db_path: str, data_dir: str) -> tuple[SQLiteDocumentRepository, SQLiteIndexRepository, SQLiteConfigRepository, SQLiteDirectoryRepository]:
    conn = get_connection(db_path, data_dir)
    init_db(conn, data_dir)
    return (
        SQLiteDocumentRepository(conn),
        SQLiteIndexRepository(conn),
        SQLiteConfigRepository(conn),
        SQLiteDirectoryRepository(conn),
    )
