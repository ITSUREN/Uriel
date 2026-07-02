#backend/app/preprocessing/config.py
from dataclasses import dataclass
from enum import Enum


class PreprocessingEngineType(str, Enum):
    SPACY = "spacy"
    TRADITIONAL = "traditional"

@dataclass
class PreprocessingConfig:

    engine: PreprocessingEngineType = PreprocessingEngineType.SPACY

    spacy_model: str = "en_core_web_sm"

    lowercase: bool = True

    remove_stopwords: bool = True

    use_lemma: bool = True

    use_stemming: bool = False

    keep_pos_tags: bool = False

    keep_noun_chunks: bool = False