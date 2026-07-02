#backend/app/storage/factory.py
import sqlite3
from typing import cast
from pathlib import Path
from .init_db import init_db
from .base import DocumentRepository, IndexRepository
from .sqlite_repository import SQLiteDocumentRepository, SQLiteIndexRepository

def get_connection(db_path: str) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    init_db(conn)
    return conn

def build_repositories(db_path: str) -> tuple[DocumentRepository, IndexRepository]:
    conn = get_connection(db_path)
    doc_repo = SQLiteDocumentRepository(conn)
    index_repo = SQLiteIndexRepository(conn)
    # Cast to IndexRepository to satisfy static type checkers when
    # the concrete implementation is not recognized as a subtype.
    return doc_repo, cast(IndexRepository, index_repo)
