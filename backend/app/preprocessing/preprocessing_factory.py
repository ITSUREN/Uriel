from .traditional_engine import TraditionalPreprocessingEngine
from .spacy_engine import SpaCyPreprocessingEngine
from .config import PreprocessingEngineType


class PreprocessingFactory:
    @staticmethod
    def create(config):
        if config.engine == PreprocessingEngineType.SPACY:
            return SpaCyPreprocessingEngine(config)

        elif config.engine == PreprocessingEngineType.TRADITIONAL:
            return TraditionalPreprocessingEngine(config)

        raise ValueError("Unknown preprocessing engine")