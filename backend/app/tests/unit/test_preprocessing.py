import pytest
from backend.app.preprocessing.config import PreprocessingConfig, PreprocessingEngineType
from backend.app.preprocessing.traditional_engine import TraditionalPreprocessingEngine
from backend.app.tests.conftest import SPACY_MODEL_AVAILABLE

pytestmark = pytest.mark.unit


class TestTraditionalPreprocessingEngine:
    def test_lowercases_and_removes_stopwords(self):
        """UT-031"""
        config = PreprocessingConfig(engine=PreprocessingEngineType.TRADITIONAL,
                                      lowercase=True, remove_stopwords=True, use_lemma=False)
        result = TraditionalPreprocessingEngine(config).process("The Cats are Sleeping")
        assert "the" not in result.terms and "are" not in result.terms

    def test_stemming_collapses_word_variants(self):
        """UT-032"""
        config = PreprocessingConfig(engine=PreprocessingEngineType.TRADITIONAL,
                                      remove_stopwords=False, use_stemming=True, use_lemma=False)
        result = TraditionalPreprocessingEngine(config).process("running runs")
        assert len(set(result.terms)) == 1


@pytest.mark.skipif(not SPACY_MODEL_AVAILABLE, reason="en_core_web_sm not installed")
class TestSpaCyPreprocessingEngine:
    def test_lemmatizes_and_removes_stopwords(self):
        """UT-033: exercises the actual production-default engine, not just traditional"""
        from backend.app.preprocessing.spacy_engine import SpaCyPreprocessingEngine
        result = SpaCyPreprocessingEngine(PreprocessingConfig()).process("The cats are running quickly")
        assert "the" not in result.terms and "are" not in result.terms
        assert "cat" in result.terms  # lemmatized from "cats"

    def test_pos_tags_returned_only_when_requested(self):
        """UT-034"""
        from backend.app.preprocessing.spacy_engine import SpaCyPreprocessingEngine
        config = PreprocessingConfig(keep_pos_tags=True)
        result = SpaCyPreprocessingEngine(config).process("The cat sleeps")
        assert result.pos_tags is not None and len(result.pos_tags) == len(result.terms)