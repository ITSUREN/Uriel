#backend/app/storage/sqlite_repository.py
import json
import sqlite3
from datetime import datetime
from .base import DocumentRepository, IndexRepository

from backend.app.models.document import Document
from backend.app.models.posting import Posting

class SQLiteDocumentRepository(DocumentRepository):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, doc: Document) -> None:
        self.conn.execute(
            """INSERT OR REPLACE INTO documents (doc_id, path, title, length, last_modified) VALUES (?, ?, ?, ?, ?)""",
            (doc.doc_id, doc.path, doc.title, doc.length, doc.last_modified.isoformat()),
        )
        self.conn.commit()

    def get(self, doc_id: int) -> Document | None:
        row = self.conn.execute(
            "SELECT doc_id, path, title, length, last_modified FROM documents WHERE doc_id = ?",
            (doc_id,)
        ).fetchone()
        
        return self._row_to_doc(row) if row else None
    
    def all(self) ->  dict[int, Document]:
        rows = self.conn.execute(
            "SELECT doc_id, path, title, length, last_modified FROM documents"
        ).fetchall()
        
        return {row[0]: self._row_to_doc(row) for row in rows}
    
    def exists_by_path(self, path: str) -> bool:
        row = self.conn.execute("SELECT 1 FROM documents where path = ?", (path,)).fetchone()
        return row is not None
    
    def next_id(self) -> int:
        row = self.conn.execute("SELECT COALESCE(MAX(doc_id), -1) FROM documents").fetchone()
        return row[0] + 1
    
    @staticmethod
    def _row_to_doc(row) -> Document:
        return Document(
            doc_id=row[0],
            path=row[1],
            title=row[2],
            length=row[3],
            last_modified=datetime.fromisoformat(row[4])
        )
    
class SQLiteIndexRepository(IndexRepository):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def add_posting(self, term: str, postings: list[Posting]) -> None:
        self.conn.executemany(
            """INSERT OR REPLACE INTO postings (term, doc_id, term_frequency, positions) VALUES (?, ?, ?, ?)""",
            [(term, posting.doc_id, posting.term_frequency, json.dumps(posting.positions)) for posting in postings],
        )
        self.conn.commit()

    def get_postings(self, term: str) -> list[Posting]:
        rows = self.conn.execute(
            "SELECT doc_id, term_frequency, positions from postings WHERE term = ?",
            (term,)
        ).fetchall()
        return [Posting(doc_id=row[0], term_frequency=row[1], positions=json.loads(row[2])) for row in rows]
    
    def vocabulary_size(self) -> int:
        row = self.conn.execute("SELECT COUNT(DISTINCT term) FROM postings").fetchone()
        return row[0]
    
    def clear(self) -> None:
        self.conn.execute("DELETE FROM postings")
        self.conn.execute("DELETE FROM documents")
        self.conn.commit()