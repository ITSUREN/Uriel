import pytest
from backend.app.query_expansion.rocchio import RocchioFeedback, RocchioParams
from backend.app.query_expansion.wordnet_expansion import WordNetExpander
from backend.app.models.posting import Posting
from backend.app.tests.unit.fakes import FakeIndexRepo

pytestmark = pytest.mark.unit


class TestRocchioFeedback:
    def test_relevant_doc_terms_are_added_to_query(self):
        """UT-091"""
        repo = FakeIndexRepo(
            postings_by_term={"cat": [Posting(1, 3, [])], "feline": [Posting(1, 2, [])]},
            doc_terms={1: {"cat": 3, "feline": 2}},
        )
        rocchio = RocchioFeedback(repo, RocchioParams(alpha=1.0, beta=1.0, gamma=0.0))
        new_weights = rocchio.expand({"cat": 1.0}, [1], [], n_docs=10)
        assert "feline" in new_weights
        assert new_weights["cat"] > 1.0

    def test_non_relevant_terms_can_be_suppressed_to_zero_and_dropped(self):
        """UT-092: positive Rocchio — never negative weights"""
        repo = FakeIndexRepo(
            postings_by_term={"noise": [Posting(1, 10, [])]},
            doc_terms={1: {"noise": 10}},
        )
        rocchio = RocchioFeedback(repo, RocchioParams(alpha=1.0, beta=0.0, gamma=5.0))
        new_weights = rocchio.expand({"noise": 0.1}, [], [1], n_docs=10)
        assert "noise" not in new_weights

    def test_no_feedback_docs_just_scales_by_alpha(self):
        """UT-093"""
        rocchio = RocchioFeedback(FakeIndexRepo(), RocchioParams(alpha=2.0, beta=0.75, gamma=0.15))
        assert rocchio.expand({"cat": 1.0}, [], [], n_docs=10) == {"cat": 2.0}


class TestWordNetExpander:
    def test_synonyms_get_lower_weight_than_original_term(self):
        """UT-101"""
        expander = WordNetExpander(max_synonyms_per_term=2, synonym_weight=0.5)
        weights = expander.expand(["happy"], normalize=lambda s: s.lower().split())
        assert weights["happy"] == 1.0
        assert all(w == 0.5 for t, w in weights.items() if t != "happy")

    def test_original_terms_never_downweighted(self):
        """UT-102"""
        expander = WordNetExpander(max_synonyms_per_term=3, synonym_weight=0.5)
        weights = expander.expand(["good", "great"], normalize=lambda s: s.lower().split())
        assert weights["good"] >= 1.0 and weights["great"] >= 1.0