#backend/app/algorithms/base.py
from abc import ABC, abstractmethod
from backend.app.models.search_result import SearchResult
from backend.app.models.document import Document
from backend.app.index.inverted_index import InvertedIndex

class RankingAlgorithm(ABC):
    """Strategy interface for scoring documents against query terms"""

    @abstractmethod
    def score(self, query_terms: list[str], index: InvertedIndex, documents: dict[int, Document], top_k: int =10 ) -> list[SearchResult]:
        ...