#backend/app/schemas/search.py
from pydantic import BaseModel
from backend.app.algorithms.ranking_factory import RankingAlgorithmType

class SearchRequest(BaseModel):
    query: str
    algorithm: RankingAlgorithmType = RankingAlgorithmType.BM25
    top_k: int = 10
    expand_query: bool | None = None  # None = use configured default

class FeedbackRequest(BaseModel):
    query: str
    relevant_doc_ids: list[int]
    non_relevant_doc_ids: list[int] = []
    algorithm: RankingAlgorithmType | None = None
    top_k: int | None = None

class SearchResponse(BaseModel):
    doc_id: int
    score: float
    snippet: str
    title: str
    path: str