#backend/app/services/search_service.py
from backend.app.algorithms.ranking_factory import RankingFactory, RankingAlgorithmType
from backend.app.models.search_result import SearchResult
from backend.query_expansion.rocchio import RocchioFeedback, RocchioParams
from backend.query_expansion.wodnet_expansion import WordNetExpander

class SearchService:
    def __init__(self, doc_repo, index_repo, preprocessor, config_repo, ranking_factory = RankingFactory):
        self.doc_repo = doc_repo
        self.index_repo = index_repo
        self.config_repo = config_repo
        self.preprocessor = preprocessor
        self.ranking_factory = ranking_factory

    def _algorithm_kwargs(self, algorithm, config):
        return config["ranking"]["bm25"] if algorithm == RankingAlgorithmType.BM25 else {}
    
    def _base_query_weights(self, query:str, expand: bool, config) -> dict[str, float]:
        query_terms = self.preprocessor.process(query).terms
        if not expand:
            return {term: query_terms.count(term) *1.0 for term in set(query_terms)}
        
        query_expander = config["query_expansion"]
        expander = WordNetExpander(query_expander["wordnet_max_synonyms_per_term"], query_expander["wordnet_max_synonyms_per_query"])
        return expander.expand(query_terms, normalize = lambda s: self.preprocessor.process(s).terms)

    def search(self, query: str, algorithm = None, top_k = None, expand_query: bool | None = None) -> list[SearchResult]:
        config = self.config_repo.get()
        algorithm = algorithm or RankingAlgorithmType(config["ranking"]["default_algorithm"])
        top_k = top_k or config["ranking"]["default_top_k"]
        expand = config["query_expansion"]["wordne_enabled"] if expand_query is None else expand_query

        query_weights = self._base_query_weights(query, expand, config)        
        ranker = self.ranking_factory.create(algorithm, **self._algorithm_kwargs(algorithm, config))
        documents = self.doc_repo.all()
        results = ranker.score(query_weights, self.index_repo, documents, top_k)
        for result in results:
            result.snippet = self._make_snippet(documents[result.doc_id])
        return results
    
    def search_with_feedback(self, query: str, relevant_doc_ids: list[int], non_relevant_doc_ids: list[int], algorithm = None, top_k = None) -> list[SearchResult]:
        config = self.config_repo.get()
        algorithm = algorithm or RankingAlgorithmType(config["ranking"]["default_algorithm"])
        top_k = top_k or config["ranking"]["default_top_k"]

        query_weights = self._base_query_weights(query, expand = False, config=config)
        # Apply Rocchio feedback to expand the query
        rocchio = RocchioFeedback(self.index_repo, RocchioParams(**config["query_expansion"]["rocchio"]))
        documents = self.doc_repo.all()
        expanded_query_weights = rocchio.expand(query_weights, relevant_doc_ids, non_relevant_doc_ids, len(documents))

        ranker = self.ranking_factory.create(algorithm, **self._algorithm_kwargs(algorithm, config))
        results = ranker.score(expanded_query_weights, self.index_repo, documents, top_k)
        for result in results:
            result.snippet = self._make_snippet(documents[result.doc_id])
        return results
    
    def _make_snippet(self, doc) -> str:
        return doc.title  # placeholder — real snippet needs stored raw text or positions+source lookup