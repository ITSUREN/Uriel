from dataclasses import dataclass

@dataclass
class SearchResult:
    doc_id: int
    score: float
    snippet: str