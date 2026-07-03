#backend/app/algorithms/base.py
from abc import ABC, abstractmethod
from backend.app.models.search_result import SearchResult
from backend.app.models.document import Document
from backend.app.storage.base import IndexRepository

class RankingAlgorithm(ABC):
    """Strategy interface for scoring documents against query terms"""

    @abstractmethod
    def score(self, query_weights: dict[str, float], index_repo: IndexRepository, documents: dict[int, Document], top_k: int =10 ) -> list[SearchResult]:
        ...