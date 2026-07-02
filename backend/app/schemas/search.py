#backend/app/schemas/search.py
from pydantic import BaseModel
from backend.app.algorithms.ranking_factory import RankingAlgorithmType

class SearchRequest(BaseModel):
    query: str
    algorithm: RankingAlgorithmType = RankingAlgorithmType.BM25
    top_k: int = 10

class SearchResponse(BaseModel):
    doc_id: int
    score: float
    snippet: str
    title: str
    path: str