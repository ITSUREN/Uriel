#backend/app/models/search_result.py
from dataclasses import dataclass

@dataclass
class SearchResult:
    doc_id: int
    score: float
    snippet: str