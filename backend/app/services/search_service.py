#backend/app/services/search_service.py
from backend.app.algorithms.ranking_factory import RankingFactory, RankingAlgorithmType
from backend.app.models.search_result import SearchResult

class SearchService:
    def __init__(self, doc_repo, index_repo, preprocessor, ranking_factory = RankingFactory):
        self.doc_repo = doc_repo
        self.index_repo = index_repo
        self.preprocessor = preprocessor
        self.ranking_factory = ranking_factory

    def search(self, query: str, algorithm: RankingAlgorithmType, top_k: int=10) -> list[SearchResult]:
        processed_query = self.preprocessor.process(query)
        query_terms = processed_query.terms
        
        ranker = self.ranking_factory.create(algorithm)
        documents = self.doc_repo.all()
        results = ranker.score(query_terms, self.index_repo, documents, top_k)
        for result in results:
            result.snippet = self._make_snippet(documents[result.doc_id])
        return results
    
    def _make_snippet(self, doc) -> str:
        return doc.title  # placeholder — real snippet needs stored raw text or positions+source lookup