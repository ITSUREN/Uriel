#backend/app/models/document.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Document:
    doc_id: int
    path: str
    title: str
    length: int
    last_modified: datetime