#backend/app/algorithms/ranking_factory.py
from enum import Enum
from .base import RankingAlgorithm
from .tfidf import TFIDFRanking
from .bm25 import BM25Ranking

class RankingAlgorithmType(str, Enum):
    TFIDF = "tfidf"
    BM25 = "bm25"

class RankingFactory:
    @staticmethod
    def create(algorithm: RankingAlgorithmType, **kwargs) -> RankingAlgorithm:
        if algorithm == RankingAlgorithmType.TFIDF:
            return TFIDFRanking(**kwargs)
        if algorithm == RankingAlgorithmType.BM25:
            return BM25Ranking(**kwargs)
        raise ValueError(f"Unsupported ranking algorithm: {algorithm}")